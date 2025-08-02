import imfusion
from imfusion.machinelearning import DataElement, ImageElement, VectorElement
from typing import Optional, Union


# create convenience methods for converting SharedImageSet to and from torch torch.Tensor
def to_torch(
    self: Union[DataElement, imfusion.SharedImageSet, imfusion.SharedImage],
    device: "torch.device" = None,
    dtype: "torch.dtype" = None,
    same_as: "torch.Tensor" = None,
) -> "torch.Tensor":
    """
    Convert SharedImageSet or a SharedImage to a torch.Tensor.

    :param self: Instance of SharedImageSet or SharedImage (this function bound as a method to SharedImageSet and SharedImage)
    :param device: Target device for the new torch.Tensor
    :param dtype: Type of the new torch.Tensor
    :param same_as: Template tensor whose device and dtype configuration should be matched.
                    :attr:`device` and :attr:`dtype` are still applied afterwards.
    :return: New torch.Tensor
    """
    import numpy as np
    import torch

    array = np.array(self, copy=False)

    # torch cannot handle uint other than uint8
    if array.dtype == np.uint16:
        array = array.astype(np.int32)
    tensor = torch.from_numpy(array)

    # perform casting
    if same_as is not None:
        tensor = tensor.to(same_as)
    tensor = tensor.to(device=device, dtype=dtype)

    # swap channel dimension
    if isinstance(self, (imfusion.SharedImage)):
        dimensions = list(range(len(tensor.shape)))
        dimensions.insert(0, dimensions.pop(-1))
        tensor = tensor.permute(dimensions)

    if isinstance(self, (imfusion.SharedImageSet, ImageElement)):
        dimensions = list(range(len(tensor.shape)))
        dimensions.insert(1, dimensions.pop(-1))
        tensor = tensor.permute(dimensions)

    # remove spatial dimension from vector elements
    if isinstance(self, (VectorElement)):
        if tensor.ndim > 2 and tensor.shape[1] == 1:  # this should always be the case
            tensor = tensor.squeeze(dim=1)

    return tensor


def __SIS_from_torch(
    cls: type,
    tensor: "torch.Tensor",
    get_metadata_from: Optional[imfusion.SharedImageSet] = None,
) -> imfusion.SharedImageSet:
    """
    Create a SharedImageSet from a torch Tensor. If you want to copy metadata from an existing SharedImageSet you can
    pass it as the :attr:`get_metadata_from` argument. If you are using this, make sure that the size of the tensor's
    batch dimension and the number of images in the SIS are equal. If :attr:`get_metadata_from` is provided,
    :attr:`properties` will be copied from the SIS and :attr:`world_to_image_matrix`, :attr:`spacing` and
    :attr:`modality` from the contained SharedImages.

    :param cls: Instance of type i.e. SharedImageSet (this function is bound as a classmethod to SharedImageSet)
    :param tensor: Instance of torch.Tensor
    :param get_metadata_from: Instance of SharedImageSet from which metadata should be copied.
    :return: New instance of SharedImageSet
    """

    # swap channel dimension
    dimensions = list(range(len(tensor.shape)))
    dimensions.append(dimensions.pop(1))
    tensor = tensor.permute(dimensions)
    array = tensor.detach().cpu().numpy()

    # add dimension in case of classification
    if len(array.shape) == 2:
        array = array[:, None, ...]

    # create new instance
    instance = (
        cls(array)
        if get_metadata_from is None
        else get_metadata_from.clone(with_data=False)
    )

    # copy metadata
    if get_metadata_from is not None:
        for original, sub_array in zip(get_metadata_from, array):
            image = imfusion.SharedImage(sub_array)
            image.world_to_image_matrix = original.world_to_image_matrix
            image.spacing = original.spacing
            image.modality = original.modality
            instance.add(image)

    return instance


# bind convenience methods
imfusion.SharedImageSet.torch = to_torch
imfusion.SharedImage.torch = to_torch
imfusion.SharedImageSet.from_torch = classmethod(__SIS_from_torch)


DataElement.torch = to_torch
ImageElement.from_torch = lambda tensor: ImageElement(
    imfusion.SharedImageSet.from_torch(tensor)
)
VectorElement.from_torch = lambda tensor: VectorElement(
    imfusion.SharedImageSet.from_torch(tensor)
)
