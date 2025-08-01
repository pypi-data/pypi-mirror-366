import copy
import sys
if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

from mirp.settings.feature_parameters import FeatureExtractionSettingsClass
from mirp.settings.general_parameters import GeneralSettingsClass
from mirp.settings.image_processing_parameters import ImagePostProcessingClass
from mirp.settings.transformation_parameters import ImageTransformationSettingsClass
from mirp.settings.interpolation_parameters import ImageInterpolationSettingsClass, MaskInterpolationSettingsClass
from mirp.settings.resegmentation_parameters import ResegmentationSettingsClass
from mirp.settings.perturbation_parameters import ImagePerturbationSettingsClass


class SettingsClass:
    """
    Container for objects used to configure the image processing and feature processing workflow. This object can be
    initialised in two ways:

    * By providing (already initialised) configuration objects as arguments.
    * By passing arguments to configuration objects as keyword arguments. These configuration objects will then be
      created while initialising this container.

    Parameters
    ----------
    general_settings: GeneralSettingsClass, optional
        Configuration object for parameters related to the general process. See
        :class:`~mirp.settings.general_parameters.GeneralSettingsClass`.

    post_process_settings: ImagePostProcessingClass, optional
        Configuration object for parameters related to image (post-)processing. See
        :class:`~mirp.settings.image_processing_parameters.ImagePostProcessingClass`.

    perturbation_settings: ImagePerturbationSettingsClass, optional
        Configuration object for parameters related to image perturbation / augmentation. See
        :class:`~mirp.settings.perturbation_parameters.ImagePerturbationSettingsClass`.

    img_interpolate_settings: ImageInterpolationSettingsClass, optional
        Configuration object for parameters related to image resampling. See
        :class:`~mirp.settings.interpolation_parameters.ImageInterpolationSettingsClass`.

    roi_interpolate_settings: MaskInterpolationSettingsClass, optional
        Configuration object for parameters related to mask resampling. See
        :class:`~mirp.settings.interpolation_parameters.MaskInterpolationSettingsClass`.

    roi_resegment_settings: ResegmentationSettingsClass, optional
        Configuration object for parameters related to mask resegmentation. See
        :class:`~mirp.settings.resegmentation_parameters.ResegmentationSettingsClass`.

    feature_extr_settings: FeatureExtractionSettingsClass, optional
        Configuration object for parameters related to feature computation. See
        :class:`~mirp.settings.feature_parameters.FeatureExtractionSettingsClass`.

    img_transform_settings: ImageTransformationSettingsClass, optional
        Configuration object for parameters related to image transformation. See
        :class:`~mirp.settings.transformation_parameters.ImageTransformationSettingsClass`.

    **kwargs: Any, optional
        Keyword arguments for initialising configuration objects stored in this container object.

    See Also
    --------

    * general settings (:class:`~mirp.settings.general_parameters.GeneralSettingsClass`)
    * image post-processing (:class:`~mirp.settings.image_processing_parameters.ImagePostProcessingClass`)
    * image perturbation / augmentation (:class:`~mirp.settings.perturbation_parameters.ImagePerturbationSettingsClass`)
    * image interpolation / resampling (:class:`~mirp.settings.interpolation_parameters.ImageInterpolationSettingsClass`
      and :class:`~mirp.settings.interpolation_parameters.MaskInterpolationSettingsClass`)
    * mask resegmentation (:class:`~mirp.settings.resegmentation_parameters.ResegmentationSettingsClass`)
    * image transformation (:class:`~mirp.settings.transformation_parameters.ImageTransformationSettingsClass`)
    * feature computation / extraction (
      :class:`~mirp.settings.feature_parameters.FeatureExtractionSettingsClass`)

    """
    def __init__(
            self,
            general_settings: None | GeneralSettingsClass = None,
            post_process_settings: None | ImagePostProcessingClass = None,
            perturbation_settings: None | ImagePerturbationSettingsClass = None,
            img_interpolate_settings: None | ImageInterpolationSettingsClass = None,
            roi_interpolate_settings: None | MaskInterpolationSettingsClass = None,
            roi_resegment_settings: None | ResegmentationSettingsClass = None,
            feature_extr_settings: None | FeatureExtractionSettingsClass = None,
            img_transform_settings: None | ImageTransformationSettingsClass = None,
            **kwargs: Unpack[
                None | GeneralSettingsClass | ImagePostProcessingClass | ImagePostProcessingClass |
                ImageInterpolationSettingsClass | MaskInterpolationSettingsClass | ResegmentationSettingsClass |
                FeatureExtractionSettingsClass | ImageTransformationSettingsClass
            ]
    ):
        kwargs = copy.deepcopy(kwargs)

        # General settings.
        if general_settings is None:
            general_settings = GeneralSettingsClass(**kwargs)
        self.general = general_settings

        # Remove by_slice and no_approximation from the keyword arguments to avoid double passing.
        kwargs.pop("by_slice", None)
        kwargs.pop("no_approximation", None)
        kwargs.pop("ibsi_compliant", None)

        # Image interpolation settings.
        if img_interpolate_settings is None:
            img_interpolate_settings = ImageInterpolationSettingsClass(
                by_slice=general_settings.by_slice,
                **kwargs
            )
        self.img_interpolate = img_interpolate_settings

        # Mask interpolation settings.
        if roi_interpolate_settings is None:
            roi_interpolate_settings = MaskInterpolationSettingsClass(**kwargs)
        self.roi_interpolate = roi_interpolate_settings

        # Image (post-)processing settings.
        if post_process_settings is None:
            post_process_settings = ImagePostProcessingClass(**kwargs)
        self.post_process = post_process_settings

        # Image perturbation settings.
        if perturbation_settings is None:
            perturbation_settings = ImagePerturbationSettingsClass(**kwargs)
        self.perturbation = perturbation_settings

        # Mask resegmentation settings.
        if roi_resegment_settings is None:
            roi_resegment_settings = ResegmentationSettingsClass(**kwargs)
        self.roi_resegment = roi_resegment_settings

        # Feature extraction settings.
        if feature_extr_settings is None:
            feature_extr_settings = FeatureExtractionSettingsClass(
                by_slice=general_settings.by_slice,
                no_approximation=general_settings.no_approximation,
                ibsi_compliant=general_settings.ibsi_compliant,
                **kwargs
            )
        self.feature_extr = feature_extr_settings

        # Image transformation settings
        if img_transform_settings is None:
            img_transform_settings = ImageTransformationSettingsClass(
                by_slice=general_settings.by_slice,
                ibsi_compliant=general_settings.ibsi_compliant,
                **kwargs
            )
        self.img_transform = img_transform_settings

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        if self.general != other.general:
            return False
        if self.img_interpolate != other.img_interpolate:
            return False
        if self.roi_interpolate != other.roi_interpolate:
            return False
        if self.post_process != other.post_process:
            return False
        if self.perturbation != other.perturbation:
            return False
        if self.roi_resegment != other.roi_resegment:
            return False
        if self.feature_extr != other.feature_extr:
            return False
        if self.img_transform != other.img_transform:
            return False

        return True
