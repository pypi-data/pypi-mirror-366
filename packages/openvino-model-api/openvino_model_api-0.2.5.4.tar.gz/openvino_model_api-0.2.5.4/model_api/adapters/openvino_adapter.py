"""
 Copyright (c) 2021-2024 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import logging as log
from pathlib import Path
from typing import Dict, Set, Tuple

try:
    import openvino.runtime as ov
    from openvino import (
        AsyncInferQueue,
        Core,
        Dimension,
        PartialShape,
        Type,
        get_version,
        layout_helpers,
    )
    from openvino.preprocess import ColorFormat, PrePostProcessor

    openvino_absent = False
except ImportError:
    openvino_absent = True

from .inference_adapter import InferenceAdapter, Metadata
from .utils import (
    Layout,
    crop_resize,
    get_rt_info_from_dict,
    load_parameters_from_onnx,
    resize_image,
    resize_image_letterbox,
    resize_image_with_aspect,
)


def create_core():
    if openvino_absent:
        raise ImportError("The OpenVINO package is not installed")

    log.info("OpenVINO Runtime")
    log.info("\tbuild: {}".format(get_version()))
    return Core()


def parse_devices(device_string):
    colon_position = device_string.find(":")
    if colon_position != -1:
        device_type = device_string[:colon_position]
        if device_type == "HETERO" or device_type == "MULTI":
            comma_separated_devices = device_string[colon_position + 1 :]
            devices = comma_separated_devices.split(",")
            for device in devices:
                parenthesis_position = device.find(":")
                if parenthesis_position != -1:
                    device = device[:parenthesis_position]
            return devices
    return (device_string,)


def parse_value_per_device(devices: Set[str], values_string: str) -> Dict[str, int]:
    """Format: <device1>:<value1>,<device2>:<value2> or just <value>"""
    values_string_upper = values_string.upper()
    result = {}
    device_value_strings = values_string_upper.split(",")
    for device_value_string in device_value_strings:
        device_value_list = device_value_string.split(":")
        if len(device_value_list) == 2:
            if device_value_list[0] in devices:
                result[device_value_list[0]] = int(device_value_list[1])
        elif len(device_value_list) == 1 and device_value_list[0] != "":
            for device in devices:
                result[device] = int(device_value_list[0])
        elif device_value_list[0] != "":
            raise RuntimeError(f"Unknown string format: {values_string}")
    return result


def get_user_config(
    flags_d: str, flags_nstreams: str, flags_nthreads: int
) -> Dict[str, str]:
    config = {}

    devices = set(parse_devices(flags_d))

    device_nstreams = parse_value_per_device(devices, flags_nstreams)
    for device in devices:
        if device == "CPU":  # CPU supports a few special performance-oriented keys
            # limit threading for CPU portion of inference
            if flags_nthreads:
                config["INFERENCE_NUM_THREADS"] = str(flags_nthreads)

            # for CPU execution, more throughput-oriented execution via streams
            config["NUM_STREAMS"] = (
                str(device_nstreams[device])
                if device in device_nstreams
                else "NUM_STREAMS_AUTO"
            )
        elif device == "GPU":
            config["NUM_STREAMS"] = (
                str(device_nstreams[device])
                if device in device_nstreams
                else "NUM_STREAMS_AUTO"
            )
            if "MULTI" in flags_d and "CPU" in devices:
                # multi-device execution with the CPU + GPU performs best with GPU throttling hint,
                # which releases another CPU thread (that is otherwise used by the GPU driver for active polling)
                config["GPU_PLUGIN_THROTTLE"] = "1"
    return config


class OpenvinoAdapter(InferenceAdapter):
    """
    Works with OpenVINO model
    """

    def __init__(
        self,
        core,
        model,
        weights_path="",
        model_parameters={},
        device="CPU",
        plugin_config=None,
        max_num_requests=0,
        precision="FP16",
        download_dir=None,
        cache_dir=None,
    ):
        """
        precision, download_dir and cache_dir are ignored if model is a path to a file
        """
        self.core = core
        self.model_path = model
        self.device = device
        self.plugin_config = plugin_config
        self.max_num_requests = max_num_requests
        self.model_parameters = model_parameters
        self.model_parameters["input_layouts"] = Layout.parse_layouts(
            self.model_parameters.get("input_layouts", None)
        )
        self.is_onnx_file = False
        self.onnx_metadata = {}

        if isinstance(self.model_path, (str, Path)):
            if Path(self.model_path).suffix == ".onnx" and weights_path:
                log.warning(
                    'For model in ONNX format should set only "model_path" parameter.'
                    'The "weights_path" will be omitted'
                )
            if Path(self.model_path).suffix == ".onnx" and not weights_path:
                import onnx

                self.is_onnx_file = True
                self.onnx_metadata = load_parameters_from_onnx(
                    onnx.load(self.model_path)
                )

        self.model_from_buffer = isinstance(self.model_path, bytes) and isinstance(
            weights_path, bytes
        )
        model_from_file = not self.model_from_buffer and Path(self.model_path).is_file()
        if model_from_file or self.model_from_buffer:
            log.info(
                "Reading model {}".format(
                    "from buffer" if self.model_from_buffer else self.model_path
                )
            )
            self.model = core.read_model(self.model_path, weights_path)
            return
        if isinstance(model, str):
            from omz_tools.models import OMZModel, list_models

            if model in list_models():
                omz_model = OMZModel.download(
                    model,
                    precision=precision,
                    download_dir=download_dir,
                    cache_dir=cache_dir,
                )
                self.model_path = omz_model.model_path
                log.info(f"Reading model {self.model_path}")
                self.model = core.read_model(self.model_path)
                return
        raise RuntimeError("Model must be bytes, a file or existing OMZ model name")

    def load_model(self):
        self.compiled_model = self.core.compile_model(
            self.model, self.device, self.plugin_config
        )
        self.async_queue = AsyncInferQueue(self.compiled_model, self.max_num_requests)
        if self.max_num_requests == 0:
            # +1 to use it as a buffer of the pipeline
            self.async_queue = AsyncInferQueue(
                self.compiled_model, len(self.async_queue) + 1
            )

        log.info(
            "The model {} is loaded to {}".format(
                "from buffer" if self.model_from_buffer else self.model_path,
                self.device,
            )
        )
        self.log_runtime_settings()

    def log_runtime_settings(self):
        devices = set(parse_devices(self.device))
        if "AUTO" not in devices:
            for device in devices:
                try:
                    nstreams = self.compiled_model.get_property(
                        device + "_THROUGHPUT_STREAMS"
                    )
                    log.info("\tDevice: {}".format(device))
                    log.info("\t\tNumber of streams: {}".format(nstreams))
                    if device == "CPU":
                        nthreads = self.compiled_model.get_property("CPU_THREADS_NUM")
                        log.info(
                            "\t\tNumber of threads: {}".format(
                                nthreads if int(nthreads) else "AUTO"
                            )
                        )
                except RuntimeError:
                    pass
        log.info("\tNumber of model infer requests: {}".format(len(self.async_queue)))

    def get_input_layers(self):
        inputs = {}
        for input in self.model.inputs:
            input_shape = get_input_shape(input)
            input_layout = self.get_layout_for_input(input, input_shape)
            inputs[input.get_any_name()] = Metadata(
                input.get_names(),
                input_shape,
                input_layout,
                input.get_element_type().get_type_name(),
            )
        inputs = self._get_meta_from_ngraph(inputs)
        return inputs

    def get_layout_for_input(self, input, shape=None) -> str:
        input_layout = ""
        if self.model_parameters["input_layouts"]:
            input_layout = Layout.from_user_layouts(
                input.get_names(), self.model_parameters["input_layouts"]
            )
        if not input_layout:
            if not layout_helpers.get_layout(input).empty:
                input_layout = Layout.from_openvino(input)
            else:
                input_layout = Layout.from_shape(
                    shape if shape is not None else input.shape
                )
        return input_layout

    def get_output_layers(self):
        outputs = {}
        for i, output in enumerate(self.model.outputs):
            output_shape = (
                output.partial_shape.get_min_shape()
                if self.model.is_dynamic()
                else output.shape
            )

            output_name = output.get_any_name() if output.get_names() else output
            outputs[output_name] = Metadata(
                output.get_names(),
                list(output_shape),
                precision=output.get_element_type().get_type_name(),
            )
        outputs = self._get_meta_from_ngraph(outputs)
        return outputs

    def reshape_model(self, new_shape):
        new_shape = {
            name: PartialShape(
                [
                    (
                        Dimension(dim)
                        if not isinstance(dim, tuple)
                        else Dimension(dim[0], dim[1])
                    )
                    for dim in shape
                ]
            )
            for name, shape in new_shape.items()
        }
        self.model.reshape(new_shape)

    def get_raw_result(self, request):
        return {key: request.get_tensor(key).data for key in self.get_output_layers()}

    def copy_raw_result(self, request):
        return {
            key: request.get_tensor(key).data.copy() for key in self.get_output_layers()
        }

    def infer_sync(self, dict_data):
        self.infer_request = self.async_queue[self.async_queue.get_idle_request_id()]
        self.infer_request.infer(dict_data)
        return self.get_raw_result(self.infer_request)

    def infer_async(self, dict_data, callback_data) -> None:
        self.async_queue.start_async(dict_data, callback_data)

    def set_callback(self, callback_fn):
        self.async_queue.set_callback(callback_fn)

    def is_ready(self) -> bool:
        return self.async_queue.is_ready()

    def await_all(self) -> None:
        self.async_queue.wait_all()

    def await_any(self) -> None:
        self.async_queue.get_idle_request_id()

    def _get_meta_from_ngraph(self, layers_info):
        for node in self.model.get_ordered_ops():
            layer_name = node.get_friendly_name()
            if layer_name not in layers_info.keys():
                continue
            layers_info[layer_name].meta = node.get_attributes()
            layers_info[layer_name].type = node.get_type_name()
        return layers_info

    def operations_by_type(self, operation_type):
        layers_info = {}
        for node in self.model.get_ordered_ops():
            if node.get_type_name() == operation_type:
                layer_name = node.get_friendly_name()
                layers_info[layer_name] = Metadata(
                    type=node.get_type_name(), meta=node.get_attributes()
                )
        return layers_info

    def get_rt_info(self, path):
        if self.is_onnx_file:
            return get_rt_info_from_dict(self.onnx_metadata, path)
        return self.model.get_rt_info(path)

    def embed_preprocessing(
        self,
        layout,
        resize_mode: str,
        interpolation_mode,
        target_shape: Tuple[int],
        pad_value,
        dtype: type = int,
        brg2rgb=False,
        mean=None,
        scale=None,
        input_idx=0,
    ):
        ppp = PrePostProcessor(self.model)

        # Change the input type to the 8-bit image
        if dtype == int:
            ppp.input(input_idx).tensor().set_element_type(Type.u8)
        elif dtype == float:
            ppp.input(input_idx).tensor().set_element_type(Type.f32)

        ppp.input(input_idx).tensor().set_layout(ov.Layout("NHWC")).set_color_format(
            ColorFormat.BGR
        )

        INTERPOLATION_MODE_MAP = {
            "LINEAR": "linear",
            "CUBIC": "cubic",
            "NEAREST": "nearest",
        }

        RESIZE_MODE_MAP = {
            "crop": crop_resize,
            "standard": resize_image,
            "fit_to_window": resize_image_with_aspect,
            "fit_to_window_letterbox": resize_image_letterbox,
        }

        # Handle resize
        # Change to dynamic shape to handle various image size
        # TODO: check the number of input channels and rank of input shape
        if resize_mode and target_shape:
            if resize_mode in RESIZE_MODE_MAP:
                input_shape = [1, -1, -1, 3]
                ppp.input(input_idx).tensor().set_shape(input_shape)
                ppp.input(input_idx).preprocess().custom(
                    RESIZE_MODE_MAP[resize_mode](
                        target_shape,
                        INTERPOLATION_MODE_MAP[interpolation_mode],
                        pad_value,
                    )
                )

            else:
                raise ValueError(
                    f"Upsupported resize type in model preprocessing: {resize_mode}"
                )

        # Handle layout
        ppp.input(input_idx).model().set_layout(ov.Layout(layout))

        # Handle color format
        if brg2rgb:
            ppp.input(input_idx).preprocess().convert_color(ColorFormat.RGB)

        ppp.input(input_idx).preprocess().convert_element_type(Type.f32)

        if mean:
            ppp.input(input_idx).preprocess().mean(mean)
        if scale:
            ppp.input(input_idx).preprocess().scale(scale)

        self.model = ppp.build()
        self.load_model()

    def get_model(self):
        """Returns the openvino.Model object

        Returns:
            openvino.Model object
        """
        return self.model


def get_input_shape(input_tensor):
    def string_to_tuple(string, casting_type=int):
        processed = string.replace(" ", "").replace("(", "").replace(")", "").split(",")
        processed = filter(lambda x: x, processed)
        return tuple(map(casting_type, processed)) if casting_type else tuple(processed)

    if not input_tensor.partial_shape.is_dynamic:
        return list(input_tensor.shape)
    ps = str(input_tensor.partial_shape)
    if ps[0] == "[" and ps[-1] == "]":
        ps = ps[1:-1]
    preprocessed = ps.replace("{", "(").replace("}", ")").replace("?", "-1")
    preprocessed = preprocessed.replace("(", "").replace(")", "")
    if ".." in preprocessed:
        shape_list = []
        for dim in preprocessed.split(","):
            if ".." in dim:
                shape_list.append(string_to_tuple(dim.replace("..", ",")))
            else:
                shape_list.append(int(dim))
        return shape_list
    return string_to_tuple(preprocessed)
