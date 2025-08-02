from importlib.metadata import metadata, PackageNotFoundError
import os
from typing import Dict, Union

import imfusion as imf
from imfusion.machinelearning import Engine, DataItem, ElementType, ImageElement
from imfusion.machinelearning.engines import LazyModule
import numpy as np

# Check if openvino is available
try:
    metadata("openvino")
except PackageNotFoundError as e:
    imf.log_debug(f"Could not register 'pyopenvino' engine: {str(e)}")
    raise

ort = LazyModule("openvino.runtime")  # This delays import openvino until it is needed

class OpenVinoEngine(Engine, factory_name="pyopenvino"):
    """
    Python inference engine based on Openvino
    """

    def __init__(self, properties: imf.Properties):
        # Instantiates the base class, we can't use super() here because
        # pybind11 doesn't support this for bound types.
        Engine.__init__(self, "pyopenvino")
        # Call base class `ìnit` method, this is required as it connects the signals
        # relative to changes of  `self.model_file` and `self.force_cpu`.
        Engine.init(self, properties)
        # load the openvino model, self.model_file is initialized in `Engine.init`
        self.model = self._load_model(self.model_file)

    def on_model_file_changed(self) -> None:
        """
        Callback to handle changes of self.model_file. This can happen either
        in the sdk i.e. with ``ov_engine.model_file = "another_model.onnx"`` or
        in the ImFusionSuite when a new yaml model configuration is given to the
        MachineLearningModelController.
        """
        self.model = self._load_model(self.model_file)

    def predict(self, input_item: DataItem) -> DataItem:
        """
        Implements the ``Engine::predict`` pure virtual function.
        """

        # checks that the input item contains the field specified in
        # the MachineLearningModel yaml config under ``EngineInputFields``.
        Engine.check_input_fields(self, input_item)
        reference_input_img: imf.SharedImageSet = None
        input_dict: Union[Dict[str, ort.Tensor], None] = None

        # In case we have a single image as input, we use the image
        # as reference for setting the metadata in the output
        if len(input_item.fields) == 1:
            input_element = input_item[self.input_fields[0]]
            if input_element.type != ElementType.IMAGE:
                raise ValueError(
                    f"Single input element only support images, got type {input_element.type}"
                )

            input_sis = input_element.sis
            reference_input_img = input_sis
            input_ = self.__sis_to_ov_tensor(input_sis)
            output = self.model(input_)
        else:
            # if we have multiple input, we check whether we have a reference
            # image component in the input data item.
            ref_image_comp = input_item.components.reference_image
            if input_item.components.reference_image is not None:
                reference_input_img = ref_image_comp.reference

            for key in self.input_fields:
                if key not in input_item:
                    raise ValueError(f'Key "{key}" not input_item, got {list(input_item.keys())}')
                if input_item[key].type not in (supported_element_types := (ElementType.IMAGE, ElementType.VECTOR)):
                    raise ValueError(f"Got unsupported element type {input_item[key].type}, {supported_element_types=}")
                input_dict[key] = self.__sis_to_ov_tensor(input_item[key].sis)
            output = self.model(input_dict).to_dict()

        out_item = self.__ov_dict_to_data_item(
            output, reference_image=reference_input_img
        )
        # checks that the output contains the field specified in
        # the MachineLearningModel yaml config under ``EngineOutputFields``.
        Engine.check_output_fields(self, out_item)
        return out_item

    @staticmethod
    def _load_model(onnx_model_file: str):
        """
        Loads an ML Model saved in onnx format and compiles it to openvino
        """

        if not onnx_model_file.endswith("onnx"):
            raise ValueError(f"Openvino expects an onnx model, got {onnx_model_file}")

        core = ort.Core()
        num_cores = os.cpu_count()
        model_onnx = core.read_model(model=onnx_model_file)
        model = core.compile_model(
            model=model_onnx,
            device_name="AUTO",
            config={"PERFORMANCE_HINT": "LATENCY", "INFERENCE_NUM_THREADS": num_cores},
        )
        return model

    @staticmethod
    def __sis_to_ov_tensor(sis: imf.SharedImageSet) -> "openvino.runtime.Tensor":
        """
        Converts imf.SharedImageSet to an openvino.Tensor
        """

        np_repr = np.array(sis, copy=False)
        permuted_dimensions = list(range(len(np_repr.shape)))
        permuted_dimensions.insert(1, permuted_dimensions.pop(-1))
        np_repr = np.transpose(np_repr, permuted_dimensions)
        return ort.Tensor(np_repr, shared_memory=False)

    def __ov_dict_to_data_item(
        self,
        ov_dict: Dict["openvino.runtime.ConstOutput", np.ndarray],
        reference_image: imf.SharedImageSet = None,
    ) -> DataItem:
        """
        Converts the openvino model output dictionary to a DataItem
        """
        output = DataItem()
        for out_field, out_array in zip(self.output_fields, ov_dict.values()):
            permuted_dimensions = list(range(len(out_array.shape)))
            permuted_dimensions.append(permuted_dimensions.pop(1))
            out_sis = imf.SharedImageSet(np.transpose(out_array, permuted_dimensions))
            if reference_image is not None:
                for n in range(len(out_sis)):
                    out_sis[n].spacing = reference_image[n].spacing
                    out_sis[n].world_to_image_matrix = reference_image[
                        n
                    ].world_to_image_matrix

            output[out_field] = ImageElement(out_sis)
        return output
