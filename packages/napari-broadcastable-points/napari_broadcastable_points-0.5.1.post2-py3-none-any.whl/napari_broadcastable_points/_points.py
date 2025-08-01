from __future__ import annotations

from typing import TYPE_CHECKING, List

import numpy as np
from napari.layers import Points
from napari.layers.points._slice import _PointSliceRequest, _PointSliceResponse
from napari.layers.utils._slice_input import _ThickNDSlice

if TYPE_CHECKING:
    from napari.layers.utils._slice_input import _SliceInput

__all__ = [
    "BroadcastablePoints",
]


class BroadcastablePointSliceRequest(_PointSliceRequest):
    """Extended _PointSliceRequest that handles broadcast dimensions."""

    def __init__(self, broadcast_dims, **kwargs):
        self.broadcast_dims = broadcast_dims
        # Pass all other arguments to parent
        super().__init__(**kwargs)

    def __call__(self) -> _PointSliceResponse:
        # Return early if no data
        if len(self.data) == 0:
            return _PointSliceResponse(
                indices=np.array([], dtype=int),
                scale=np.empty(0),
                slice_input=self.slice_input,
                request_id=self.id,
            )

        not_disp = list(self.slice_input.not_displayed)

        # Remove broadcast dimensions from not_displayed
        for dim in self.broadcast_dims:
            if dim in not_disp:
                not_disp.remove(dim)

        if not not_disp:
            # If we want to display everything, then use all indices.
            return _PointSliceResponse(
                indices=np.arange(len(self.data), dtype=int),
                scale=1,
                slice_input=self.slice_input,
                request_id=self.id,
            )

        # Call parent's _get_slice_data with modified not_disp
        slice_indices, scale = self._get_slice_data(not_disp)

        return _PointSliceResponse(
            indices=slice_indices,
            scale=scale,
            slice_input=self.slice_input,
            request_id=self.id,
        )


class BroadcastablePoints(Points):
    def __init__(
        self, data=None, *, ndim=None, broadcast_dims: List[int] = None, **kwargs
    ):
        """
        Parameters
        ----------
        data :
        """
        if broadcast_dims is None:
            broadcast_dims = []
        # sort to ensure the for loop works correctly
        self._broadcast_dims = sorted(broadcast_dims)
        if data is not None:
            for b in broadcast_dims:
                # need to loop so because doing all at once means that larger
                # values for dim will be placed in the wrong spot
                # data = np.insert(data, b, -np.ones(data.shape[0]), axis=1)
                data = np.insert(data, b, 0, axis=1)

        super().__init__(data, ndim=ndim, **kwargs)

    def last_displayed(self) -> np.ndarray:
        """
        Return the XY coordinates of the most recently displayed points

        Returns
        -------
        data : (N, 2)
            The xy coordinates of the most recently displayed points.
        """
        return self._view_data

    def _make_slice_request_internal(
        self, slice_input: _SliceInput, data_slice: _ThickNDSlice
    ) -> _PointSliceRequest:
        # Create a custom _PointSliceRequest that includes broadcast_dims
        return BroadcastablePointSliceRequest(
            broadcast_dims=self._broadcast_dims,
            slice_input=slice_input,
            data=self.data,
            data_slice=data_slice,
            projection_mode=self.projection_mode,
            out_of_slice_display=self.out_of_slice_display,
            size=self.size,
        )
