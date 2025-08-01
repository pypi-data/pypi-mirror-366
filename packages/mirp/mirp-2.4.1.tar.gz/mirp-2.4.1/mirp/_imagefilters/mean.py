import copy
import numpy as np

from mirp._images.generic_image import GenericImage
from mirp._images.transformed_image import MeanTransformedImage
from mirp._imagefilters.generic import GenericFilter
from mirp._imagefilters.utilities import SeparableFilterSet
from mirp.settings.generic import SettingsClass


class MeanFilter(GenericFilter):

    def __init__(self, image: GenericImage, settings: SettingsClass, name: str):

        super().__init__(image=image, settings=settings, name=name)

        self.ibsi_compliant = True
        self.ibsi_id = "S60F"

        # Set the filter size
        self.filter_size = settings.img_transform.mean_filter_size

        # Set the filter mode
        self.mode = settings.img_transform.mean_filter_boundary_condition

    def generate_object(self):
        # Generator for transformation objects.
        filter_size = copy.deepcopy(self.filter_size)
        if not isinstance(filter_size, list):
            filter_size = [filter_size]

        # Iterate over options to yield filter objects with specific settings. A copy of the parent object is made to
        # avoid updating by reference.
        for current_filter_size in filter_size:
            filter_object = copy.deepcopy(self)
            filter_object.filter_size = current_filter_size

            yield filter_object

    def transform(self, image: GenericImage) -> MeanTransformedImage:
        # Create placeholder Laws kernel response map.
        response_map = MeanTransformedImage(
            image_data=None,
            filter_size=self.filter_size,
            boundary_condition=self.mode,
            riesz_order=None,
            riesz_steering=None,
            riesz_sigma_parameter=None,
            template=image
        )
        response_map.ibsi_compliant = self.ibsi_compliant and image.ibsi_compliant

        if image.is_empty():
            return response_map

        # Set up the filter kernel.
        filter_kernel = np.ones(self.filter_size, dtype=float) / self.filter_size

        # Create a filter set.
        if self.separate_slices:
            filter_set = SeparableFilterSet(
                filter_x=filter_kernel,
                filter_y=filter_kernel
            )
        else:
            filter_set = SeparableFilterSet(
                filter_x=filter_kernel,
                filter_y=filter_kernel,
                filter_z=filter_kernel
            )

        # Apply the filter.
        response_map.set_voxel_grid(voxel_grid=filter_set.convolve(
            voxel_grid=image.get_voxel_grid(),
            mode=self.mode)
        )

        return response_map
