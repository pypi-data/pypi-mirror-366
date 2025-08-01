# Copyright (c) 2024-2025, Huawei Technologies Co., Ltd.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0  (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import zlib
from dataclasses import asdict
from typing import List

import numpy as np
import torch
from torch import distributed as dist
from torch.distributed.distributed_c10d import _get_default_group

from msprobe.core.common.const import Const
from msprobe.core.common.exceptions import MsprobeException
from msprobe.core.common.file_utils import path_len_exceeds_limit
from msprobe.core.common.log import logger
from msprobe.core.common.utils import convert_tuple
from msprobe.core.common.decorator import recursion_depth_decorator
from msprobe.core.data_dump.data_processor.base import BaseDataProcessor, ModuleBackwardInputsOutputs, \
    ModuleForwardInputsOutputs, TensorStatInfo
from msprobe.pytorch.common.utils import save_pt
from msprobe.pytorch.free_benchmark import FreeBenchmarkCheck, UnequalRow

is_gpu = False
try:
    import torch_npu
except ImportError:
    is_gpu = True


class PytorchDataProcessor(BaseDataProcessor):
    pytorch_special_type = (
        torch.device,
        torch.dtype,
        torch.Size,
        torch.Tensor,
        torch.memory_format,
        dist.ProcessGroup,
        dist.P2POp,
        dist.ReduceOp
    )
    memory_format = {
        torch.contiguous_format: "contiguous_format",
        torch.channels_last: "channels_last",
        torch.channels_last_3d: "channels_last_3d",
        torch.preserve_format: "preserve_format"
    }

    def __init__(self, config, data_writer):
        super().__init__(config, data_writer)
        self.torch_object_key = {
            "device": self.analyze_device_in_kwargs,
            "dtype": self.analyze_dtype_in_kwargs
        }
        self._async_dump_cache = {}

    @staticmethod
    def get_md5_for_tensor(x):
        if x.dtype == torch.bfloat16:
            x = x.float()
        tensor_bytes = x.cpu().detach().numpy().tobytes()
        crc32_hash = zlib.crc32(tensor_bytes)
        return f"{crc32_hash:08x}"

    @staticmethod
    def analyze_device_in_kwargs(element):
        single_arg = {}
        single_arg.update({'type': "torch.device"})
        if isinstance(element, (int, str)):
            single_arg.update({"value": element})
        elif isinstance(element, torch.device):
            if hasattr(element, "index"):
                device_value = element.type + ":" + str(element.index)
            else:
                device_value = element.type
            single_arg.update({"value": device_value})
        else:
            logger.debug(f"Device type {type(element)} is not supported.")
        return single_arg

    @staticmethod
    def analyze_dtype_in_kwargs(element):
        return {"type": "torch.dtype", "value": str(element)}

    @staticmethod
    def get_stat_info_async(data):
        tensor_stat = TensorStatInfo()
        if torch.is_complex(data):
            logger.warning("Async dump do not support complex data!")
            return tensor_stat
        elif data.dtype == torch.bool:
            tensor_stat.max = torch.any(data)
            tensor_stat.min = torch.all(data)
        elif not data.shape:
            tensor_stat.max = tensor_stat.min = tensor_stat.mean = tensor_stat.norm = data
        else:
            if data.dtype == torch.float64 or not data.is_floating_point():
                data = data.float()
            tensor_stat.max = torch.max(data)
            tensor_stat.min = torch.min(data)
            tensor_stat.mean = torch.mean(data)
            tensor_stat.norm = torch.norm(data)
        return tensor_stat

    @staticmethod
    def get_stat_info_sync(data):
        tensor_stat = TensorStatInfo()
        if torch.is_complex(data):
            data_np = data.cpu().numpy()
            data_abs = np.abs(data_np)
            tensor_stat.max = np.max(data_abs).item()
            tensor_stat.min = np.min(data_abs).item()
            tensor_stat.mean = np.mean(data_abs).item()
        elif data.dtype == torch.bool:
            tensor_stat.max = torch.any(data)
            tensor_stat.min = torch.all(data)
        elif not data.shape:
            tensor_stat.max = tensor_stat.min = tensor_stat.mean = tensor_stat.norm = data
        else:
            if data.dtype == torch.float64 or not data.is_floating_point():
                data = data.float()
            tensor_stat.max = torch.max(data)
            tensor_stat.min = torch.min(data)
            tensor_stat.mean = torch.mean(data)
            tensor_stat.norm = torch.norm(data)
        return tensor_stat

    @staticmethod
    def get_stat_info(data, async_dump=False):
        tensor_stat = TensorStatInfo()
        if data.is_meta:
            return tensor_stat
        data_clone = data.detach()
        if not data_clone.numel() or not data_clone.data_ptr():
            return tensor_stat
        else:
            if data_clone.device.type == Const.CPU_LOWERCASE or not async_dump:
                return PytorchDataProcessor.get_stat_info_sync(data_clone)
            else:
                return PytorchDataProcessor.get_stat_info_async(data_clone)

    @staticmethod
    def handle_tensor_extremum_nan_inf(tensor, operator):
        data_clone = tensor.detach()
        data_nan = torch.isnan(data_clone)
        if int(torch.sum(data_nan)) == data_clone.numel():
            return float('nan')

        finite_mask = torch.isfinite(data_clone)
        if int(torch.sum(finite_mask)) > 0:
            finite_values = data_clone[finite_mask]
            return torch.max(finite_values).item() if operator == 'max' else \
                torch.min(finite_values).item()
        else:
            data_no_nan = data_clone[~data_nan]
            return torch.max(data_no_nan).item() if operator == 'max' else \
                torch.min(data_no_nan).item()

    @staticmethod
    def process_group_hash(arg):
        group_ranks = dist.get_process_group_ranks(arg)
        group_ranks_hash = zlib.crc32(str(group_ranks).encode('utf-8'))
        return f"{group_ranks_hash:08x}"

    @staticmethod
    def is_hookable_element(element):
        return (hasattr(element, "register_hook") and callable(element.register_hook)) and \
            (hasattr(element, "requires_grad") and element.requires_grad)

    @staticmethod
    def _analyze_torch_size(arg):
        return {"type": "torch.Size", "value": [int(x) for x in list(arg)]}

    @staticmethod
    def _analyze_memory_format(arg):
        # 获取内存格式
        format_type = PytorchDataProcessor.memory_format.get(arg)
        return {"type": "torch.memory_format", "format": format_type}

    @staticmethod
    def _analyze_process_group(arg):
        group_info = {"type": "torch.ProcessGroup"}
        try:
            group_ranks = dist.get_process_group_ranks(arg)
            group_info.update({"group_ranks": group_ranks})
            group_id = PytorchDataProcessor.process_group_hash(arg)
            group_info.update({"group_id": group_id})
        except Exception as e:
            logger.warning(f"Failed to get process group ranks info with error info: {e}.")
        return group_info

    @staticmethod
    def _analyze_reduce_op(arg):
        op_type = None
        try:
            op_type = str(arg)
        except Exception as e:
            logger.warning(f"Failed to get value of torch.distributed.ReduceOp with error info: {e}.")
        return {"type": "torch.distributed.ReduceOp", "value": op_type}

    @classmethod
    def get_special_types(cls):
        return super().get_special_types() + cls.pytorch_special_type

    def dump_async_data(self):
        for file_path, tensor in self._async_dump_cache.items():
            save_pt(tensor.contiguous(), file_path)
        self._async_dump_cache.clear()

    def analyze_single_element(self, element, suffix_stack):
        if suffix_stack and suffix_stack[-1] in self.torch_object_key:
            return self.torch_object_key[suffix_stack[-1]](element)

        suffix_str = Const.SEP.join(str(s) for s in suffix_stack)
        type_analyzer = [
            (PytorchDataProcessor.builtin_type, self._analyze_builtin),
            (torch.Size, self._analyze_torch_size),
            (torch.Tensor, lambda e: self._analyze_tensor(e, suffix_str)),
            (torch.memory_format, self._analyze_memory_format),
            (dist.ProcessGroup, self._analyze_process_group),
            (dist.P2POp, lambda e: self._analyze_p2pop(e, suffix_str)),
            (dist.ReduceOp, self._analyze_reduce_op),
            (PytorchDataProcessor.np_type[:-1], self._analyze_numpy),
            (np.ndarray, lambda e: self._analyze_ndarray(e, suffix_str)),
        ]
        for type_key, analyze_fn in type_analyzer:
            if isinstance(element, type_key):
                return analyze_fn(element)
        return {}

    def _analyze_p2pop(self, arg, suffix):
        p2pop_info = {"class_type": "torch.distributed.P2POp"}
        try:
            tensor_info = self._analyze_tensor(arg.tensor, suffix)
            p2pop_info.update({"tensor": tensor_info})
            p2pop_info.update({"op": arg.op.__name__})
            p2pop_info.update({"peer": arg.peer})
            p2pop_info.update({"tag": arg.tag})
            group_id = PytorchDataProcessor.process_group_hash(
                arg.group) if arg.group else PytorchDataProcessor.process_group_hash(_get_default_group())
            p2pop_info.update({"group_id": group_id})
        except Exception as e:
            logger.warning(f"Failed to parse the P2POp content with error info: {e}.")
        return p2pop_info

    def _analyze_tensor(self, tensor, suffix):
        tensor_stat = self.get_stat_info(tensor, self.config.async_dump)
        tensor_json = {}
        tensor_json.update({'type': 'torch.Tensor'})
        tensor_json.update({'dtype': str(tensor.dtype)})
        tensor_json.update({"shape": tensor.shape})

        stat_values = [
            tensor_stat.max,
            tensor_stat.min,
            tensor_stat.mean,
            tensor_stat.norm
        ]
        placeholder_index = self.data_writer.append_stat_to_buffer(stat_values)

        tensor_json.update({Const.TENSOR_STAT_INDEX: placeholder_index})
        tensor_json.update({"requires_grad": tensor.requires_grad})

        if self.config.summary_mode == Const.MD5 and not self.config.async_dump:
            tensor_md5 = self.get_md5_for_tensor(tensor)
            tensor_json.update({Const.MD5: tensor_md5})
        return tensor_json

    def _analyze_and_save_tensor(self, tensor, suffix):
        dump_data_name, file_path = self.get_save_file_path(suffix)
        single_arg = PytorchDataProcessor._analyze_tensor(self, tensor, suffix)
        single_arg.update({"data_name": dump_data_name})
        if self.config.async_dump:
            self._async_dump_cache[file_path] = tensor.clone().detach()
        else:
            saved_tensor = tensor.clone().contiguous().detach()
            save_pt(saved_tensor, file_path)
        return single_arg

    def _analyze_and_save_ndarray(self, ndarray, suffix):
        dump_data_name, file_path = self.get_save_file_path(suffix)
        save_pt(torch.tensor(ndarray), file_path)
        ndarray_json = PytorchDataProcessor._analyze_ndarray(ndarray, suffix)
        ndarray_json.update({"data_name": dump_data_name})
        return ndarray_json


class StatisticsDataProcessor(PytorchDataProcessor):
    def _analyze_tensor(self, tensor, suffix):
        if any(item in self.current_api_or_module_name for item in self.config.tensor_list):
            return self._analyze_and_save_tensor(tensor, suffix)
        else:
            return super()._analyze_tensor(tensor, suffix)

    def _analyze_ndarray(self, ndarray, suffix):
        if any(item in self.current_api_or_module_name for item in self.config.tensor_list):
            return self._analyze_and_save_ndarray(ndarray, suffix)
        else:
            return super()._analyze_ndarray(ndarray, suffix)


class TensorDataProcessor(PytorchDataProcessor):
    def _analyze_tensor(self, tensor, suffix):
        return self._analyze_and_save_tensor(tensor, suffix)

    def _analyze_ndarray(self, ndarray, suffix):
        return self._analyze_and_save_ndarray(ndarray, suffix)


class OverflowCheckDataProcessor(PytorchDataProcessor):
    __slots__ = ["cached_tensors_and_file_paths"]

    def __init__(self, config, data_writer):
        super().__init__(config, data_writer)
        self.has_overflow = False
        self.support_inf_nan = None
        self.cached_api_info = {}
        self.cached_tensors_and_file_paths = {}
        self.bits_for_overflow = 8
        self.real_overflow_nums = 0
        self.overflow_nums = config.overflow_nums

    @property
    def is_terminated(self):
        if self.overflow_nums == -1:
            return False
        if self.real_overflow_nums >= self.overflow_nums:
            return True
        return False

    def analyze_forward_input(self, name, module, module_input_output: ModuleForwardInputsOutputs):
        self.has_overflow = False
        self._is_support_inf_nan()
        self.cached_api_info = super().analyze_forward_input(name, module, module_input_output)
        return None

    def analyze_forward_output(self, name, module, module_input_output: ModuleForwardInputsOutputs):
        self._is_support_inf_nan()
        api_info_struct = super().analyze_forward_output(name, module, module_input_output)
        if name in self.cached_api_info and name in api_info_struct:
            self.cached_api_info[name].update(api_info_struct[name])
        elif name in api_info_struct:
            self.cached_api_info = api_info_struct
        self.handle_overflow()
        return self.cached_api_info if self.has_overflow else None

    def analyze_forward(self, name, module, module_input_output: ModuleForwardInputsOutputs):
        self.has_overflow = False
        self._is_support_inf_nan()
        api_info_struct = super().analyze_forward(name, module, module_input_output)
        self.handle_overflow()
        return api_info_struct if self.has_overflow else None

    def analyze_backward(self, name, module, module_input_output: ModuleBackwardInputsOutputs):
        self.has_overflow = False
        self._is_support_inf_nan()
        api_info_struct = super().analyze_backward(name, module, module_input_output)
        self.handle_overflow()
        return api_info_struct if self.has_overflow else None

    def analyze_params(self, name, param_name, grad):
        self.has_overflow = False
        self._is_support_inf_nan()
        api_info_struct = super().analyze_params(name, param_name, grad)
        self.handle_overflow()
        return api_info_struct if self.has_overflow else None

    def handle_overflow(self):
        if not self.support_inf_nan:
            self._analyze_maybe_overflow_flag()
        if self.has_overflow:
            for file_path, tensor in self.cached_tensors_and_file_paths.items():
                save_pt(tensor.clone().contiguous().detach(), file_path)
            self.real_overflow_nums += 1
            if self.overflow_nums != -1 and self.real_overflow_nums >= self.overflow_nums:
                logger.info(f"[{Const.TOOL_NAME}] Reached the preset overflow times, "
                            f"current overflow times: {self.real_overflow_nums}.")
        self.cached_tensors_and_file_paths = {}

    def _is_support_inf_nan(self):
        if self.support_inf_nan is not None:
            return
        try:
            self.support_inf_nan = is_gpu or torch_npu.npu.utils.is_support_inf_nan()
        except Exception:
            logger.warning(f"Unable to determine if the current device supports inf/nan mode, default not supported.")
            self.support_inf_nan = False

    def _analyze_maybe_overflow_flag(self):
        try:
            self.has_overflow = torch_npu.npu.utils.get_npu_overflow_flag()
            if self.has_overflow:
                torch_npu.npu.utils.clear_npu_overflow_flag()
        except Exception as e:
            logger.error(f"Overflow check failed, the current environment may be abnormal.")
            raise RuntimeError(f"overflow check failed") from e

    def _analyze_maybe_overflow_tensor(self, tensor_json):
        tensor_stat_index = tensor_json.get(Const.TENSOR_STAT_INDEX)
        if tensor_stat_index is None:
            logger.warning("tensor_stat_index does not exist in tensor_json.")
            return
        max_tensor = self.data_writer.get_buffer_values_max(tensor_stat_index)
        min_tensor = self.data_writer.get_buffer_values_min(tensor_stat_index)

        if max_tensor is None or min_tensor is None:
            return

        if torch.isinf(max_tensor) or torch.isnan(max_tensor):
            self.has_overflow = True
            return

        if torch.isinf(min_tensor) or torch.isnan(min_tensor):
            self.has_overflow = True

    def _analyze_tensor(self, tensor, suffix):
        dump_data_name, file_path = self.get_save_file_path(suffix)
        if not path_len_exceeds_limit(file_path):
            self.cached_tensors_and_file_paths.update({file_path: tensor})
        else:
            logger.warning(f'The file path {file_path} length exceeds limit.')
        single_arg = super()._analyze_tensor(tensor, suffix)
        single_arg.update({"data_name": dump_data_name})
        if not self.has_overflow and self.support_inf_nan:
            self._analyze_maybe_overflow_tensor(single_arg)
        return single_arg


class FreeBenchmarkDataProcessor(PytorchDataProcessor):

    def __init__(self, config, data_writer):
        super().__init__(config, data_writer)
        self.checker = FreeBenchmarkCheck(config=config)
        self._return_forward_new_output = None
        self._forward_new_output = None

    def update_iter(self, current_iter):
        super().update_iter(current_iter)
        self.checker.update_iter(current_iter)

    def update_unequal_rows(self, unequal_rows: List[UnequalRow]):
        if not unequal_rows:
            return
        for row in unequal_rows:
            data_dict = asdict(row)
            self.data_writer.write_data_to_csv(
                data_dict.values(),
                data_dict.keys(),
                self.data_writer.free_benchmark_file_path
            )
        return

    def analyze_forward_input(self, name, module, module_input_output: ModuleForwardInputsOutputs):
        self.checker.pre_forward(name, module, self, module_input_output.args, module_input_output.kwargs)

    def analyze_forward_output(self, name, module, module_input_output: ModuleForwardInputsOutputs):
        new_output, unequal_rows = self.checker.forward(
            name,
            module,
            module_input_output.args,
            module_input_output.kwargs,
            module_input_output.output,
        )
        self.update_unequal_rows(unequal_rows)
        if self.checker.if_fix():
            self._return_forward_new_output = True
            self._forward_new_output = new_output

    def analyze_backward(self, name, module, module_input_output: ModuleBackwardInputsOutputs):
        self.checker.backward(name, module, module_input_output.grad_input)


class KernelDumpDataProcessor(PytorchDataProcessor):
    def __init__(self, config, data_writer):
        super().__init__(config, data_writer)
        self.enable_kernel_dump = True
        self.is_found_output_tensor = False
        self.is_found_grad_input_tensor = False
        self.forward_args = None
        self.forward_kwargs = None
        self.forward_output_tensor = None
        self.grad_input_tensor = None

    @staticmethod
    def start_kernel_dump(config_path):
        torch_npu.npu.synchronize()
        torch_npu.npu.init_dump()
        torch_npu.npu.set_dump(config_path)
        torch_npu.npu.synchronize()

    @staticmethod
    def stop_kernel_dump():
        torch_npu.npu.synchronize()
        torch_npu.npu.finalize_dump()
        torch_npu.npu.synchronize()

    @staticmethod
    def _print_unsupported_log(api_name):
        logger.warning(f"The kernel dump does not support the {api_name} API.")

    def analyze_forward_input(self, name, module, module_input_output):
        if not self.enable_kernel_dump:
            return
        if is_gpu:
            logger.warning("The current environment is not a complete NPU environment, and kernel dump cannot be used.")
            self.enable_kernel_dump = False
            return

        if self.config.is_backward_kernel_dump:
            try:
                self.forward_args = self.clone_and_detach_tensor(module_input_output.args)
                self.forward_kwargs = self.clone_and_detach_tensor(module_input_output.kwargs)
                output = module.forward(*self.forward_args, **self.forward_kwargs)
            except Exception as e:
                if isinstance(e, MsprobeException):
                    logger.warning(str(e))
                self._print_unsupported_log(name)
                self.enable_kernel_dump = False
                return

            self.analyze_element(convert_tuple(output))
            if not self.is_found_output_tensor:
                self._print_unsupported_log(name)
                self.enable_kernel_dump = False
            return
        self.start_kernel_dump(self.config.kernel_config_path)

    def analyze_forward_output(self, name, module, module_input_output):
        if not self.enable_kernel_dump:
            return
        if self.config.is_backward_kernel_dump:
            return
        self.enable_kernel_dump = False
        self.stop_kernel_dump()
        logger.info(f"The kernel data of {name} is dumped successfully.")

    def analyze_backward(self, name, module, module_input_output):
        if not self.enable_kernel_dump:
            return
        self.enable_kernel_dump = False

        self.analyze_element(module_input_output.grad_input)
        if not self.is_found_grad_input_tensor:
            self._print_unsupported_log(name)
            return
        self.start_kernel_dump(self.config.kernel_config_path)

        try:
            self.forward_output_tensor.backward(self.grad_input_tensor, retain_graph=True)
        except Exception:
            self._print_unsupported_log(name)
            self.stop_kernel_dump()
            return

        self.stop_kernel_dump()
        logger.info(f"The kernel data of {name} is dumped successfully.")

    @recursion_depth_decorator(
        "KernelDump: KernelDumpDataProcessor.clone_and_detach_tensor",
        max_depth=Const.DUMP_MAX_DEPTH
    )
    def clone_and_detach_tensor(self, input_params):
        if isinstance(input_params, torch.Tensor):
            if input_params.requires_grad:
                return input_params.clone().detach().requires_grad_()
            return input_params.clone()
        elif isinstance(input_params, tuple):
            return tuple(self.clone_and_detach_tensor(x) for x in input_params)
        elif isinstance(input_params, list):
            return list(self.clone_and_detach_tensor(x) for x in input_params)
        elif isinstance(input_params, dict):
            return {k: self.clone_and_detach_tensor(v) for k, v in input_params.items()}
        else:
            return input_params

    def analyze_single_element(self, element, suffix_stack):
        if isinstance(element, torch.Tensor):
            if not self.is_found_output_tensor:
                if element.requires_grad:
                    self.forward_output_tensor = element
                    self.is_found_output_tensor = True
                return {}
            if not self.is_found_grad_input_tensor:
                self.grad_input_tensor = element.clone()
                self.is_found_grad_input_tensor = True
        return {}

    def reset_status(self):
        self.enable_kernel_dump = True
        self.is_found_output_tensor = False
        self.is_found_grad_input_tensor = False
        self.forward_args = None
        self.forward_kwargs = None
        self.forward_output_tensor = None
        self.grad_input_tensor = None
