from __future__ import annotations
import imfusion as imfusion
from imfusion.machinelearning import DataElement
from imfusion.machinelearning import ImageElement
from imfusion.machinelearning import VectorElement
__all__ = ['DataElement', 'ImageElement', 'VectorElement', 'imfusion', 'to_torch']
def __SIS_from_torch(cls: type, tensor: torch.Tensor, get_metadata_from: typing.Optional[imfusion.SharedImageSet] = None) -> imfusion.SharedImageSet:
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
def to_torch(self: typing.Union[imfusion.machinelearning.DataElement, imfusion.SharedImageSet, imfusion.SharedImage], device: torch.device = None, dtype: torch.dtype = None, same_as: torch.Tensor = None) -> torch.Tensor:
    """
    
        Convert SharedImageSet or a SharedImage to a torch.Tensor.
    
        :param self: Instance of SharedImageSet or SharedImage (this function bound as a method to SharedImageSet and SharedImage)
        :param device: Target device for the new torch.Tensor
        :param dtype: Type of the new torch.Tensor
        :param same_as: Template tensor whose device and dtype configuration should be matched.
                        :attr:`device` and :attr:`dtype` are still applied afterwards.
        :return: New torch.Tensor
        
    """
