from importlib.metadata import metadata, PackageNotFoundError
from typing import Optional

import imfusion as imf
from imfusion.machinelearning import ExecutionProvider, Engine, DataItem, ElementType, ImageElement
from imfusion.machinelearning.engines import LazyModule

try:
    metadata("coremltools")
except PackageNotFoundError as e:
    imf.log_debug(f"Could not register 'pycoreml' engine: {str(e)}")
    raise

ct = LazyModule("coremltools")  # This delays the import of coreml until it is needed


class CoreMLEngine(Engine, factory_name="pycoreml"):
    """
    Python inference engine based on coremltools.
    """

    def __init__(self, properties: imf.Properties):
        # Instantiates the base class, we can't use super() here because
        # pybind11 doesn't support this for bound types.
        Engine.__init__(self, "pycoreml")
        # Call base class `ìnit` method, this is required as it connects the signals
        # relative to changes of  `self.model_file` and `self.force_cpu`.
        Engine.init(self, properties)
        self.model = self._load_model(self.model_file)

    def on_model_file_changed(self) -> None:
        """
        Callback to handle changes of self.model_file. This can happen either
        in the sdk i.e. with ``engine.model_file = "another_model.mlpackage"`` or
        in the ImFusionSuite when a new yaml model configuration is given to the
        MachineLearningModelController.
        """
        self.model = self._load_model(self.model_file)

    def predict(self, input_item: DataItem) -> DataItem:
        """
        Return predictions for the model.
        """
        # checks that the input item contains the field specified in
        # the MachineLearningModel yaml config under ``EngineInputFields``.
        Engine.check_input_fields(self, input_item)
        reference_input_img: imf.SharedImageSet = None

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

            # make channels first
            input_ = input_sis.numpy().transpose(0, -1, 1, 2, 3)

            output = self.model.predict({"input": input_})
        else:
            raise NotImplementedError("Multiple inputs not implemented for pycoreml.")

        out_item = self.__coreml_dict_to_data_item(
            output, reference_image=reference_input_img
        )
        # checks that the output contains the field specified in
        # the MachineLearningModel yaml config under ``EngineOutputFields``.
        Engine.check_output_fields(self, out_item)
        return out_item

    @staticmethod
    def _load_model(traced_model_file: str):
        """
        Loads an ML Model saved in traced format
        """
        if not traced_model_file.endswith("mlpackage"):
            raise ValueError(
                f"pycoreml expects a .mlpackage model, got {traced_model_file}"
            )

        coreml_model = ct.models.MLModel(traced_model_file)

        return coreml_model

    def __coreml_dict_to_data_item(
        self, coreml_dict: dict, reference_image: imf.SharedImageSet = None
    ) -> DataItem:
        """
        Converts the model output dictionary to a DataItem
        """
        output = DataItem()

        for out_field, out_array in zip(self.output_fields, coreml_dict.values()):
            out_sis = imf.SharedImageSet(out_array.transpose(0, 2, 3, 4, 1))

            if reference_image is not None:
                for n in range(len(out_sis)):
                    out_sis[n].spacing = reference_image[n].spacing
                    out_sis[n].world_to_image_matrix = reference_image[
                        n
                    ].world_to_image_matrix

            output[out_field] = ImageElement(out_sis.clone())
        return output

    def available_providers(self) -> list[ExecutionProvider]:
        providers = [ExecutionProvider.MPS]
        return providers

    def provider(self) -> Optional[ExecutionProvider]:
        return ExecutionProvider.MPS
