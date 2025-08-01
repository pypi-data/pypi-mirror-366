import copy

import numpy as np
import scipy.ndimage as ndi
import scipy.fft as fft
import pandas as pd

from copy import deepcopy
from scipy.special import factorial


def pool_voxel_grids(x1, x2, pooling_method):

    if x1 is None:
        return copy.deepcopy(x2)

    elif pooling_method == "max":
        # Perform max pooling by selecting the maximum intensity of each voxel.
        return np.maximum(x1, x2)

    elif pooling_method == "min":
        # Perform min pooling by selecting the minimum intensity of each voxel.
        return np.minimum(x1, x2)

    elif pooling_method in ["mean", "sum"]:
        # Perform mean / sum pooling by summing the intensities of each voxel.
        return np.add(x1, x2)

    else:
        raise ValueError(f"Unknown pooling method encountered: {pooling_method}")


class SeparableFilterSet:
    def __init__(
            self,
            filter_x,
            filter_y,
            filter_z=None,
            pre_filter_x=None,
            pre_filter_y=None,
            pre_filter_z=None
    ):
        self.x = filter_x
        self.y = filter_y
        self.z = filter_z

        self.pr_x = pre_filter_x
        self.pr_y = pre_filter_y
        self.pr_z = pre_filter_z

        # Extend even-sized filters.
        for attr in ["x", "y", "z", "pr_x", "pr_y", "pr_z"]:
            if self.__dict__[attr] is not None:

                # Check if the kernel is even or odd.
                if len(self.__dict__[attr]) % 2 == 0:
                    self.__dict__[attr] = np.append(self.__dict__[attr], 0.0)

    def permute_filters(self, rotational_invariance=True, require_pre_filter=False, as_filter_table=False):

        if require_pre_filter:
            if self.pr_x is None or self.pr_y is None:
                raise ValueError("The pre-filter should be set for all dimensions.")

            if self.z is not None and self.pr_z is None:
                raise ValueError("The pre-filter should have a component in the z-direction.")

            elif self.z is None and self.pr_z is not None:
                raise ValueError("The pre-filter should not have a component in the z-direction.")

        # Return an encapsulated version of the object.
        if not rotational_invariance:
            return [self]

        permuted_filters = []

        # Initiate filter strings
        g_x = "gx"
        g_y = "gy"
        g_z = "gz"
        jg_x = "jgx"
        jg_y = "jgy"
        jg_z = "jgz"

        # Test if x and y filters are the same.
        if np.array_equiv(self.x, self.y):
            g_y = g_x
            jg_y = jg_x

        # Test if x and z filters are the same
        if self.z is not None:
            if np.array_equiv(self.x, self.z):
                g_z = g_x
                jg_z = jg_x

        # Test if y and z filters are the same
        if self.z is not None:
            if np.array_equiv(self.y, self.z):
                g_z = g_y
                jg_z = jg_y

        # Test if the x-filter is symmetric.
        if np.array_equiv(self.x, np.flip(self.x)):
            jg_x = g_x

        # Test if the y-filter is symmetric.
        if np.array_equiv(self.y, np.flip(self.y)):
            jg_y = g_y

        # Test if the y-filter is symmetric.
        if self.z is not None:
            if np.array_equiv(self.z, np.flip(self.z)):
                jg_z = g_z

        if self.z is None:
            # 2D right-hand permutations
            permuted_filters += [{"x": g_x, "y": g_y}]
            permuted_filters += [{"x": jg_y, "y": g_x}]
            permuted_filters += [{"x": jg_x, "y": jg_y}]
            permuted_filters += [{"x": g_y, "y": jg_x}]

        else:
            # 3D right-hand permutations
            permuted_filters += [{"x": g_x, "y": g_y, "z": g_z}]
            permuted_filters += [{"x": jg_z, "y": g_y, "z": g_x}]
            permuted_filters += [{"x": jg_x, "y": g_y, "z": jg_z}]
            permuted_filters += [{"x": g_z, "y": g_y, "z": jg_x}]

            permuted_filters += [{"x": g_y, "y": g_z, "z": g_x}]
            permuted_filters += [{"x": g_y, "y": jg_z, "z": jg_x}]
            permuted_filters += [{"x": g_y, "y": jg_x, "z": g_z}]
            permuted_filters += [{"x": jg_x, "y": jg_y, "z": g_z}]

            permuted_filters += [{"x": jg_y, "y": g_x, "z": g_z}]
            permuted_filters += [{"x": jg_z, "y": jg_x, "z": g_y}]
            permuted_filters += [{"x": jg_z, "y": jg_y, "z": jg_x}]
            permuted_filters += [{"x": jg_z, "y": g_x, "z": jg_y}]

            permuted_filters += [{"x": jg_y, "y": jg_x, "z": jg_z}]
            permuted_filters += [{"x": g_x, "y": jg_y, "z": jg_z}]
            permuted_filters += [{"x": g_y, "y": g_x, "z": jg_z}]
            permuted_filters += [{"x": g_z, "y": jg_x, "z": jg_y}]

            permuted_filters += [{"x": g_z, "y": jg_y, "z": g_x}]
            permuted_filters += [{"x": g_z, "y": g_x, "z": g_y}]
            permuted_filters += [{"x": jg_x, "y": g_z, "z": g_y}]
            permuted_filters += [{"x": jg_y, "y": g_z, "z": jg_x}]

            permuted_filters += [{"x": g_x, "y": g_z, "z": jg_y}]
            permuted_filters += [{"x": jg_x, "y": jg_z, "z": jg_y}]
            permuted_filters += [{"x": jg_y, "y": jg_z, "z": g_x}]
            permuted_filters += [{"x": g_x, "y": jg_z, "z": g_y}]

        # Combine filters into a table.
        permuted_filters = pd.DataFrame(permuted_filters)

        if require_pre_filter:
            # Create a pre-filter to derive a table with filter orientations.
            pre_filter_set = SeparableFilterSet(filter_x=self.pr_x,
                                                filter_y=self.pr_y,
                                                filter_z=self.pr_z)

            permuted_pre_filters = pre_filter_set.permute_filters(rotational_invariance=rotational_invariance,
                                                                  as_filter_table=True)

            # Update the columns names
            permuted_pre_filters.rename(columns={"x": "pr_x",
                                                 "y": "pr_y",
                                                 "z": "pr_z"},
                                        inplace=True)

            # Join with the permuted_filters table.
            permuted_filters = pd.concat([permuted_pre_filters, permuted_filters], axis=1)

        if as_filter_table:
            return permuted_filters

        # Remove duplicates.
        permuted_filters = permuted_filters.drop_duplicates(ignore_index=True)

        filter_set_list = []
        for ii in range(len(permuted_filters)):
            permuted_filter_set = permuted_filters.loc[ii, :]

            filter_obj = deepcopy(self)

            if require_pre_filter:
                if self.z is None:
                    filter_set_list += [SeparableFilterSet(
                        filter_x=filter_obj._translate_filter(permuted_filter_set.x),
                        filter_y=filter_obj._translate_filter(permuted_filter_set.y),
                        pre_filter_x=filter_obj._translate_filter(permuted_filter_set.pr_x, True),
                        pre_filter_y=filter_obj._translate_filter(permuted_filter_set.pr_y, True)
                    )]

                else:
                    filter_set_list += [SeparableFilterSet(
                        filter_x=filter_obj._translate_filter(permuted_filter_set.x),
                        filter_y=filter_obj._translate_filter(permuted_filter_set.y),
                        filter_z=filter_obj._translate_filter(permuted_filter_set.z),
                        pre_filter_x=filter_obj._translate_filter(permuted_filter_set.pr_x, True),
                        pre_filter_y=filter_obj._translate_filter(permuted_filter_set.pr_y, True),
                        pre_filter_z=filter_obj._translate_filter(permuted_filter_set.pr_z, True)
                    )]

            else:
                if self.z is None:
                    filter_set_list += [SeparableFilterSet(
                        filter_x=filter_obj._translate_filter(permuted_filter_set.x),
                        filter_y=filter_obj._translate_filter(permuted_filter_set.y)
                    )]

                else:
                    filter_set_list += [SeparableFilterSet(
                        filter_x=filter_obj._translate_filter(permuted_filter_set.x),
                        filter_y=filter_obj._translate_filter(permuted_filter_set.y),
                        filter_z=filter_obj._translate_filter(permuted_filter_set.z)
                    )]

        return filter_set_list

    def _translate_filter(self, filter_symbol, use_pre_filter=False):

        if filter_symbol == "gx":
            if use_pre_filter:
                return self.pr_x
            else:
                return self.x

        elif filter_symbol == "gy":
            if use_pre_filter:
                return self.pr_y
            else:
                return self.y

        elif filter_symbol == "gz":
            if use_pre_filter:
                return self.pr_z
            else:
                return self.z

        elif filter_symbol == "jgx":
            if use_pre_filter:
                return np.flip(self.pr_x)
            else:
                return np.flip(self.x)

        elif filter_symbol == "jgy":
            if use_pre_filter:
                return np.flip(self.pr_y)
            else:
                return np.flip(self.y)

        elif filter_symbol == "jgz":
            if use_pre_filter:
                return np.flip(self.pr_z)
            else:
                return np.flip(self.z)

        else:
            raise ValueError(f"Encountered unrecognised filter symbol: {filter_symbol}")

    def decompose_filter(self, method="a_trous"):

        if method == "a_trous":
            # Add in 0s for the à trous algorithm

            # Iterate over filters.
            for attr in ["x", "y", "z", "pr_x", "pr_y", "pr_z"]:
                if self.__dict__[attr] is not None:
                    # Strip zeros from tail and head.
                    # old_filter_kernel = np.trim_zeros(deepcopy(self.__dict__[attr]))
                    old_filter_kernel = deepcopy(self.__dict__[attr])

                    # Create an array of zeros
                    new_filter_kernel = np.zeros(len(old_filter_kernel) * 2 - 1, dtype=float)

                    # Place the original filter constants at every second position. This creates a hole (0.0) between
                    # each of the filter constants.
                    new_filter_kernel[::2] = old_filter_kernel

                    # Update the attribute.
                    self.__dict__[attr] = new_filter_kernel

        else:
            raise ValueError(f"Unknown filter decomposition method: {method}")

    def convolve(self, voxel_grid, mode, use_pre_filter=False):

        # Ensure that we work from a local copy of voxel_grid to prevent updating it by reference.
        voxel_grid = deepcopy(voxel_grid)

        if use_pre_filter:
            if self.pr_x is None or self.pr_y is None or (self.z is not None and self.pr_z is None):
                raise ValueError("Pre-filter kernels are expected, but not found.")

            # Apply filter along the z-axis. Note that the voxel grid is stored with z, y, x indexing. Hence the
            # z-axis is the first axis, the y-axis the second, and the x-axis the third.
            if self.pr_z is not None:
                voxel_grid = ndi.convolve1d(voxel_grid, weights=self.pr_z, axis=0, mode=mode)

            # Apply filter along the y-axis.
            voxel_grid = ndi.convolve1d(voxel_grid, weights=self.pr_y, axis=1, mode=mode)

            # Apply filter along the x-axis.
            voxel_grid = ndi.convolve1d(voxel_grid, weights=self.pr_x, axis=2, mode=mode)

        else:
            # Apply filter along the z-axis. Note that the voxel grid is stored with z, y, x indexing. Hence the
            # z-axis is the first axis, the y-axis the second, and the x-axis the third.
            if self.z is not None:
                voxel_grid = ndi.convolve1d(voxel_grid, weights=self.z, axis=0, mode=mode)

            # Apply filter along the y-axis.
            voxel_grid = ndi.convolve1d(voxel_grid, weights=self.y, axis=1, mode=mode)

            # Apply filter along the x-axis.
            voxel_grid = ndi.convolve1d(voxel_grid, weights=self.x, axis=2, mode=mode)

        return voxel_grid


class FilterSet:
    def __init__(
            self,
            filter_set: np.ndarray,
            transformed=False,
            pad_image=True,
            riesz_order: None | list[int] = None,
            riesz_steered: bool = False,
            riesz_sigma: None | float = None
    ):

        self.filter_set = filter_set
        self.transformed = transformed
        self.pad_image = pad_image
        self.riesz_order = riesz_order
        self.riesz_steered = riesz_steered
        self.riesz_sigma = riesz_sigma

    def _get_coordinate_grid(self, axis=None):

        # Determine the grid center.
        grid_center = (np.array(self.filter_set.shape, dtype=float) - 1.0) / 2.0

        # Determine distance from center
        coordinate_grid = list(np.indices(self.filter_set.shape, sparse=True))
        coordinate_grid = [(coordinate_grid[ii] - center_pos) / center_pos for ii, center_pos in enumerate(grid_center)]

        # Broadcast to filter size shape.
        if axis is not None:
            coordinate_grid = np.broadcast_to(coordinate_grid[axis], self.filter_set.shape)

        return coordinate_grid

    def _get_distance_grid(self):

        # Generate a coordinate grid.
        coordinate_grid = self._get_coordinate_grid()

        # Compute the distances in the grid.
        distance_grid = np.sqrt(np.sum(
            np.power(np.meshgrid(coordinate_grid[0], coordinate_grid[1], coordinate_grid[2]), 2.0), axis=0)
        )

        return distance_grid

    def _pad_image(
            self,
            voxel_grid: np.ndarray,
            mode: str,
            axis: None | int = None
    ):

        # Modes in scipy and numpy are defined differently.
        if mode == "reflect":
            mode = "symmetric"
        elif mode == "symmetric":
            mode = "reflect"
        elif mode == "nearest":
            mode = "edge"
        elif mode == "mirror":
            mode = "reflect"

        # Ensure that we work from a local copy of voxel_grid to prevent updating it by reference.
        voxel_grid = deepcopy(voxel_grid)

        # Determine the original shape
        original_shape = voxel_grid.shape

        # Pad original image with half the kernel size on axes other than axis.
        if self.pad_image:
            pad_size = np.floor(np.array(self.filter_set.shape) / 2.0)
        else:
            pad_size = np.zeros(len(self.filter_set.shape))

        # Determine pad widths.
        pad_width = []
        original_offset = []
        axis_id = 0

        for current_axis in range(3):
            if current_axis != axis:
                # Select current axis.
                current_pad_size = int(pad_size[axis_id])

                # Add to elements.
                pad_width.append((current_pad_size, current_pad_size))
                original_offset.append(current_pad_size)

                # Update axis_id to skip to next element.
                axis_id += 1

            else:
                pad_width.append((0, 0))
                original_offset.append(0)

        # Set padding
        voxel_grid = np.pad(voxel_grid, pad_width=pad_width, mode=mode)

        return voxel_grid, original_shape, original_offset

    def _transform_filter(self, filter_shape, transform_method="interpolate"):

        if transform_method not in ["zero_pad", "interpolate"]:
            raise ValueError(
                f"The transform_method argument expects \"zero_pad\" or \"interpolate\". Found: {transform_method}"
            )

        if self.transformed and not np.equal(self.filter_set.shape, filter_shape).all() and transform_method == \
                "zero_pad":
            # Zero-padding takes place in the spatial domain. We therefore have to inverse transform the filter.
            self.filter_set = fft.ifftn(self.filter_set)

            # Transform back to the Fourier domain
            self.filter_set = fft.fftn(self.filter_set,
                                       filter_shape)

        elif self.transformed and not np.equal(self.filter_set.shape, filter_shape).all() and transform_method == \
                "interpolate":
            # Find zoom factor.
            zoom_factor = np.divide(filter_shape, self.filter_set.shape)

            # Make sure to zoom in the centric filter view.
            self.filter_set = fft.ifftshift(ndi.zoom(fft.fftshift(self.filter_set),
                                                     zoom=zoom_factor))

        elif not self.transformed:
            # Transform to the Fourier domain
            self.filter_set = fft.fftn(self.filter_set,
                                       filter_shape)

            self.transformed = True

    def _riesz_transform(self):

        # Skip if no Riesz transformation order have been set.
        if self.riesz_order is None:
            return

        # Skip if all Riesz transformation orders are 0.
        if not np.any(np.array(self.riesz_order) > 0):
            return

        # Check if the number of dimensions match.
        if len(self.riesz_order) is not np.ndim(self.filter_set):
            raise ValueError(f"The number of transformation orders ({len(self.riesz_order)}) does not match the filter "
                             f"dimension ({np.ndim(self.filter_set)}).")

        # Determine the order sum (L).
        order_sum = np.sum(np.array(self.riesz_order))

        # Compute the pre-factor, see equation 4.11.
        prefactor = (-1.0j) ** order_sum * np.sqrt(factorial(order_sum) / np.prod(factorial(np.array(
            self.riesz_order))))

        # Distance grid, see equation 4.11.
        distance_grid = np.power(self._get_distance_grid(), order_sum)

        # Set up gradient grid.
        gradient_grid = np.ones(self.filter_set.shape, dtype=np.cdouble)

        # Iterate over transformation orders.
        for ii, riesz_transform_order in enumerate(self.riesz_order):
            # Skip if no transformation is required.
            if riesz_transform_order == 0:
                continue

            # Update the gradient grid.
            gradient_grid = np.multiply(gradient_grid,
                                        np.power(self._get_coordinate_grid(axis=ii), riesz_transform_order))

        # Divide by l2-norm.
        gradient_grid = prefactor * np.divide(gradient_grid, distance_grid)

        # Update filter by taking Hadamard product.
        self.filter_set = fft.ifftshift(np.multiply(fft.fftshift(self.filter_set), gradient_grid))

    @staticmethod
    def _return_response(voxel_grid, response, original_offset, original_shape):
        # Compute response map.
        if response in ["modulus", "abs", "magnitude"]:
            voxel_grid = np.abs(voxel_grid)

        elif response in ["angle", "phase", "argument"]:
            voxel_grid = np.angle(voxel_grid)

        elif response in ["real"]:
            voxel_grid = np.real(voxel_grid)

        elif response in ["imaginary"]:
            voxel_grid = np.imag(voxel_grid)

        else:
            raise ValueError(f"The response argument should be \"modulus\", \"abs\", \"magnitude\", \"angle\", "
                             f"\"phase\", \"argument\", \"real\" or \"imaginary\". Found: {response}")

        # Crop image to original size.
        voxel_grid = voxel_grid[2 * original_offset[0]:2 * original_offset[0] + original_shape[0],
                                2 * original_offset[1]:2 * original_offset[1] + original_shape[1],
                                2 * original_offset[2]:2 * original_offset[2] + original_shape[2]]

        return voxel_grid


class FilterSet2D(FilterSet):

    def convolve(self,
                 voxel_grid: np.ndarray,
                 mode,
                 response,
                 axis=0):

        # Pad the image prior to convolution so that the valid convolution spans the image.
        voxel_grid, original_shape, original_offset = self._pad_image(voxel_grid, mode=mode, axis=axis)

        # Determine the filter output shape.
        filter_output_shape = [dim_size for current_axis, dim_size in enumerate(voxel_grid.shape) if
                               current_axis != axis]

        # Compute the fft of the filter, with output shape of the image.
        self._transform_filter(filter_shape=filter_output_shape)

        # Riesz transform the filter.
        self._riesz_transform()

        # Iterate over slices, compute fft, multiply with filter, and compute inverse fourier transform.
        voxel_grid = np.stack([self._convolve(voxel_grid=np.squeeze(current_grid, axis=axis))
                               for current_grid in np.split(voxel_grid, voxel_grid.shape[axis], axis=axis)],
                              axis=axis)

        return self._return_response(voxel_grid=voxel_grid,
                                     response=response,
                                     original_offset=original_offset,
                                     original_shape=original_shape)

    def _convolve(self,
                  voxel_grid: np.ndarray):

        # Compute FFT of the slice.
        f_voxel = fft.fft2(voxel_grid)

        if not self.transformed:
            raise ValueError("Filter should have been transformed to the Fourier domain.")

        # Multiply with the filter and return the inverse fourier transform of the hadamard product.
        return fft.ifft2(f_voxel * self.filter_set)


class FilterSet3D(FilterSet):

    def convolve(self,
                 voxel_grid: np.ndarray,
                 mode,
                 response):

        # Pad the image prior to convolution so that the valid convolution spans the image.
        voxel_grid, original_shape, original_offset = self._pad_image(voxel_grid, mode=mode)

        # Determine the filter output shape.
        filter_output_shape = [dim_size for current_axis, dim_size in enumerate(voxel_grid.shape)]

        # Compute the fft of the filter, with output shape of the image.
        self._transform_filter(filter_shape=filter_output_shape)

        # Riesz transform the filter.
        self._riesz_transform()

        # Iterate over slices, compute fft, multiply with filter, and compute inverse fourier transform.
        voxel_grid = self._convolve(voxel_grid)

        return self._return_response(voxel_grid=voxel_grid,
                                     response=response,
                                     original_offset=original_offset,
                                     original_shape=original_shape)

    def _convolve(self,
                  voxel_grid: np.ndarray):

        # Compute FFT of the slice
        f_voxel = fft.fftn(voxel_grid)

        if not self.transformed:
            raise ValueError("Filter should have been transformed to the Fourier domain.")

        # Multiply with the filter and return the inverse fourier transform of the hadamard product.
        return fft.ifftn(f_voxel * self.filter_set)
