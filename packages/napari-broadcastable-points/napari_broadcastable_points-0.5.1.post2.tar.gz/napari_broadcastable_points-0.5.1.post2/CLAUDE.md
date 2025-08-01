# napari-broadcastable-points Development Guide

## Project Overview

This project extends napari's Points layer to support "broadcast dimensions" - dimensions that are ignored during slicing, making points visible across all values in those dimensions. This is useful for overlaying points across multiple channels, z-slices, or other dimensions in multi-dimensional image data.

### Key Concepts

1. **Broadcast Dimensions**: Dimensions specified in `broadcast_dims` parameter are ignored during slicing operations
2. **Data Structure**: When creating a BroadcastablePoints layer, zeros are inserted at broadcast dimension positions
3. **Example**: If you have 4D data [T, P, Y, X] and specify `broadcast_dims=(2, 3)`, the data becomes 6D with structure [T, P, C=0, Z=0, Y, X]

## Architecture

### Core Implementation (`napari_broadcastable_points/_points.py`)

1. **BroadcastablePoints class**: Extends napari's Points layer
   - Inserts columns of zeros at broadcast dimension positions during initialization
   - Overrides `_make_slice_request_internal()` to return custom slice request

2. **BroadcastablePointSliceRequest class**: Custom slice request that handles broadcast logic
   - Extends napari's `_PointSliceRequest`
   - In `__call__()`, removes broadcast dimensions from `not_displayed` list before slicing
   - This causes napari to ignore those dimensions when determining point visibility

### How It Works

1. User creates points with `broadcast_dims` parameter
2. Constructor inserts zero-filled columns at specified positions
3. During slicing, custom slice request removes broadcast dims from filtering
4. Points remain visible regardless of slice position in broadcast dimensions

## Compatibility Notes

### napari Version Support
- Originally built for napari 0.5.0
- Updated to work with napari >=0.6.0
- No backwards compatibility maintained (only supports latest napari)

### Key Changes Between Versions
- napari's internal structure moved from `napari/layers/` to `src/napari/layers/`
- Core slicing API remained stable between 0.5.0 and 0.6.x
- Implementation now imports directly from napari instead of copying internal files

## Python Dependency Management

This project uses `uv` for Python dependency management. Always use `uv` to manage dependencies:

```bash
# Sync dependencies (preferred)
uv sync

# Run scripts
uv run python script.py

# Add new dependencies
uv add package_name

# For development dependencies
uv add --dev package_name
```

Note: Use `uv sync` instead of `uv pip install` when possible.

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_broadcast_slicing.py

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_broadcast_slicing.py::TestBroadcastablePointsSlicing::test_data_insertion
```

### Test Coverage

The test suite (`tests/test_broadcast_slicing.py`) includes:
- **test_data_insertion**: Verifies broadcast dims are inserted correctly
- **test_slice_request_type**: Checks custom slice request is used
- **test_broadcast_slicing_behavior**: Tests core broadcast functionality
- **test_comparison_with_regular_points**: Demonstrates difference from regular Points
- **test_empty_data**: Edge case handling
- **test_no_broadcast_dims**: Behavior when no broadcast dims specified
- **test_broadcast_dims_sorting**: Verifies dims are sorted properly
- **test_various_broadcast_combinations**: Tests different broadcast dim combinations

### Key Testing Insight

The most important test is `test_comparison_with_regular_points` which shows:
- Regular Points: Only shows points matching ALL dimensions exactly
- BroadcastablePoints: Shows all points matching non-broadcast dimensions, ignoring broadcast dims

## Common Tasks

### Testing GUI Functionality

```python
# user_test.py example
import napari
from napari_broadcastable_points import BroadcastablePoints
import numpy as np

v = napari.Viewer()

# Create multi-dimensional image
T, P, C, Z, Y, X = 5, 4, 3, 2, 512, 512
images = np.zeros([T, P, C, Z, Y, X])
v.add_image(images)

# Add points that broadcast over C and Z dimensions
dat = np.array([
    [0, 0, 10, 10],  # T=0, P=0, Y=10, X=10
    [0, 1, 20, 20],  # T=0, P=1, Y=20, X=20
])

points = BroadcastablePoints(dat, broadcast_dims=(2, 3))
v.add_layer(points)
napari.run()
```

### Debugging Slicing Behavior

To understand how slicing works, check:
1. What dimensions are in `not_displayed`
2. Which dimensions get removed by broadcast logic
3. What points match the remaining filter criteria

## Important Edge Cases

1. **Broadcast Original Dimensions**: When broadcast_dims includes original column indices (e.g., [0,1] for T,P), the behavior is complex due to column shifting during insertion
2. **Empty Data**: Handled gracefully, returns empty indices
3. **No Broadcast Dims**: Behaves identically to regular Points layer

## Future Considerations

1. The current implementation assumes broadcast dimensions will be "extra" dimensions (like C, Z) rather than core data dimensions
2. Broadcasting original data dimensions (T, P, Y, X) is possible but the semantics are less clear
3. The implementation could be enhanced to better handle dimension mapping after insertion
