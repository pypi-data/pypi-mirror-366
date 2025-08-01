import numpy as np
from typing import Any
from mirp._images.generic_image import GenericImage


class PETImage(GenericImage):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_colour_map():
        return "gist_yarg"

    @staticmethod
    def get_default_lowest_intensity():
        return 0.0

    @staticmethod
    def get_default_ivh_discretisation_method():
        return "fixed_bin_size"

    @staticmethod
    def get_default_ivh_bin_size():
        return 0.10

    def update_image_data(self):
        if self.image_data is None:
            return

        # Ensure that PET values are not negative.
        self.image_data[self.image_data < 0.0] = 0.0

    def normalise_intensities(
            self,
            normalisation_method: None | str = "none",
            intensity_range: None | tuple[Any, Any] = None,
            saturation_range: None | tuple[Any, Any] = None,
            mask: None | np.ndarray = None
    ):
        """
        Normalise intensities. NOTE: this changes the class of the object from PETImage to GenericImage as
        normalisation breaks the one-to-one relationship between intensities and SUV values or PET counts.
        """
        if self.image_data is None:
            return self

        if normalisation_method is None or normalisation_method == "none":
            return self

        new_image = GenericImage(image_data=self.image_data)
        new_image.update_from_template(template=self)
        new_image = new_image.normalise_intensities(
            normalisation_method=normalisation_method,
            intensity_range=intensity_range,
            saturation_range=saturation_range,
            mask=mask
        )

        return new_image

    def scale_intensities(self, scale: float):
        if self.image_data is None:
            return self

        if scale == 1.0:
            return self

        # Scaling intensities changes the object class from PETImage to GenericImage as this breaks the one-to-one
        # relationship between intensities and SUV values or PET counts.
        new_image = GenericImage(image_data=self.image_data)
        new_image.update_from_template(template=self)
        new_image = new_image.scale_intensities(scale=scale)

        return new_image
