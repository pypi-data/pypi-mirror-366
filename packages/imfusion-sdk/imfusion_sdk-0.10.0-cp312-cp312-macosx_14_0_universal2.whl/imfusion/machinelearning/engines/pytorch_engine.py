from __future__ import annotations
from importlib.metadata import metadata, PackageNotFoundError
from typing import Optional, Union

import imfusion as imf
from imfusion.machinelearning import ExecutionProvider, Engine, DataItem, ElementType, ImageElement
from imfusion.machinelearning.engines import LazyModule

# We cannot import torch when the TorchPlugin is loaded, due to conflicts
for plugin in imf.info().plugins:
    if plugin.name.lower() == "torchplugin":
        message = f"Could not register 'pytorch' engine: {plugin.name} is already loaded which prevents the import of 'torch'."
        imf.log_debug(message)
        raise ImportError(message)

# Check if pytorch is available
try:
    metadata("torch")
except PackageNotFoundError as e:
    imf.log_debug(f"Could not register 'pytorch' engine: {str(e)}")
    raise

torch = LazyModule("torch")  # This will delay loading torch until it is needed

class PyTorchEngine(Engine, factory_name=["pytorch", "torch"]):
    """
    Python inference engine based on PyTorch
    """

    def __init__(self, properties: imf.Properties):
        # Instantiates the base class, we can't use super() here because
        # pybind11 doesn't support this for bound types.
        Engine.__init__(self, "pytorch")
        # Call base class `ìnit` method, this is required as it connects the signals
        # relative to changes of  `self.model_file` and `self.force_cpu`.
        Engine.init(self, properties)
        # load the pytorch model, self.model_file is initialized in `Engine.init`
        self.model = self._load_model(self.model_file)

    def on_model_file_changed(self) -> None:
        """
        Callback to handle changes of self.model_file. This can happen either
        in the sdk i.e. with ``engine.model_file = "another_model.pt"`` or
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

        # In case we have a single image as input, we use the image
        # as reference for setting the metadata in the output
        if len(input_item.fields) == 1:
            input_element = input_item[self.input_fields[0]]
            if input_element.type != ElementType.IMAGE:
                raise ValueError(f"Single input element only support images, got type {input_element.type}")

            input_sis = input_element.sis
            reference_input_img = input_sis
            input_ = self.__sis_to_torch_tensor(input_sis)

            # Move model and tensor to the GPU
            if self.should_run_on_cuda():
                input_ = input_.to("cuda")
                self.model = self.model.to("cuda")

            # Move input to same precision as the model
            model_dtype = next(self.model.parameters()).dtype
            input_ = input_.to(dtype=model_dtype)

            output = self.model(input_)
        else:
            # if we have multiple input, we check whether we have a reference
            # image component in the input data item.
            reference_input_img = None
            if len(input_item.components) > 0:
                ref_image_comp = input_item.components.reference_image
                if input_item.components.reference_image is not None:
                    reference_input_img = ref_image_comp.reference

            if self.should_run_on_cuda():
                self.model = self.model.to("cuda")

            model_dtype = next(self.model.parameters()).dtype

            input_list: list[torch.Tensor] = list()

            for key in self.input_fields:
                imf.log_debug(f"Key in self.input_fields: {key}")
                if key not in input_item:
                    raise ValueError(f'Key "{key}" not input_item, got {list(input_item.keys())}')
                if input_item[key].type not in (supported_element_types := (ElementType.IMAGE, ElementType.VECTOR)):
                    raise ValueError(f"Got unsupported element type {input_item[key].type}, {supported_element_types=}")
                imf.log_debug(f"Getting field {key} from input item: {input_item}")
                input_tensor = self.__sis_to_torch_tensor(input_item[key].sis)
                imf.log_debug("Successful conversion to torch tensor")

                # Move tensor to the GPU
                if self.should_run_on_cuda():
                    input_tensor = input_tensor.to("cuda")

                # Move input to same precision as the model
                input_tensor.to(dtype=model_dtype)

                input_list.append(input_tensor)
            imf.log_debug("Running backend model")
            output = self.model(*input_list)

        imf.log_debug("Converting output torch tensors to DataItem")
        out_item = self.__torch_dict_to_data_item(output, reference_image=reference_input_img)
        # checks that the output contains the field specified in
        # the MachineLearningModel yaml config under ``EngineOutputFields``.
        Engine.check_output_fields(self, out_item)
        return out_item

    @staticmethod
    def _load_model(traced_model_file: str):
        """
        Loads an ML Model saved in traced format
        """
        if not traced_model_file.endswith("pt"):
            raise ValueError(f"TorchEngine expects a .pt model, got {traced_model_file}")

        model = torch.jit.load(traced_model_file)
        return model

    @staticmethod
    def __sis_to_torch_tensor(sis: imf.SharedImageSet) -> torch.Tensor:
        """
        Converts imf.SharedImageSet to an torch.Tensor
        """

        return sis.torch()

    def __torch_dict_to_data_item(
        self,
        torch_dict: Union["torch.Tensor", dict, tuple],
        reference_image: imf.SharedImageSet = None,
    ) -> DataItem:
        """
        Converts the torch model output dictionary to a DataItem
        """
        output = DataItem()

        if isinstance(torch_dict, torch.Tensor):
            torch_dict = {"Prediction": torch_dict}

        if isinstance(torch_dict, tuple):
            torch_dict = {f"Prediction_{i}": v for i, v in enumerate(torch_dict)}

        assert isinstance(torch_dict, dict)

        for out_field, out_array in zip(self.output_fields, torch_dict.values()):

            out_sis = imf.SharedImageSet.from_torch(out_array)

            if reference_image is not None:
                for n in range(len(out_sis)):
                    out_sis[n].spacing = reference_image[n].spacing
                    out_sis[n].world_to_image_matrix = reference_image[n].world_to_image_matrix

            output[out_field] = ImageElement(out_sis.clone())
        return output

    def should_run_on_cuda(self) -> bool:
        return not self.force_cpu and torch.cuda.is_available()

    def available_providers(self) -> list[ExecutionProvider]:
        providers = [ExecutionProvider.CPU]
        if torch.cuda.is_available():
            providers += [ExecutionProvider.CUDA]
        return providers

    def provider(self) -> Optional[ExecutionProvider]:
        return (ExecutionProvider.CUDA if self.should_run_on_cuda() else ExecutionProvider.CPU)
