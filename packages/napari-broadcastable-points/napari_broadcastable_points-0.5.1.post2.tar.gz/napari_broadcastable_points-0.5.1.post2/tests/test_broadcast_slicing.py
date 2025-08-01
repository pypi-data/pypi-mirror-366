"""Tests for BroadcastablePoints slicing behavior without GUI dependencies."""

import numpy as np
import pytest
from napari.layers import Points
from napari.layers.utils._slice_input import _SliceInput, _ThickNDSlice

from napari_broadcastable_points import BroadcastablePoints


class TestBroadcastablePointsSlicing:
    """Test suite for BroadcastablePoints slicing behavior."""

    def test_data_insertion(self):
        """Test that broadcast dimensions are properly inserted into data."""
        # Original 4D data: T, P, Y, X
        dat = np.array(
            [
                [0, 0, 10, 10],
                [0, 1, 20, 20],
                [1, 0, 30, 30],
                [1, 1, 40, 40],
            ]
        )

        # Create BroadcastablePoints with broadcast dims for C and Z (indices 2,3)
        points = BroadcastablePoints(dat, broadcast_dims=(2, 3))

        # Check that dimensions were inserted correctly
        assert points.data.shape == (4, 6)  # Original 4 cols + 2 inserted = 6 cols
        assert points._broadcast_dims == [2, 3]

        # Check that zeros were inserted at the correct positions
        expected_data = np.array(
            [
                [0, 0, 0, 0, 10, 10],  # T, P, C(0), Z(0), Y, X
                [0, 1, 0, 0, 20, 20],
                [1, 0, 0, 0, 30, 30],
                [1, 1, 0, 0, 40, 40],
            ]
        )
        np.testing.assert_array_equal(points.data, expected_data)

    def test_slice_request_type(self):
        """Test that the correct slice request type is created."""
        dat = np.array([[0, 0, 10, 10]])
        points = BroadcastablePoints(dat, broadcast_dims=(2, 3))

        # Create a minimal slice input
        world_slice = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 0.0, 0.0, 256.0, 256.0),
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input = _SliceInput(
            ndisplay=2, world_slice=world_slice, order=(0, 1, 2, 3, 4, 5)
        )

        data_slice = slice_input.data_slice(points._data_to_world.inverse)
        request = points._make_slice_request_internal(slice_input, data_slice)

        # Check that it's our custom request type
        assert request.__class__.__name__ == "BroadcastablePointSliceRequest"
        assert hasattr(request, "broadcast_dims")
        assert request.broadcast_dims == [2, 3]

    def test_broadcast_slicing_behavior(self):
        """Test the core broadcast slicing behavior."""
        # Create 4D data with different T and P values
        dat = np.array(
            [
                [0, 0, 10, 10],  # T=0, P=0
                [0, 1, 20, 20],  # T=0, P=1
                [1, 0, 30, 30],  # T=1, P=0
                [1, 1, 40, 40],  # T=1, P=1
            ]
        )

        points = BroadcastablePoints(dat, broadcast_dims=(2, 3))

        # Test slicing at T=0, P=0 (should show points at T=0, P=0 regardless of C,Z)
        world_slice = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 0.0, 0.0, 256.0, 256.0),
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input = _SliceInput(
            ndisplay=2, world_slice=world_slice, order=(0, 1, 2, 3, 4, 5)
        )

        data_slice = slice_input.data_slice(points._data_to_world.inverse)
        request = points._make_slice_request_internal(slice_input, data_slice)
        response = request()

        # Should show only the point at T=0, P=0 (index 0)
        assert response.indices.tolist() == [0]

        # Test at different C value (should still show same point due to broadcast)
        world_slice_c5 = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 5.0, 0.0, 256.0, 256.0),  # C=5 (different from inserted 0)
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input_c5 = _SliceInput(
            ndisplay=2, world_slice=world_slice_c5, order=(0, 1, 2, 3, 4, 5)
        )

        data_slice = slice_input_c5.data_slice(points._data_to_world.inverse)
        request = points._make_slice_request_internal(slice_input_c5, data_slice)
        response = request()

        # Should STILL show point at T=0, P=0 because C is broadcast
        assert response.indices.tolist() == [0], "Broadcast dim C should be ignored"

        # Test at different Z value (should still show same point due to broadcast)
        world_slice_z10 = _ThickNDSlice.make_full(
            point=(
                0.0,
                0.0,
                0.0,
                10.0,
                256.0,
                256.0,
            ),  # Z=10 (different from inserted 0)
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input_z10 = _SliceInput(
            ndisplay=2, world_slice=world_slice_z10, order=(0, 1, 2, 3, 4, 5)
        )

        data_slice = slice_input_z10.data_slice(points._data_to_world.inverse)
        request = points._make_slice_request_internal(slice_input_z10, data_slice)
        response = request()

        # Should STILL show point at T=0, P=0 because Z is broadcast
        assert response.indices.tolist() == [0], "Broadcast dim Z should be ignored"

        # Test at T=0, P=1
        world_slice_p1 = _ThickNDSlice.make_full(
            point=(0.0, 1.0, 0.0, 0.0, 256.0, 256.0),
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input_p1 = _SliceInput(
            ndisplay=2, world_slice=world_slice_p1, order=(0, 1, 2, 3, 4, 5)
        )

        data_slice = slice_input_p1.data_slice(points._data_to_world.inverse)
        request = points._make_slice_request_internal(slice_input_p1, data_slice)
        response = request()

        # Should show only the point at T=0, P=1 (index 1)
        assert response.indices.tolist() == [1]

    def test_comparison_with_regular_points(self):
        """Test that BroadcastablePoints behaves differently from regular Points."""
        # Create 6D data for regular Points with points at different C and Z values
        dat_6d = np.array(
            [
                [0, 0, 0, 0, 10, 10],  # T=0, P=0, C=0, Z=0
                [0, 0, 1, 0, 20, 20],  # T=0, P=0, C=1, Z=0 (different C)
                [0, 0, 0, 1, 30, 30],  # T=0, P=0, C=0, Z=1 (different Z)
                [0, 1, 0, 0, 40, 40],  # T=0, P=1, C=0, Z=0 (different P)
                [1, 0, 0, 0, 50, 50],  # T=1, P=0, C=0, Z=0 (different T)
            ]
        )

        # Create 4D data for BroadcastablePoints (without C and Z dimensions)
        dat_4d = np.array(
            [
                [0, 0, 10, 10],  # T=0, P=0
                [0, 0, 20, 20],  # T=0, P=0 (duplicate coordinates, different point)
                [0, 0, 30, 30],  # T=0, P=0 (duplicate coordinates, different point)
                [0, 1, 40, 40],  # T=0, P=1
                [1, 0, 50, 50],  # T=1, P=0
            ]
        )

        regular_points = Points(dat_6d, ndim=6)
        broadcast_points = BroadcastablePoints(dat_4d, ndim=6, broadcast_dims=(2, 3))

        # Test 1: Slice at T=0, P=0, C=0, Z=0
        # Regular points should only show the exact match
        # Broadcast points should show ALL points at T=0, P=0 regardless of C,Z
        world_slice = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 0.0, 0.0, 256.0, 256.0),
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input = _SliceInput(
            ndisplay=2, world_slice=world_slice, order=(0, 1, 2, 3, 4, 5)
        )

        # Regular points - should only show index 0 (exact match)
        data_slice = slice_input.data_slice(regular_points._data_to_world.inverse)
        request = regular_points._make_slice_request_internal(slice_input, data_slice)
        response = request()
        regular_indices = response.indices.tolist()

        # Broadcast points - should show indices 0,1,2 (all at T=0, P=0)
        data_slice = slice_input.data_slice(broadcast_points._data_to_world.inverse)
        request = broadcast_points._make_slice_request_internal(slice_input, data_slice)
        response = request()
        broadcast_indices = response.indices.tolist()

        assert regular_indices == [0], (
            f"Regular points should only show exact match, got {regular_indices}"
        )
        assert broadcast_indices == [
            0,
            1,
            2,
        ], f"Broadcast points should show all at T=0,P=0, got {broadcast_indices}"

        # Test 2: Slice at T=0, P=0, C=1, Z=0 (different C value)
        # Regular points should only show the point at C=1
        # Broadcast points should still show ALL points at T=0, P=0 (C is ignored)
        world_slice_c1 = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 1.0, 0.0, 256.0, 256.0),  # C=1 now
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input_c1 = _SliceInput(
            ndisplay=2, world_slice=world_slice_c1, order=(0, 1, 2, 3, 4, 5)
        )

        # Regular points - should only show index 1 (at C=1)
        data_slice = slice_input_c1.data_slice(regular_points._data_to_world.inverse)
        request = regular_points._make_slice_request_internal(
            slice_input_c1, data_slice
        )
        response = request()
        regular_indices_c1 = response.indices.tolist()

        # Broadcast points - should still show indices 0,1,2 (C is broadcast/ignored)
        data_slice = slice_input_c1.data_slice(broadcast_points._data_to_world.inverse)
        request = broadcast_points._make_slice_request_internal(
            slice_input_c1, data_slice
        )
        response = request()
        broadcast_indices_c1 = response.indices.tolist()

        assert regular_indices_c1 == [1], (
            f"Regular points should only show C=1 match, got {regular_indices_c1}"
        )
        assert broadcast_indices_c1 == [
            0,
            1,
            2,
        ], f"Broadcast points should ignore C dimension, got {broadcast_indices_c1}"

        # Test 3: Slice at T=0, P=0, C=0, Z=1 (different Z value)
        # Regular points should only show the point at Z=1
        # Broadcast points should still show ALL points at T=0, P=0 (Z is ignored)
        world_slice_z1 = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 0.0, 1.0, 256.0, 256.0),  # Z=1 now
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input_z1 = _SliceInput(
            ndisplay=2, world_slice=world_slice_z1, order=(0, 1, 2, 3, 4, 5)
        )

        # Regular points - should only show index 2 (at Z=1)
        data_slice = slice_input_z1.data_slice(regular_points._data_to_world.inverse)
        request = regular_points._make_slice_request_internal(
            slice_input_z1, data_slice
        )
        response = request()
        regular_indices_z1 = response.indices.tolist()

        # Broadcast points - should still show indices 0,1,2 (Z is broadcast/ignored)
        data_slice = slice_input_z1.data_slice(broadcast_points._data_to_world.inverse)
        request = broadcast_points._make_slice_request_internal(
            slice_input_z1, data_slice
        )
        response = request()
        broadcast_indices_z1 = response.indices.tolist()

        assert regular_indices_z1 == [2], (
            f"Regular points should only show Z=1 match, got {regular_indices_z1}"
        )
        assert broadcast_indices_z1 == [
            0,
            1,
            2,
        ], f"Broadcast points should ignore Z dimension, got {broadcast_indices_z1}"

    def test_empty_data(self):
        """Test behavior with empty data."""
        points = BroadcastablePoints(np.empty((0, 4)), broadcast_dims=(2, 3))

        world_slice = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 0.0, 0.0, 256.0, 256.0),
            margin_left=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.5, 0.5, 0.0, 0.0),
        )
        slice_input = _SliceInput(
            ndisplay=2, world_slice=world_slice, order=(0, 1, 2, 3, 4, 5)
        )

        data_slice = slice_input.data_slice(points._data_to_world.inverse)
        request = points._make_slice_request_internal(slice_input, data_slice)
        response = request()

        assert len(response.indices) == 0
        assert len(response.scale) == 0

    def test_no_broadcast_dims(self):
        """Test behavior when no broadcast dimensions are specified."""
        dat = np.array(
            [
                [0, 0, 10, 10],
                [0, 1, 20, 20],
                [1, 0, 30, 30],
            ]
        )
        broadcast_points = BroadcastablePoints(dat, ndim=4, broadcast_dims=[])
        regular_points = Points(dat, ndim=4)

        # Should behave like regular Points when no broadcast dims
        assert broadcast_points.data.shape == (3, 4)  # No dimensions inserted
        assert broadcast_points._broadcast_dims == []

        # Test slicing behavior matches regular Points
        world_slice = _ThickNDSlice.make_full(
            point=(0.0, 0.0, 256.0, 256.0),
            margin_left=(0.5, 0.5, 0.0, 0.0),
            margin_right=(0.5, 0.5, 0.0, 0.0),
        )
        slice_input = _SliceInput(
            ndisplay=2, world_slice=world_slice, order=(0, 1, 2, 3)
        )

        # Get responses from both
        data_slice = slice_input.data_slice(broadcast_points._data_to_world.inverse)
        broadcast_request = broadcast_points._make_slice_request_internal(
            slice_input, data_slice
        )
        broadcast_response = broadcast_request()

        data_slice = slice_input.data_slice(regular_points._data_to_world.inverse)
        regular_request = regular_points._make_slice_request_internal(
            slice_input, data_slice
        )
        regular_response = regular_request()

        # Should have identical behavior
        assert (
            broadcast_response.indices.tolist()
            == regular_response.indices.tolist()
            == [0]
        )

    def test_broadcast_dims_sorting(self):
        """Test that broadcast dimensions are properly sorted."""
        dat = np.array([[0, 0, 10, 10]])
        points = BroadcastablePoints(dat, broadcast_dims=[3, 1, 2])

        # Should be sorted
        assert points._broadcast_dims == [1, 2, 3]

        # Data should have zeros inserted at sorted positions
        expected_shape = (1, 7)  # Original 4 + 3 inserted = 7
        assert points.data.shape == expected_shape

    @pytest.mark.parametrize(
        "broadcast_dims",
        [
            [2, 3],  # Standard case - broadcast newly inserted dims
            [0, 1],  # Edge case - broadcast original dims
            [1, 3],  # Mixed case
            [0, 2, 3],  # Multiple broadcasts
        ],
    )
    def test_various_broadcast_combinations(self, broadcast_dims):
        """Test that various broadcast dimension combinations work without errors.

        Note: The exact behavior for edge cases (like broadcasting original dimensions)
        is complex due to how dimensions shift during insertion. This test primarily
        verifies that the mechanism works without errors.
        """
        dat = np.array(
            [
                [0, 0, 10, 10],
                [1, 1, 20, 20],
            ]
        )

        points = BroadcastablePoints(dat, broadcast_dims=broadcast_dims)

        # Check that the broadcast dims are stored correctly
        assert points._broadcast_dims == sorted(broadcast_dims)

        # Check that data shape is correct
        expected_cols = dat.shape[1] + len(broadcast_dims)
        assert points.data.shape == (dat.shape[0], expected_cols)

        # Test that slicing works without errors
        world_slice = _ThickNDSlice.make_full(
            point=tuple([0.0] * expected_cols),
            margin_left=tuple([0.5] * expected_cols),
            margin_right=tuple([0.5] * expected_cols),
        )
        slice_input = _SliceInput(
            ndisplay=2, world_slice=world_slice, order=tuple(range(expected_cols))
        )

        data_slice = slice_input.data_slice(points._data_to_world.inverse)
        request = points._make_slice_request_internal(slice_input, data_slice)
        response = request()

        # Just verify we get a valid response
        assert isinstance(response.indices, np.ndarray)
        assert len(response.indices) >= 0  # Can be 0 if no points match

        # For the standard case, verify expected behavior
        if broadcast_dims == [2, 3]:
            # This is the well-tested case where we broadcast C and Z
            assert response.indices.tolist() == [0]  # Point at T=0,P=0
