import itk
import os.path
import copy
import numpy as np

from mirp._data_import.generic_file import ImageFile, MaskFile


class ImageITKFile(ImageFile):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_stackable(self, stack_images: str) -> bool:
        """
        Is the image potentially stackable?
        :param stack_images: One of auto, yes or no. By default (auto), images are not stackable. Images might be
        stackable if an image object represents a single slice.
        :return: boolean value
        """
        if stack_images == "auto":
            return False
        elif stack_images == "yes":
            if self.image_dimension is None:
                raise ValueError(
                    "DEV: The image_dimension argument is expected to be set. Call load_metadata to set this attribute."
                )

            if len(self.image_dimension) < 3:
                return True
            elif self.image_dimension[0] == 1:
                return True
            else:
                return False

        elif stack_images == "no":
            return False
        else:
            raise ValueError(
                f"The stack_images argument is expected to be one of yes, auto, or no. Found: {stack_images}. "
                f"[{self.describe_self()}]"
            )

    def copy(self):
        # Remove metadata during copying to prevent ITK SwigPyObjects from being pickled (which produces errors).
        temporary_metadata = self.image_metadata
        self.remove_metadata()

        # Create a copy without copying any metadata.
        image_copy = copy.deepcopy(self)

        # Restore metadata.
        self.image_metadata = temporary_metadata
        image_copy.image_metadata = temporary_metadata

        return image_copy

    def _complete_image_origin(self, force=False, frame_id=None):
        if self.image_origin is None:
            self.load_metadata()

            # Get dimensions, as this determines what can be meaningfully read.
            n_dimensions = self.image_metadata.GetNumberOfDimensions()

            # Get origin.
            origin = [0.0] * n_dimensions
            for ii in range(n_dimensions):
                origin[n_dimensions - (ii + 1)] = self.image_metadata.GetOrigin(ii)

            # Set origin.
            self.image_origin = tuple(origin)

    def _complete_image_orientation(self, force=False, frame_id=None):
        if self.image_orientation is None:
            self.load_metadata()

            # Get dimensions, as this determines what can be meaningfully read.
            n_dimensions = self.image_metadata.GetNumberOfDimensions()

            # Get orientation.
            orientation = []
            for ii in range(n_dimensions):
                orientation.append(self.image_metadata.GetDirection(ii))

            self.image_orientation = np.reshape(np.ravel(np.array(orientation))[::-1], [n_dimensions, n_dimensions])

    def _complete_image_spacing(self, force=False, frame_id=None):
        if self.image_spacing is None:
            self.load_metadata()

            # Get dimensions, as this determines what can be meaningfully read.
            n_dimensions = self.image_metadata.GetNumberOfDimensions()

            # Get spacing.
            spacing = [0.0] * n_dimensions
            for ii in range(n_dimensions):
                spacing[n_dimensions - (ii + 1)] = self.image_metadata.GetSpacing(ii)

            # Set spacing.
            self.image_spacing = tuple(spacing)

    def _complete_image_dimensions(self, force=False):
        self.load_metadata()

        if self.image_dimension is None:
            # Get dimensions, as this determines what can be meaningfully read.
            n_dimensions = self.image_metadata.GetNumberOfDimensions()

            # Get size of dimensions
            dimensions = [0] * n_dimensions
            for ii in range(n_dimensions):
                dimensions[n_dimensions - (ii + 1)] = self.image_metadata.GetDimensions(ii)

            # Set size of dimensions
            self.image_dimension = tuple(dimensions)

    def create(self):
        return self

    def load_metadata(self, **kwargs):
        if self.image_metadata is not None:
            return

        if self.file_path is None or not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"The image file could not be found at the expected location: {self.file_path}. "
                f"[{self.describe_self()}]"
            )

        # Generate reader.
        reader = itk.ImageIOFactory.CreateImageIO(self.file_path, itk.CommonEnums.IOFileMode_ReadMode)
        reader.SetFileName(self.file_path)
        reader.ReadImageInformation()

        self.image_metadata = reader

    def load_data(self, **kwargs):
        if self.image_data is not None:
            return

        if self.file_path is None or not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"The image file could not be found at the expected location: {self.file_path}. "
                f"[{self.describe_self()}]"
            )

        # Load the image
        itk_img = itk.imread(os.path.join(self.file_path))
        self.image_data = itk.GetArrayFromImage(itk_img).astype(np.float32)


class MaskITKFile(ImageITKFile, MaskFile):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_data(self, **kwargs):
        if self.image_data is not None:
            return

        if self.file_path is None or not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"The mask file could not be found at the expected location: {self.file_path}. "
                f"[{self.describe_self()}]"
            )

        # Load the image
        itk_img = itk.imread(os.path.join(self.file_path))
        self.image_data = itk.GetArrayFromImage(itk_img).astype(int)
