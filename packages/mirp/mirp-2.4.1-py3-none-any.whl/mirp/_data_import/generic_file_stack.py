import copy
import itertools
import warnings

import numpy as np
import pandas as pd

from mirp._data_import.generic_file import ImageFile, MaskFile
from mirp._data_import.dicom_file import ImageDicomFile, MaskDicomFile
from mirp._data_import.itk_file import ImageITKFile, MaskITKFile
from mirp._data_import.numpy_file import ImageNumpyFile, MaskNumpyFile


class ImageFileStack(ImageFile):
    def is_stackable(self, stack_images: str):
        return False

    def __init__(
            self,
            image_file_objects: list[ImageFile] | list[ImageDicomFile] | list[ImageITKFile] | list[ImageNumpyFile],
            dir_path: None | str = None,
            sample_name: None | str = None,
            image_name: None | str | list[str] = None,
            image_modality: None | str = None,
            image_file_type: None | str = None,
            **kwargs
    ):

        if dir_path is None:
            dir_path = image_file_objects[0].dir_path

        if sample_name is None:
            sample_name = image_file_objects[0].sample_name

        if image_name is None:
            image_name = image_file_objects[0].image_name

        if image_modality is None:
            image_modality = image_file_objects[0].modality

        if image_file_type is None:
            image_file_type = image_file_objects[0].file_type

        if len(image_file_objects) == 1:
            raise ValueError(f"DEV: More than one file is expected for file stacks.")

        # Aspects regarding the image itself are set based on the stack itself.
        super().__init__(
            file_path=None,
            dir_path=dir_path,
            sample_name=sample_name,
            file_name=None,
            image_name=image_name,
            image_modality=image_modality,
            image_file_type=image_file_type,
            image_data=None,
            image_origin=None,
            image_orientation=None,
            image_spacing=None,
            image_dimensions=None,
            **kwargs
        )

        self.image_file_objects = image_file_objects
        self.slice_positions: None | list[float] = None

    def create(self):
        # Import locally to avoid potential circular references.
        from mirp._data_import.dicom_file_stack import ImageDicomFileStack
        from mirp._data_import.itk_file_stack import ImageITKFileStack
        from mirp._data_import.numpy_file_stack import ImageNumpyFileStack

        if all(isinstance(image_file_object, ImageDicomFile) for image_file_object in self.image_file_objects):
            file_stack_class = ImageDicomFileStack
            file_type = "dicom"

        elif all(isinstance(image_file_object, ImageITKFile) for image_file_object in self.image_file_objects):
            file_stack_class = ImageITKFileStack
            file_type = self.image_file_objects[0].file_type

        elif all(isinstance(image_file_object, ImageNumpyFile) for image_file_object in self.image_file_objects):
            file_stack_class = ImageNumpyFileStack
            file_type = "numpy"

        else:
            raise TypeError(
                f"The list of image objects does not consist of a known object type. [{self.describe_self()}]"
            )

        image_file_stack = file_stack_class(
            image_file_objects=self.image_file_objects,
            dir_path=self.dir_path,
            sample_name=self.sample_name,
            image_name=self.image_name,
            image_modality=self.modality,
            image_file_type=file_type
        )

        return image_file_stack

    def complete(self, remove_metadata=False, force=False):
        raise NotImplementedError(
            f"DEV: There is (intentionally) no generic implementation of complete. Please specify "
            f"implementation for subclasses."
        )

    def _complete_sample_name(self):
        if self.sample_name is None:
            self.image_file_objects[0]._complete_sample_name()
            self.sample_name = self.image_file_objects[0].sample_name

    def _complete_modality(self):
        if self.modality is None:
            self.image_file_objects[0]._complete_modality()
            self.modality = self.image_file_objects[0].modality

    def _complete_image_origin(self, force=False, frame_id=None):
        # Image origin and other image-related aspects are set using the complete method of subclasses.
        pass

    def _complete_image_orientation(self, force=False, frame_id=None):
        pass

    def _complete_image_spacing(self, force=False, frame_id=None):
        pass

    def _complete_image_dimensions(self, force=False):
        pass

    def sort_image_objects_by_file(self):
        """
        Strip sample name and any image name from filenames. Then isolate numeric values.
        sequences of numeric values. We follow the following rules:
        1. Check if all files have a numeric value in their name, otherwise, use the original order.
        2. Check that all files only have a single range of numeric values (otherwise, it might hard to arrange and
        identify sequences).
        3. Sort and check that sequences are truly sequential, i.e. have a difference of one.
        :return: nothing, changes are made in-place.
        """

        file_name_numeric = [image_object._get_numeric_sequence_from_file() for image_object in self.image_file_objects]
        if any(current_file_name_numeric is None for current_file_name_numeric in file_name_numeric):
            warnings.warn(
                f"Cannot form stacks from numpy slices based on the file name as numeric values are missing "
                f"from one or more files. The original file order is used. [{self.describe_self()}]", UserWarning
            )
            return

        if any(len(current_file_name_numeric) > 1 for current_file_name_numeric in file_name_numeric):
            warnings.warn(
                f"Cannot form stacks from numpy slices based on the file name as more than one sequence of numeric "
                f"values are present in the name of one or more files. This excludes the sample name (if known) and "
                f"any identifiers for image data. The original file order is used. [{self.describe_self()}]",
                UserWarning
            )
            return

        # Flatten array and convert to integer values.
        file_name_numeric = list(itertools.chain.from_iterable(file_name_numeric))
        file_name_numeric = [int(current_file_name_numeric) for current_file_name_numeric in file_name_numeric]

        if len(file_name_numeric) == 1:
            return

        # Check that all numbers are sequential.
        if not np.all(np.diff(np.sort(np.array(file_name_numeric))) == 1):
            warnings.warn(
                f"Cannot form stacks from numpy slices based on the file name as numbers are not fully sequential for"
                f" all files. The original file order is used. [{self.describe_self()}]",
                UserWarning
            )
            return

        position_table = pd.DataFrame({
            "original_object_order": list(range(len(self.image_file_objects))),
            "order_id": file_name_numeric,
        }).sort_values(by=["order_id"])

        # Sort image file objects.
        self.image_file_objects = [
            self.image_file_objects[position_table.original_object_order[ii]]
            for ii in range(len(position_table))
        ]

    def load_metadata(self, limited=False, include_image=False):
        # Load metadata for underlying files in the order indicated by self.image_file_objects.
        for image_file_object in self.image_file_objects:
            image_file_object.load_metadata(limited=limited, include_image=include_image)

    def remove_metadata(self):
        for image_file_object in self.image_file_objects:
            image_file_object.remove_metadata()

    def load_data(self, **kwargs):
        # Load data for underlying files in the order indicated by self.image_file_objects.
        for image_file_object in self.image_file_objects:
            image_file_object.load_data(**kwargs)

    def stack_slices(self):
        if self.image_data is not None:
            return

        image = np.zeros(self.image_dimension, dtype=np.float32)
        for ii, image_file in enumerate(self.image_file_objects):
            if image_file.image_data is None:
                raise ValueError(
                    "DEV: the image_data attribute of underlying image files are not set. Please call load_data first.")
            image[ii, :, :] = image_file.image_data.astype(np.float32)

        self.image_data = image


class MaskFileStack(ImageFileStack, MaskFile):

    def __init__(
            self,
            image_file_objects: list[MaskFile] | list[MaskDicomFile] | list[MaskITKFile] | list[MaskNumpyFile],
            **kwargs
    ):

        super().__init__(image_file_objects=image_file_objects, **kwargs)

    def complete(self, remove_metadata=False, force=False):
        raise NotImplementedError(
            f"DEV: There is (intentionally) no generic implementation of complete. Please specify "
            f"implementation for subclasses."
        )

    def create(self):
        # Import locally to avoid potential circular references.
        from mirp._data_import.dicom_file_stack import MaskDicomFileStack
        from mirp._data_import.itk_file_stack import MaskITKFileStack
        from mirp._data_import.numpy_file_stack import MaskNumpyFileStack

        if all(isinstance(image_file_object, MaskDicomFile) for image_file_object in self.image_file_objects):
            file_stack_class = MaskDicomFileStack
            file_type = "dicom"

        elif all(isinstance(image_file_object, MaskITKFile) for image_file_object in self.image_file_objects):
            file_stack_class = MaskITKFileStack
            file_type = self.image_file_objects[0].file_type

        elif all(isinstance(image_file_object, MaskNumpyFile) for image_file_object in self.image_file_objects):
            file_stack_class = MaskNumpyFileStack
            file_type = "numpy"

        else:
            raise TypeError(
                f"The list of image objects does not consist of a known object type. [{self.describe_self()}]"
            )

        image_file_stack = file_stack_class(
            image_file_objects=self.image_file_objects,
            dir_path=self.dir_path,
            sample_name=self.sample_name,
            image_name=self.image_name,
            image_modality=self.modality,
            image_file_type=file_type,
            roi_name=self.roi_name
        )

        return image_file_stack

    def stack_slices(self):
        if self.image_data is not None:
            return

        image = np.zeros(self.image_dimension, dtype=int)
        for ii, image_file in enumerate(self.image_file_objects):
            if image_file.image_data is None:
                raise ValueError(
                    "DEV: the image_data attribute of underlying mask files are not set. Please call load_data first."
                )
            image[ii, :, :] = image_file.image_data.astype(int)

        self.image_data = image
