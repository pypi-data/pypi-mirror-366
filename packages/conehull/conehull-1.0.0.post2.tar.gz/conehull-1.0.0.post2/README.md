# 2D Conehull

This package uses the quickhull algorithm to find the convex hull of a point set,
but with the added option of restricting the set of halfplanes we intersect over to only those with normals lying in a given convex cone.

## Features

- **Cone-Constrained Hull**: The cone feature computes the intersection of halfplanes whose outward normals lie between two specified direction vectors. This creates a larger (unbounded) region that contains the original convex hull.
- **Visualizations**: View a step-by-step visualization of the algorithm.
- **Samplers**: For convenience we include simple ways of creating point sets, by inputting either an implicit (in)equality or a parametrization.

## Basic Usage

```python
import numpy as np

# Make conehull accessible
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))

from conehull import conehull
from conehull.view import plot_hull

points = np.array([
    [ 3.0, -4.0],
    [-1.0,  0.0],
    [ 3.0,  5.0],
    [ 4.5,  1.0],
    [-6.0, -2.0],
    [ 0.0,  4.0],
    [ 5.0,  2.0],
    [-2.0, -5.0],
    [ 1.0,  2.0],
    [ 2.0,  6.0],
    [-5.5,  1.5],
    [ 6.0, -1.0],
    [-3.0,  7.0],
    [ 3.0,  0.0],
    [ 2.0, -2.5],
    [ 4.0,  0.0],
    [-7.0,  3.0],
    [-4.0, -0.5],
])
cone = np.array([[1, 0], [0, 1]])

cone_hull = conehull(points, cone=cone)

# plot_hull is just a convenience wrapper around pyplot
plot_hull(cone_hull, points, cone=cone, show_convex_hull=True, 
                title="Cone hull with standard convex hull comparison")
```
![](img/conehull_comparison.jpg)


## Visualization Modes

```python
# Import visualization functions
from conehull.view import (
    conehull_animated,
    conehull_step_by_step, 
    conehull_jupyter,
    plot_hull
)

# 1. Animated visualization - auto-playing GIF/video
# Creates a smooth animation showing algorithm steps
conehull_animated(points, cone=cone, save_path="animation.gif", interval=800)

# 2. Step-by-step interactive viewer - returns navigation functions
# Best for understanding algorithm mechanics step by step
hull, frames, show_frame = conehull_step_by_step(points, cone=cone)

# Use the returned show_frame function to navigate:
show_frame(0)    # Show first step
show_frame(5)    # Jump to step 5
show_frame(-1)   # Show final result

# 3. Jupyter widget - interactive controls in notebooks
# Returns a widget object with navigation buttons and sliders
if 'ipywidgets' in globals():  # Only works in Jupyter
    viewer = conehull_jupyter(points, cone=cone)
    viewer.show()  # Display the interactive widget

# 4. Static hull plot - simple visualization with comparison option
plot_hull(hull=cone_hull, points=points, cone=cone, 
          show_convex_hull=True, save_path="comparison.png")
```


## Configurable Bounding Box

Since the hull is unbounded for any nontrivial cone, we use a bounding box.
The `cone_bounds` parameter controls how the unbounded cone hull is clipped:

```python
# Default: margin = 2.0 times data range
cone_hull = conehull(points, cone=cone)

# Custom margin multiplier
cone_hull = conehull(points, cone=cone, cone_bounds=5.0)

# Explicit bounds: [x_min, x_max, y_min, y_max]
cone_hull = conehull(points, cone=cone, cone_bounds=[-10, 10, -10, 10])

# Alternative format: [[x_min, y_min], [x_max, y_max]]
cone_hull = conehull(points, cone=cone, cone_bounds=[[-10, -10], [10, 10]])
```


## Files
- `_geometry.py` - Basic geometric operations like point-to-line distances and determining which side of a line points are on. Also handles sorting hull points in counterclockwise order.
- `_conehull.py` - Implements the QuickHull algorithm for both standard and cone-constrained convex hulls. Contains the main `conehull()` function and recursive hull construction logic.
- `_cone_intersection.py` - Transforms standard convex hulls into cone hulls by filtering halfplanes based on cone constraints. Computes intersections within configurable bounding boxes.
- `view.py` - Visualization tools including step-by-step animations, interactive Jupyter widgets, and static plotting. Supports both automated playback and manual navigation of algorithm steps.
- `sampler.py` - Generates test point datasets from mathematical functions. Supports parametric curves, implicit equations, and region sampling for creating diverse test cases.
