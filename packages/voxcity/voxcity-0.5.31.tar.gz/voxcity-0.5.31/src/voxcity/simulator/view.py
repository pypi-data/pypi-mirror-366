"""Functions for computing and visualizing various view indices in a voxel city model.

This module provides functionality to compute and visualize:
- Green View Index (GVI): Measures visibility of green elements like trees and vegetation
- Sky View Index (SVI): Measures visibility of open sky from street level 
- Sky View Factor (SVF): Measures the ratio of visible sky hemisphere to total hemisphere
- Landmark Visibility: Measures visibility of specified landmark buildings from different locations

The module uses optimized ray tracing techniques with Numba JIT compilation for efficient computation.
Key features:
- Generic ray tracing framework that can be customized for different view indices
- Parallel processing for fast computation of view maps
- Tree transmittance modeling using Beer-Lambert law
- Visualization tools including matplotlib plots and OBJ exports
- Support for both inclusion and exclusion based visibility checks

The module provides several key functions:
- trace_ray_generic(): Core ray tracing function that handles tree transmittance
- compute_vi_generic(): Computes view indices by casting rays in specified directions
- compute_vi_map_generic(): Generates 2D maps of view indices
- get_view_index(): High-level function to compute various view indices
- compute_landmark_visibility(): Computes visibility of landmark buildings
- get_sky_view_factor_map(): Computes sky view factor maps

The module uses a voxel-based representation where:
- Empty space is represented by 0
- Trees are represented by -2 
- Buildings are represented by -3
- Other values can be used for different features

Tree transmittance is modeled using the Beer-Lambert law with configurable parameters:
- tree_k: Static extinction coefficient (default 0.6)
- tree_lad: Leaf area density in m^-1 (default 1.0)

Additional implementation details:
- Uses DDA (Digital Differential Analyzer) algorithm for efficient ray traversal
- Handles edge cases like zero-length rays and division by zero
- Supports early exit optimizations for performance
- Provides flexible observer placement rules
- Includes comprehensive error checking and validation
- Allows customization of visualization parameters
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from numba import njit, prange
import time
import trimesh

from ..geoprocessor.polygon import find_building_containing_point, get_buildings_in_drawn_polygon
from ..geoprocessor.mesh import create_voxel_mesh
from ..exporter.obj import grid_to_obj, export_obj

@njit
def calculate_transmittance(length, tree_k=0.6, tree_lad=1.0):
    """Calculate tree transmittance using the Beer-Lambert law.
    
    Uses the Beer-Lambert law to model light attenuation through tree canopy:
    transmittance = exp(-k * LAD * L)
    where:
    - k is the extinction coefficient
    - LAD is the leaf area density
    - L is the path length through the canopy
    
    Args:
        length (float): Path length through tree voxel in meters
        tree_k (float): Static extinction coefficient (default: 0.6)
            Controls overall light attenuation strength
        tree_lad (float): Leaf area density in m^-1 (default: 1.0)
            Higher values = denser foliage = more attenuation
    
    Returns:
        float: Transmittance value between 0 and 1
            1.0 = fully transparent
            0.0 = fully opaque
    """
    return np.exp(-tree_k * tree_lad * length)

@njit
def trace_ray_generic(voxel_data, origin, direction, hit_values, meshsize, tree_k, tree_lad, inclusion_mode=True):
    """Trace a ray through a voxel grid and check for hits with specified values.
    
    Uses DDA algorithm to efficiently traverse voxels along ray path.
    Handles tree transmittance using Beer-Lambert law.
    
    The DDA algorithm:
    1. Initializes ray at origin voxel
    2. Calculates distances to next voxel boundaries in each direction
    3. Steps to next voxel by choosing smallest distance
    4. Repeats until hit or out of bounds
    
    Tree transmittance:
    - When ray passes through tree voxels (-2), transmittance is accumulated
    - Uses Beer-Lambert law with configurable extinction coefficient and leaf area density
    - Ray is considered blocked if cumulative transmittance falls below 0.01
    
    Args:
        voxel_data (ndarray): 3D array of voxel values
        origin (ndarray): Starting point (x,y,z) of ray in voxel coordinates
        direction (ndarray): Direction vector of ray (will be normalized)
        hit_values (tuple): Values to check for hits
        meshsize (float): Size of each voxel in meters
        tree_k (float): Tree extinction coefficient
        tree_lad (float): Leaf area density in m^-1
        inclusion_mode (bool): If True, hit_values are hits. If False, hit_values are allowed values.
    
    Returns:
        tuple: (hit_detected, transmittance_value)
            hit_detected (bool): Whether ray hit a target voxel
            transmittance_value (float): Cumulative transmittance through trees
    """
    nx, ny, nz = voxel_data.shape
    x0, y0, z0 = origin
    dx, dy, dz = direction

    # Normalize direction vector to ensure consistent step sizes
    length = np.sqrt(dx*dx + dy*dy + dz*dz)
    if length == 0.0:
        return False, 1.0
    dx /= length
    dy /= length
    dz /= length

    # Initialize ray position at center of starting voxel
    x, y, z = x0 + 0.5, y0 + 0.5, z0 + 0.5
    i, j, k = int(x0), int(y0), int(z0)

    # Determine step direction for each axis (-1 or +1)
    step_x = 1 if dx >= 0 else -1
    step_y = 1 if dy >= 0 else -1
    step_z = 1 if dz >= 0 else -1

    # Calculate DDA parameters with safety checks to prevent division by zero
    EPSILON = 1e-10  # Small value to prevent division by zero
    
    # Calculate distances to next voxel boundaries and step sizes for X-axis
    if abs(dx) > EPSILON:
        t_max_x = ((i + (step_x > 0)) - x) / dx
        t_delta_x = abs(1 / dx)
    else:
        t_max_x = np.inf
        t_delta_x = np.inf

    # Calculate distances to next voxel boundaries and step sizes for Y-axis
    if abs(dy) > EPSILON:
        t_max_y = ((j + (step_y > 0)) - y) / dy
        t_delta_y = abs(1 / dy)
    else:
        t_max_y = np.inf
        t_delta_y = np.inf

    # Calculate distances to next voxel boundaries and step sizes for Z-axis
    if abs(dz) > EPSILON:
        t_max_z = ((k + (step_z > 0)) - z) / dz
        t_delta_z = abs(1 / dz)
    else:
        t_max_z = np.inf
        t_delta_z = np.inf

    # Track cumulative values for tree transmittance calculation
    cumulative_transmittance = 1.0
    cumulative_hit_contribution = 0.0
    last_t = 0.0

    # Main ray traversal loop using DDA algorithm
    while (0 <= i < nx) and (0 <= j < ny) and (0 <= k < nz):
        voxel_value = voxel_data[i, j, k]
        
        # Find next intersection point along the ray
        t_next = min(t_max_x, t_max_y, t_max_z)
        
        # Calculate segment length in current voxel (in real world units)
        segment_length = (t_next - last_t) * meshsize
        segment_length = max(0.0, segment_length) 
        
        # Handle tree voxels (value -2) with Beer-Lambert law transmittance
        if voxel_value == -2:
            transmittance = calculate_transmittance(segment_length, tree_k, tree_lad)
            cumulative_transmittance *= transmittance

            # If transmittance becomes too low, consider the ray blocked
            if cumulative_transmittance < 0.01:
                return True, cumulative_transmittance

        # Check for hits with target objects based on inclusion/exclusion mode
        if inclusion_mode:
            # Inclusion mode: hit if voxel value is in the target set
            for hv in hit_values:
                if voxel_value == hv:
                    return True, cumulative_transmittance
        else:
            # Exclusion mode: hit if voxel value is NOT in the allowed set
            in_set = False
            for hv in hit_values:
                if voxel_value == hv:
                    in_set = True
                    break
            if not in_set and voxel_value != -2:  # Exclude trees from regular hits
                return True, cumulative_transmittance

        # Update for next iteration
        last_t = t_next
        
        # Move to next voxel using DDA step logic
        if t_max_x < t_max_y:
            if t_max_x < t_max_z:
                # Step in X direction
                t_max_x += t_delta_x
                i += step_x
            else:
                # Step in Z direction
                t_max_z += t_delta_z
                k += step_z
        else:
            if t_max_y < t_max_z:
                # Step in Y direction
                t_max_y += t_delta_y
                j += step_y
            else:
                # Step in Z direction
                t_max_z += t_delta_z
                k += step_z

    # Ray exited the grid without hitting a target
    return False, cumulative_transmittance

@njit
def compute_vi_generic(observer_location, voxel_data, ray_directions, hit_values, meshsize, tree_k, tree_lad, inclusion_mode=True):
    """Compute view index accounting for tree transmittance.
    
    Casts rays in specified directions and computes visibility index based on hits and transmittance.
    The view index is the ratio of visible rays to total rays cast, where:
    - For inclusion mode: Counts hits with target values
    - For exclusion mode: Counts rays that don't hit obstacles
    Tree transmittance is handled specially:
    - In inclusion mode with trees as targets: Uses (1 - transmittance) as contribution
    - In exclusion mode: Uses transmittance value directly
    
    Args:
        observer_location (ndarray): Observer position (x,y,z) in voxel coordinates
        voxel_data (ndarray): 3D array of voxel values
        ray_directions (ndarray): Array of direction vectors for rays
        hit_values (tuple): Values to check for hits
        meshsize (float): Size of each voxel in meters
        tree_k (float): Tree extinction coefficient
        tree_lad (float): Leaf area density in m^-1
        inclusion_mode (bool): If True, hit_values are hits. If False, hit_values are allowed values.
    
    Returns:
        float: View index value between 0 and 1
            0.0 = no visibility in any direction
            1.0 = full visibility in all directions
    """
    total_rays = ray_directions.shape[0]
    visibility_sum = 0.0

    # Cast rays in all specified directions
    for idx in range(total_rays):
        direction = ray_directions[idx]
        hit, value = trace_ray_generic(voxel_data, observer_location, direction, 
                                     hit_values, meshsize, tree_k, tree_lad, inclusion_mode)
        
        # Accumulate visibility contributions based on mode
        if inclusion_mode:
            if hit:
                # For trees in hit_values, use partial visibility based on transmittance
                if -2 in hit_values:
                    # Use the hit contribution (1 - transmittance) for tree visibility
                    visibility_sum += value if value < 1.0 else 1.0
                else:
                    # Full visibility for non-tree targets
                    visibility_sum += 1.0
        else:
            if not hit:
                # For exclusion mode, use transmittance value directly as visibility
                visibility_sum += value

    # Return average visibility across all rays
    return visibility_sum / total_rays

@njit(parallel=True)
def compute_vi_map_generic(voxel_data, ray_directions, view_height_voxel, hit_values, 
                          meshsize, tree_k, tree_lad, inclusion_mode=True):
    """Compute view index map incorporating tree transmittance.
    
    Places observers at valid locations and computes view index for each position.
    Valid observer locations are:
    - Empty voxels (0) or tree voxels (-2)
    - Above non-empty, non-tree voxels
    - Not above water (7,8,9) or negative values
    
    The function processes each x,y position in parallel for efficiency.
    
    Args:
        voxel_data (ndarray): 3D array of voxel values
        ray_directions (ndarray): Array of direction vectors for rays
        view_height_voxel (int): Observer height in voxel units
        hit_values (tuple): Values to check for hits
        meshsize (float): Size of each voxel in meters
        tree_k (float): Tree extinction coefficient
        tree_lad (float): Leaf area density in m^-1
        inclusion_mode (bool): If True, hit_values are hits. If False, hit_values are allowed values.
    
    Returns:
        ndarray: 2D array of view index values
            NaN = invalid observer location
            0.0-1.0 = view index value
    """
    nx, ny, nz = voxel_data.shape
    vi_map = np.full((nx, ny), np.nan)

    # Process each horizontal position in parallel for efficiency
    for x in prange(nx):
        for y in range(ny):
            found_observer = False
            # Search from bottom to top for valid observer placement
            for z in range(1, nz):
                # Check for valid observer location: empty space above solid ground
                if voxel_data[x, y, z] in (0, -2) and voxel_data[x, y, z - 1] not in (0, -2):
                    # Skip invalid ground types (water or negative values)
                    if (voxel_data[x, y, z - 1] in (7, 8, 9)) or (voxel_data[x, y, z - 1] < 0):
                        vi_map[x, y] = np.nan
                        found_observer = True
                        break
                    else:
                        # Place observer at specified height above ground level
                        observer_location = np.array([x, y, z + view_height_voxel], dtype=np.float64)
                        # Compute view index for this location
                        vi_value = compute_vi_generic(observer_location, voxel_data, ray_directions, 
                                                    hit_values, meshsize, tree_k, tree_lad, inclusion_mode)
                        vi_map[x, y] = vi_value
                        found_observer = True
                        break
            # Mark locations where no valid observer position was found
            if not found_observer:
                vi_map[x, y] = np.nan

    # Flip vertically to match display orientation
    return np.flipud(vi_map)

def get_view_index(voxel_data, meshsize, mode=None, hit_values=None, inclusion_mode=True, **kwargs):
    """Calculate and visualize a generic view index for a voxel city model.

    This is a high-level function that provides a flexible interface for computing
    various view indices. It handles:
    - Mode presets for common indices (green, sky)
    - Ray direction generation
    - Tree transmittance parameters
    - Visualization
    - Optional OBJ export

    Args:
        voxel_data (ndarray): 3D array of voxel values.
        meshsize (float): Size of each voxel in meters.
        mode (str): Predefined mode. Options: 'green', 'sky', or None.
            If 'green': GVI mode - measures visibility of vegetation
            If 'sky': SVI mode - measures visibility of open sky
            If None: Custom mode requiring hit_values parameter
        hit_values (tuple): Voxel values considered as hits (if inclusion_mode=True)
                            or allowed values (if inclusion_mode=False), if mode is None.
        inclusion_mode (bool): 
            True = voxel_value in hit_values is success.
            False = voxel_value not in hit_values is success.
        **kwargs: Additional arguments:
            - view_point_height (float): Observer height in meters (default: 1.5)
            - colormap (str): Matplotlib colormap name (default: 'viridis')
            - obj_export (bool): Export as OBJ (default: False)
            - output_directory (str): Directory for OBJ output
            - output_file_name (str): Base filename for OBJ output
            - num_colors (int): Number of discrete colors for OBJ export
            - alpha (float): Transparency value for OBJ export
            - vmin (float): Minimum value for color mapping
            - vmax (float): Maximum value for color mapping
            - N_azimuth (int): Number of azimuth angles for ray directions
            - N_elevation (int): Number of elevation angles for ray directions
            - elevation_min_degrees (float): Minimum elevation angle in degrees
            - elevation_max_degrees (float): Maximum elevation angle in degrees
            - tree_k (float): Tree extinction coefficient (default: 0.5)
            - tree_lad (float): Leaf area density in m^-1 (default: 1.0)

    Returns:
        ndarray: 2D array of computed view index values.
    """
    # Handle predefined mode presets for common view indices
    if mode == 'green':
        # GVI defaults - detect vegetation and trees
        hit_values = (-2, 2, 5, 6, 7, 8)
        inclusion_mode = True
    elif mode == 'sky':
        # SVI defaults - detect open sky
        hit_values = (0,)
        inclusion_mode = False
    else:
        # For custom mode, user must specify hit_values
        if hit_values is None:
            raise ValueError("For custom mode, you must provide hit_values.")

    # Extract parameters from kwargs with sensible defaults
    view_point_height = kwargs.get("view_point_height", 1.5)
    view_height_voxel = int(view_point_height / meshsize)
    colormap = kwargs.get("colormap", 'viridis')
    vmin = kwargs.get("vmin", 0.0)
    vmax = kwargs.get("vmax", 1.0)
    
    # Ray casting parameters for hemisphere sampling
    N_azimuth = kwargs.get("N_azimuth", 60)
    N_elevation = kwargs.get("N_elevation", 10)
    elevation_min_degrees = kwargs.get("elevation_min_degrees", -30)
    elevation_max_degrees = kwargs.get("elevation_max_degrees", 30)
    
    # Tree transmittance parameters for Beer-Lambert law
    tree_k = kwargs.get("tree_k", 0.5)
    tree_lad = kwargs.get("tree_lad", 1.0)

    # Generate ray directions using spherical coordinates
    # Create uniform sampling over specified azimuth and elevation ranges
    azimuth_angles = np.linspace(0, 2 * np.pi, N_azimuth, endpoint=False)
    elevation_angles = np.deg2rad(np.linspace(elevation_min_degrees, elevation_max_degrees, N_elevation))

    ray_directions = []
    for elevation in elevation_angles:
        cos_elev = np.cos(elevation)
        sin_elev = np.sin(elevation)
        for azimuth in azimuth_angles:
            # Convert spherical coordinates to Cartesian
            dx = cos_elev * np.cos(azimuth)
            dy = cos_elev * np.sin(azimuth)
            dz = sin_elev
            ray_directions.append([dx, dy, dz])
    ray_directions = np.array(ray_directions, dtype=np.float64)

    # Compute the view index map with transmittance parameters
    vi_map = compute_vi_map_generic(voxel_data, ray_directions, view_height_voxel, 
                                  hit_values, meshsize, tree_k, tree_lad, inclusion_mode)

    # Create visualization with custom colormap handling
    import matplotlib.pyplot as plt
    cmap = plt.cm.get_cmap(colormap).copy()
    cmap.set_bad(color='lightgray')  # Color for NaN values (invalid locations)
    plt.figure(figsize=(10, 8))
    plt.imshow(vi_map, origin='lower', cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label='View Index')
    plt.axis('off')
    plt.show()

    # Optional OBJ export for 3D visualization
    obj_export = kwargs.get("obj_export", False)
    if obj_export:
        dem_grid = kwargs.get("dem_grid", np.zeros_like(vi_map))
        output_dir = kwargs.get("output_directory", "output")
        output_file_name = kwargs.get("output_file_name", "view_index")
        num_colors = kwargs.get("num_colors", 10)
        alpha = kwargs.get("alpha", 1.0)
        grid_to_obj(
            vi_map,
            dem_grid,
            output_dir,
            output_file_name,
            meshsize,
            view_point_height,
            colormap_name=colormap,
            num_colors=num_colors,
            alpha=alpha,
            vmin=vmin,
            vmax=vmax
        )

    return vi_map

def mark_building_by_id(voxcity_grid_ori, building_id_grid_ori, ids, mark):
    """Mark specific buildings in the voxel grid with a given value.

    This function is used to identify landmark buildings for visibility analysis
    by replacing their voxel values with a special marker value. It handles
    coordinate system alignment between the building ID grid and voxel grid.

    Args:
        voxcity_grid_ori (ndarray): 3D array of voxel values (original, will be copied)
        building_id_grid_ori (ndarray): 2D array of building IDs (original, will be copied)
        ids (list): List of building IDs to mark as landmarks
        mark (int): Value to mark the landmark buildings with (typically negative)

    Returns:
        ndarray: Modified 3D voxel grid with landmark buildings marked
    """
    # Create working copies to avoid modifying original data
    voxcity_grid = voxcity_grid_ori.copy()

    # Flip building ID grid vertically to match voxel grid orientation
    # This accounts for different coordinate system conventions
    building_id_grid = np.flipud(building_id_grid_ori.copy())

    # Find x,y positions where target building IDs are located
    positions = np.where(np.isin(building_id_grid, ids))

    # Process each location containing a target building
    for i in range(len(positions[0])):
        x, y = positions[0][i], positions[1][i]
        # Find all building voxels (-3) at this x,y location and mark them
        z_mask = voxcity_grid[x, y, :] == -3
        voxcity_grid[x, y, z_mask] = mark
    
    return voxcity_grid

@njit
def trace_ray_to_target(voxel_data, origin, target, opaque_values):
    """Trace a ray from origin to target through voxel data.

    Uses DDA algorithm to efficiently traverse voxels along ray path.
    Checks for any opaque voxels blocking the line of sight.

    Args:
        voxel_data (ndarray): 3D array of voxel values
        origin (tuple): Starting point (x,y,z) in voxel coordinates
        target (tuple): End point (x,y,z) in voxel coordinates
        opaque_values (ndarray): Array of voxel values that block the ray

    Returns:
        bool: True if target is visible from origin, False otherwise
    """
    nx, ny, nz = voxel_data.shape
    x0, y0, z0 = origin
    x1, y1, z1 = target
    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0

    # Normalize direction vector for consistent traversal
    length = np.sqrt(dx*dx + dy*dy + dz*dz)
    if length == 0.0:
        return True  # Origin and target are at the same location
    dx /= length
    dy /= length
    dz /= length

    # Initialize ray position at center of starting voxel
    x, y, z = x0 + 0.5, y0 + 0.5, z0 + 0.5
    i, j, k = int(x0), int(y0), int(z0)

    # Determine step direction for each axis
    step_x = 1 if dx >= 0 else -1
    step_y = 1 if dy >= 0 else -1
    step_z = 1 if dz >= 0 else -1

    # Calculate distances to next voxel boundaries and step sizes
    # Handle cases where direction components are zero to avoid division by zero
    if dx != 0:
        t_max_x = ((i + (step_x > 0)) - x) / dx
        t_delta_x = abs(1 / dx)
    else:
        t_max_x = np.inf
        t_delta_x = np.inf

    if dy != 0:
        t_max_y = ((j + (step_y > 0)) - y) / dy
        t_delta_y = abs(1 / dy)
    else:
        t_max_y = np.inf
        t_delta_y = np.inf

    if dz != 0:
        t_max_z = ((k + (step_z > 0)) - z) / dz
        t_delta_z = abs(1 / dz)
    else:
        t_max_z = np.inf
        t_delta_z = np.inf

    # Main ray traversal loop using DDA algorithm
    while True:
        # Check if current voxel is within bounds and contains opaque material
        if (0 <= i < nx) and (0 <= j < ny) and (0 <= k < nz):
            voxel_value = voxel_data[i, j, k]
            if voxel_value in opaque_values:
                return False  # Ray is blocked by opaque voxel
        else:
            return False  # Ray went out of bounds before reaching target

        # Check if we've reached the target voxel
        if i == int(x1) and j == int(y1) and k == int(z1):
            return True  # Ray successfully reached the target

        # Move to next voxel using DDA algorithm
        # Choose the axis with the smallest distance to next boundary
        if t_max_x < t_max_y:
            if t_max_x < t_max_z:
                t_max = t_max_x
                t_max_x += t_delta_x
                i += step_x
            else:
                t_max = t_max_z
                t_max_z += t_delta_z
                k += step_z
        else:
            if t_max_y < t_max_z:
                t_max = t_max_y
                t_max_y += t_delta_y
                j += step_y
            else:
                t_max = t_max_z
                t_max_z += t_delta_z
                k += step_z

@njit
def compute_visibility_to_all_landmarks(observer_location, landmark_positions, voxel_data, opaque_values):
    """Check if any landmark is visible from the observer location.

    Traces rays to each landmark position until finding one that's visible.
    Uses optimized ray tracing with early exit on first visible landmark.

    Args:
        observer_location (ndarray): Observer position (x,y,z) in voxel coordinates
        landmark_positions (ndarray): Array of landmark positions (n_landmarks, 3)
        voxel_data (ndarray): 3D array of voxel values
        opaque_values (ndarray): Array of voxel values that block visibility

    Returns:
        int: 1 if any landmark is visible, 0 if none are visible
    """
    # Check visibility to each landmark sequentially
    # Early exit strategy: return 1 as soon as any landmark is visible
    for idx in range(landmark_positions.shape[0]):
        target = landmark_positions[idx].astype(np.float64)
        is_visible = trace_ray_to_target(voxel_data, observer_location, target, opaque_values)
        if is_visible:
            return 1  # Return immediately when first visible landmark is found
    return 0  # No landmarks were visible from this location

@njit(parallel=True)
def compute_visibility_map(voxel_data, landmark_positions, opaque_values, view_height_voxel):
    """Compute visibility map for landmarks in the voxel grid.

    Places observers at valid locations (empty voxels above ground, excluding building
    roofs and vegetation) and checks visibility to any landmark.

    The function processes each x,y position in parallel for efficiency.
    Valid observer locations are:
    - Empty voxels (0) or tree voxels (-2)
    - Above non-empty, non-tree voxels
    - Not above water (7,8,9) or negative values

    Args:
        voxel_data (ndarray): 3D array of voxel values
        landmark_positions (ndarray): Array of landmark positions (n_landmarks, 3)
        opaque_values (ndarray): Array of voxel values that block visibility
        view_height_voxel (int): Height offset for observer in voxels

    Returns:
        ndarray: 2D array of visibility values
            NaN = invalid observer location
            0 = no landmarks visible
            1 = at least one landmark visible
    """
    nx, ny, nz = voxel_data.shape
    visibility_map = np.full((nx, ny), np.nan)

    # Process each x,y position in parallel for computational efficiency
    for x in prange(nx):
        for y in range(ny):
            found_observer = False
            # Find the lowest valid observer location by searching from bottom up
            for z in range(1, nz):
                # Valid observer location: empty voxel above non-empty ground
                if voxel_data[x, y, z] == 0 and voxel_data[x, y, z - 1] != 0:
                    # Skip locations above building roofs or vegetation
                    if (voxel_data[x, y, z - 1] in (7, 8, 9)) or (voxel_data[x, y, z - 1] < 0):
                        visibility_map[x, y] = np.nan
                        found_observer = True
                        break
                    else:
                        # Place observer at specified height above ground level
                        observer_location = np.array([x, y, z+view_height_voxel], dtype=np.float64)
                        # Check visibility to any landmark from this location
                        visible = compute_visibility_to_all_landmarks(observer_location, landmark_positions, voxel_data, opaque_values)
                        visibility_map[x, y] = visible
                        found_observer = True
                        break
            # Mark locations where no valid observer position exists
            if not found_observer:
                visibility_map[x, y] = np.nan

    return visibility_map

def compute_landmark_visibility(voxel_data, target_value=-30, view_height_voxel=0, colormap='viridis'):
    """Compute and visualize landmark visibility in a voxel grid.

    Places observers at valid locations and checks visibility to any landmark voxel.
    Generates a binary visibility map and visualization.

    The function:
    1. Identifies all landmark voxels (target_value)
    2. Determines which voxel values block visibility
    3. Computes visibility from each valid observer location
    4. Generates visualization with legend

    Args:
        voxel_data (ndarray): 3D array of voxel values
        target_value (int, optional): Value used to identify landmark voxels. Defaults to -30.
        view_height_voxel (int, optional): Height offset for observer in voxels. Defaults to 0.
        colormap (str, optional): Matplotlib colormap name. Defaults to 'viridis'.

    Returns:
        ndarray: 2D array of visibility values (0 or 1) with y-axis flipped
            NaN = invalid observer location
            0 = no landmarks visible
            1 = at least one landmark visible

    Raises:
        ValueError: If no landmark voxels are found with the specified target_value
    """
    # Find positions of all landmark voxels
    landmark_positions = np.argwhere(voxel_data == target_value)

    if landmark_positions.shape[0] == 0:
        raise ValueError(f"No landmark with value {target_value} found in the voxel data.")

    # Define which voxel values block visibility
    unique_values = np.unique(voxel_data)
    opaque_values = np.array([v for v in unique_values if v != 0 and v != target_value], dtype=np.int32)

    # Compute visibility map
    visibility_map = compute_visibility_map(voxel_data, landmark_positions, opaque_values, view_height_voxel)

    # Set up visualization
    cmap = plt.cm.get_cmap(colormap, 2).copy()
    cmap.set_bad(color='lightgray')

    # Create main plot
    plt.figure(figsize=(10, 8))
    plt.imshow(np.flipud(visibility_map), origin='lower', cmap=cmap, vmin=0, vmax=1)

    # Create and add legend
    visible_patch = mpatches.Patch(color=cmap(1.0), label='Visible (1)')
    not_visible_patch = mpatches.Patch(color=cmap(0.0), label='Not Visible (0)')
    plt.legend(handles=[visible_patch, not_visible_patch], 
            loc='center left',
            bbox_to_anchor=(1.0, 0.5))
    plt.axis('off')
    plt.show()

    return np.flipud(visibility_map)

def get_landmark_visibility_map(voxcity_grid_ori, building_id_grid, building_gdf, meshsize, **kwargs):
    """Generate a visibility map for landmark buildings in a voxel city.

    Places observers at valid locations and checks visibility to any part of the
    specified landmark buildings. Can identify landmarks either by ID or by finding
    buildings within a specified rectangle.

    Args:
        voxcity_grid (ndarray): 3D array representing the voxel city
        building_id_grid (ndarray): 3D array mapping voxels to building IDs
        building_gdf (GeoDataFrame): GeoDataFrame containing building features
        meshsize (float): Size of each voxel in meters
        **kwargs: Additional keyword arguments
            view_point_height (float): Height of observer viewpoint in meters
            colormap (str): Matplotlib colormap name
            landmark_building_ids (list): List of building IDs to mark as landmarks
            rectangle_vertices (list): List of (lat,lon) coordinates defining rectangle
            obj_export (bool): Whether to export visibility map as OBJ file
            dem_grid (ndarray): Digital elevation model grid for OBJ export
            output_directory (str): Directory for OBJ file output
            output_file_name (str): Base filename for OBJ output
            alpha (float): Alpha transparency value for OBJ export
            vmin (float): Minimum value for color mapping
            vmax (float): Maximum value for color mapping

    Returns:
        ndarray: 2D array of visibility values for landmark buildings
    """
    # Convert observer height from meters to voxel units
    view_point_height = kwargs.get("view_point_height", 1.5)
    view_height_voxel = int(view_point_height / meshsize)

    colormap = kwargs.get("colormap", 'viridis')

    # Get landmark building IDs either directly or by finding buildings in rectangle
    landmark_ids = kwargs.get('landmark_building_ids', None)
    landmark_polygon = kwargs.get('landmark_polygon', None)
    if landmark_ids is None:
        if landmark_polygon is not None:
            landmark_ids = get_buildings_in_drawn_polygon(building_gdf, landmark_polygon, operation='within')
        else:
            rectangle_vertices = kwargs.get("rectangle_vertices", None)
            if rectangle_vertices is None:
                print("Cannot set landmark buildings. You need to input either of rectangle_vertices or landmark_ids.")
                return None
                
            # Calculate center point of rectangle
            lons = [coord[0] for coord in rectangle_vertices]
            lats = [coord[1] for coord in rectangle_vertices]
            center_lon = (min(lons) + max(lons)) / 2
            center_lat = (min(lats) + max(lats)) / 2
            target_point = (center_lon, center_lat)
            
            # Find buildings at center point
            landmark_ids = find_building_containing_point(building_gdf, target_point)

    # Mark landmark buildings in voxel grid with special value
    target_value = -30
    voxcity_grid = mark_building_by_id(voxcity_grid_ori, building_id_grid, landmark_ids, target_value)
    
    # Compute visibility map
    landmark_vis_map = compute_landmark_visibility(voxcity_grid, target_value=target_value, view_height_voxel=view_height_voxel, colormap=colormap)

    # Handle optional OBJ export
    obj_export = kwargs.get("obj_export")
    if obj_export == True:
        dem_grid = kwargs.get("dem_grid", np.zeros_like(landmark_vis_map))
        output_dir = kwargs.get("output_directory", "output")
        output_file_name = kwargs.get("output_file_name", "landmark_visibility")        
        num_colors = 2
        alpha = kwargs.get("alpha", 1.0)
        vmin = kwargs.get("vmin", 0.0)
        vmax = kwargs.get("vmax", 1.0)
        
        # Export visibility map and voxel city as OBJ files
        grid_to_obj(
            landmark_vis_map,
            dem_grid,
            output_dir,
            output_file_name,
            meshsize,
            view_point_height,
            colormap_name=colormap,
            num_colors=num_colors,
            alpha=alpha,
            vmin=vmin,
            vmax=vmax
        )
        output_file_name_vox = 'voxcity_' + output_file_name
        export_obj(voxcity_grid, output_dir, output_file_name_vox, meshsize)

    return landmark_vis_map, voxcity_grid

def get_sky_view_factor_map(voxel_data, meshsize, show_plot=False, **kwargs):
    """
    Compute and visualize the Sky View Factor (SVF) for each valid observer cell in the voxel grid.

    Sky View Factor measures the proportion of the sky hemisphere that is visible from a given point.
    It ranges from 0 (completely obstructed) to 1 (completely open sky). This implementation:
    - Uses hemisphere ray casting to sample sky visibility
    - Accounts for tree transmittance using Beer-Lambert law
    - Places observers at valid street-level locations
    - Provides optional visualization and OBJ export

    Args:
        voxel_data (ndarray): 3D array of voxel values.
        meshsize (float): Size of each voxel in meters.
        show_plot (bool): Whether to display the SVF visualization plot.
        **kwargs: Additional parameters including:
            view_point_height (float): Observer height in meters (default: 1.5)
            colormap (str): Matplotlib colormap name (default: 'BuPu_r')
            vmin, vmax (float): Color scale limits (default: 0.0, 1.0)
            N_azimuth (int): Number of azimuth angles for ray sampling (default: 60)
            N_elevation (int): Number of elevation angles for ray sampling (default: 10)
            elevation_min_degrees (float): Minimum elevation angle (default: 0)
            elevation_max_degrees (float): Maximum elevation angle (default: 90)
            tree_k (float): Tree extinction coefficient (default: 0.6)
            tree_lad (float): Leaf area density in m^-1 (default: 1.0)
            obj_export (bool): Whether to export as OBJ file (default: False)

    Returns:
        ndarray: 2D array of SVF values at each valid observer location (x, y).
                 NaN values indicate invalid observer positions.
    """
    # Extract default parameters with sky-specific settings
    view_point_height = kwargs.get("view_point_height", 1.5)
    view_height_voxel = int(view_point_height / meshsize)
    colormap = kwargs.get("colormap", 'BuPu_r')  # Blue-purple colormap suitable for sky
    vmin = kwargs.get("vmin", 0.0)
    vmax = kwargs.get("vmax", 1.0)
    
    # Ray sampling parameters optimized for sky view factor
    N_azimuth = kwargs.get("N_azimuth", 60)      # Full 360-degree azimuth sampling
    N_elevation = kwargs.get("N_elevation", 10)   # Hemisphere elevation sampling
    elevation_min_degrees = kwargs.get("elevation_min_degrees", 0)   # Horizon
    elevation_max_degrees = kwargs.get("elevation_max_degrees", 90)  # Zenith

    # Tree transmittance parameters for Beer-Lambert law
    tree_k = kwargs.get("tree_k", 0.6)    # Static extinction coefficient
    tree_lad = kwargs.get("tree_lad", 1.0) # Leaf area density in m^-1

    # Sky view factor configuration: detect open sky (value 0)
    hit_values = (0,)        # Sky voxels have value 0
    inclusion_mode = False   # Count rays that DON'T hit obstacles (exclusion mode)

    # Generate ray directions over the sky hemisphere (0 to 90 degrees elevation)
    azimuth_angles = np.linspace(0, 2 * np.pi, N_azimuth, endpoint=False)
    elevation_angles = np.deg2rad(np.linspace(elevation_min_degrees, elevation_max_degrees, N_elevation))

    ray_directions = []
    for elevation in elevation_angles:
        cos_elev = np.cos(elevation)
        sin_elev = np.sin(elevation)
        for azimuth in azimuth_angles:
            # Convert spherical to Cartesian coordinates
            dx = cos_elev * np.cos(azimuth)
            dy = cos_elev * np.sin(azimuth)
            dz = sin_elev  # Always positive for sky hemisphere
            ray_directions.append([dx, dy, dz])
    ray_directions = np.array(ray_directions, dtype=np.float64)

    # Compute the SVF map using the generic view index computation
    vi_map = compute_vi_map_generic(voxel_data, ray_directions, view_height_voxel, 
                                  hit_values, meshsize, tree_k, tree_lad, inclusion_mode)

    # Display visualization if requested
    if show_plot:
        import matplotlib.pyplot as plt
        cmap = plt.cm.get_cmap(colormap).copy()
        cmap.set_bad(color='lightgray')  # Gray for invalid observer locations
        plt.figure(figsize=(10, 8))
        plt.imshow(vi_map, origin='lower', cmap=cmap, vmin=vmin, vmax=vmax)
        plt.colorbar(label='Sky View Factor')
        plt.axis('off')
        plt.show()

    # Optional OBJ export for 3D visualization
    obj_export = kwargs.get("obj_export", False)
    if obj_export:        
        dem_grid = kwargs.get("dem_grid", np.zeros_like(vi_map))
        output_dir = kwargs.get("output_directory", "output")
        output_file_name = kwargs.get("output_file_name", "sky_view_factor")
        num_colors = kwargs.get("num_colors", 10)
        alpha = kwargs.get("alpha", 1.0)
        grid_to_obj(
            vi_map,
            dem_grid,
            output_dir,
            output_file_name,
            meshsize,
            view_point_height,
            colormap_name=colormap,
            num_colors=num_colors,
            alpha=alpha,
            vmin=vmin,
            vmax=vmax
        )

    return vi_map

@njit
def rotate_vector_axis_angle(vec, axis, angle):
    """
    Rotate a 3D vector around an arbitrary axis using Rodrigues' rotation formula.
    
    This function implements the Rodrigues rotation formula:
    v_rot = v*cos(θ) + (k × v)*sin(θ) + k*(k·v)*(1-cos(θ))
    where k is the unit rotation axis, θ is the rotation angle, and v is the input vector.
    
    Args:
        vec (ndarray): 3D vector to rotate [x, y, z]
        axis (ndarray): 3D rotation axis vector [x, y, z] (will be normalized)
        angle (float): Rotation angle in radians
        
    Returns:
        ndarray: Rotated 3D vector [x, y, z]
    """
    # Normalize rotation axis to unit length
    axis_len = np.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
    if axis_len < 1e-12:
        # Degenerate axis case: return original vector unchanged
        return vec
    
    ux, uy, uz = axis / axis_len
    c = np.cos(angle)
    s = np.sin(angle)
    
    # Calculate dot product: k·v
    dot = vec[0]*ux + vec[1]*uy + vec[2]*uz
    
    # Calculate cross product: k × v
    cross_x = uy*vec[2] - uz*vec[1]
    cross_y = uz*vec[0] - ux*vec[2]
    cross_z = ux*vec[1] - uy*vec[0]
    
    # Apply Rodrigues formula: v_rot = v*c + (k × v)*s + k*(k·v)*(1-c)
    v_rot = np.zeros(3, dtype=np.float64)
    
    # First term: v*cos(θ)
    v_rot[0] = vec[0] * c
    v_rot[1] = vec[1] * c
    v_rot[2] = vec[2] * c
    
    # Second term: (k × v)*sin(θ)
    v_rot[0] += cross_x * s
    v_rot[1] += cross_y * s
    v_rot[2] += cross_z * s
    
    # Third term: k*(k·v)*(1-cos(θ))
    tmp = dot * (1.0 - c)
    v_rot[0] += ux * tmp
    v_rot[1] += uy * tmp
    v_rot[2] += uz * tmp
    
    return v_rot

@njit
def compute_view_factor_for_all_faces(
    face_centers,
    face_normals,
    hemisphere_dirs,
    voxel_data,
    meshsize,
    tree_k,
    tree_lad,
    target_values,
    inclusion_mode,
    grid_bounds_real,
    boundary_epsilon,
    ignore_downward=True
):
    """
    Compute a per-face "view factor" for a specified set of target voxel classes.

    This function computes view factors from building surface faces to target voxel types
    (e.g., sky, trees, other buildings). It uses hemisphere ray casting with rotation
    to align rays with each face's normal direction.

    Typical usage examples:
    - Sky View Factor: target_values=(0,), inclusion_mode=False (sky voxels)
    - Tree View Factor: target_values=(-2,), inclusion_mode=True (tree voxels)  
    - Building View Factor: target_values=(-3,), inclusion_mode=True (building voxels)

    Args:
        face_centers (np.ndarray): (n_faces, 3) face centroid positions in real coordinates.
        face_normals (np.ndarray): (n_faces, 3) face normal vectors (outward pointing).
        hemisphere_dirs (np.ndarray): (N, 3) set of direction vectors in the upper hemisphere.
        voxel_data (np.ndarray): 3D array of voxel values.
        meshsize (float): Size of each voxel in meters.
        tree_k (float): Tree extinction coefficient for Beer-Lambert law.
        tree_lad (float): Leaf area density in m^-1 for tree transmittance.
        target_values (tuple[int]): Voxel classes that define a 'hit' or target.
        inclusion_mode (bool): If True, hitting target_values counts as visibility.
                               If False, hitting anything NOT in target_values blocks the ray.
        grid_bounds_real (np.ndarray): [[x_min,y_min,z_min],[x_max,y_max,z_max]] in real coords.
        boundary_epsilon (float): Tolerance for identifying boundary vertical faces.
        ignore_downward (bool): If True, only consider upward rays. If False, consider all outward rays.

    Returns:
        np.ndarray of shape (n_faces,): Computed view factor for each face.
            NaN values indicate boundary vertical faces that should be excluded.
    """
    n_faces = face_centers.shape[0]
    face_vf_values = np.zeros(n_faces, dtype=np.float64)
    
    # Reference vector pointing upward (+Z direction)
    z_axis = np.array([0.0, 0.0, 1.0])
    
    # Process each face individually
    for fidx in range(n_faces):
        center = face_centers[fidx]
        normal = face_normals[fidx]
        
        # Check for boundary vertical faces and mark as NaN
        # This excludes faces on domain edges that may have artificial visibility
        is_vertical = (abs(normal[2]) < 0.01)  # Face normal is nearly horizontal
        
        # Check if face is near domain boundaries
        on_x_min = (abs(center[0] - grid_bounds_real[0,0]) < boundary_epsilon)
        on_y_min = (abs(center[1] - grid_bounds_real[0,1]) < boundary_epsilon)
        on_x_max = (abs(center[0] - grid_bounds_real[1,0]) < boundary_epsilon)
        on_y_max = (abs(center[1] - grid_bounds_real[1,1]) < boundary_epsilon)
        
        is_boundary_vertical = is_vertical and (on_x_min or on_y_min or on_x_max or on_y_max)
        if is_boundary_vertical:
            face_vf_values[fidx] = np.nan
            continue
        
        # Compute rotation to align face normal with +Z axis
        # This allows us to use the same hemisphere directions for all faces
        norm_n = np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        if norm_n < 1e-12:
            # Degenerate normal vector
            face_vf_values[fidx] = 0.0
            continue
        
        # Calculate angle between face normal and +Z axis
        dot_zn = z_axis[0]*normal[0] + z_axis[1]*normal[1] + z_axis[2]*normal[2]
        cos_angle = dot_zn / (norm_n)
        if cos_angle >  1.0: cos_angle =  1.0
        if cos_angle < -1.0: cos_angle = -1.0
        angle = np.arccos(cos_angle)
        
        # Handle special cases and general rotation
        if abs(cos_angle - 1.0) < 1e-9:
            # Face normal is already aligned with +Z => no rotation needed
            local_dirs = hemisphere_dirs
        elif abs(cos_angle + 1.0) < 1e-9:
            # Face normal points in -Z direction => rotate 180 degrees around X axis
            axis_180 = np.array([1.0, 0.0, 0.0])
            local_dirs = np.empty_like(hemisphere_dirs)
            for i in range(hemisphere_dirs.shape[0]):
                local_dirs[i] = rotate_vector_axis_angle(hemisphere_dirs[i], axis_180, np.pi)
        else:
            # General case: rotate around axis perpendicular to both +Z and face normal
            axis_x = z_axis[1]*normal[2] - z_axis[2]*normal[1]
            axis_y = z_axis[2]*normal[0] - z_axis[0]*normal[2]
            axis_z = z_axis[0]*normal[1] - z_axis[1]*normal[0]
            rot_axis = np.array([axis_x, axis_y, axis_z], dtype=np.float64)
            
            local_dirs = np.empty_like(hemisphere_dirs)
            for i in range(hemisphere_dirs.shape[0]):
                local_dirs[i] = rotate_vector_axis_angle(
                    hemisphere_dirs[i],
                    rot_axis,
                    angle
                )
        
        # Count valid ray directions based on face orientation and downward filtering
        total_outward = 0  # Rays pointing away from face surface
        num_valid = 0      # Rays that meet all criteria (outward + optionally upward)
        
        for i in range(local_dirs.shape[0]):
            dvec = local_dirs[i]
            # Check if ray points outward from face surface (positive dot product with normal)
            dp = dvec[0]*normal[0] + dvec[1]*normal[1] + dvec[2]*normal[2]
            if dp > 0.0:
                total_outward += 1
                # Apply downward filtering if requested
                if not ignore_downward or dvec[2] > 0.0:
                    num_valid += 1
        
        # Handle cases with no valid directions
        if total_outward == 0:
            face_vf_values[fidx] = 0.0
            continue
        
        if num_valid == 0:
            face_vf_values[fidx] = 0.0
            continue
        
        # Create array containing only the valid ray directions
        valid_dirs_arr = np.empty((num_valid, 3), dtype=np.float64)
        out_idx = 0
        for i in range(local_dirs.shape[0]):
            dvec = local_dirs[i]
            dp = dvec[0]*normal[0] + dvec[1]*normal[1] + dvec[2]*normal[2]
            if dp > 0.0 and (not ignore_downward or dvec[2] > 0.0):
                valid_dirs_arr[out_idx, 0] = dvec[0]
                valid_dirs_arr[out_idx, 1] = dvec[1]
                valid_dirs_arr[out_idx, 2] = dvec[2]
                out_idx += 1
        
        # Set ray origin slightly offset from face surface to avoid self-intersection
        offset_vox = 0.1  # Offset in voxel units
        ray_origin = (center / meshsize) + (normal / norm_n) * offset_vox
        
        # Compute fraction of valid rays that "see" the target using generic ray tracing
        vf = compute_vi_generic(
            ray_origin,
            voxel_data,
            valid_dirs_arr,
            target_values,
            meshsize,
            tree_k,
            tree_lad,
            inclusion_mode
        )
        
        # Scale result by fraction of directions that were valid
        # This normalizes for the hemisphere portion that the face can actually "see"
        fraction_valid = num_valid / total_outward
        face_vf_values[fidx] = vf * fraction_valid
    
    return face_vf_values

def get_surface_view_factor(voxel_data, meshsize, **kwargs):
    """
    Compute and optionally visualize view factors for surface meshes with respect to target voxel classes.
    
    This function provides a flexible framework for computing various surface-based view factors:
    - Sky View Factor: Fraction of sky hemisphere visible from building surfaces
    - Tree View Factor: Fraction of directions that intersect vegetation
    - Building View Factor: Fraction of directions that intersect other buildings
    - Custom View Factors: User-defined target voxel classes
    
    The function extracts surface meshes from the voxel data, then computes view factors
    for each face using hemisphere ray casting with proper geometric transformations.

    Args:
        voxel_data (ndarray): 3D array of voxel values representing the urban environment.
        meshsize (float): Size of each voxel in meters for coordinate scaling.
        **kwargs: Extensive configuration options including:
            # Target specification:
            target_values (tuple[int]): Voxel classes to measure visibility to (default: (0,) for sky)
            inclusion_mode (bool): Interpretation of target_values (default: False for sky)
            
            # Surface extraction:
            building_class_id (int): Voxel class to extract surfaces from (default: -3 for buildings)
            building_id_grid (ndarray): Optional grid mapping voxels to building IDs
            
            # Ray sampling:
            N_azimuth (int): Number of azimuth angles for hemisphere sampling (default: 60)
            N_elevation (int): Number of elevation angles for hemisphere sampling (default: 10)
            
            # Tree transmittance (Beer-Lambert law):
            tree_k (float): Tree extinction coefficient (default: 0.6)
            tree_lad (float): Leaf area density in m^-1 (default: 1.0)
            
            # Visualization and export:
            colormap (str): Matplotlib colormap for visualization (default: 'BuPu_r')
            vmin, vmax (float): Color scale limits (default: 0.0, 1.0)
            obj_export (bool): Whether to export mesh as OBJ file (default: False)
            output_directory (str): Directory for OBJ export (default: "output")
            output_file_name (str): Base filename for OBJ export (default: "surface_view_factor")
            
            # Other options:
            progress_report (bool): Whether to print computation progress (default: False)
            debug (bool): Enable debug output (default: False)

    Returns:
        trimesh.Trimesh: Surface mesh with per-face view factor values stored in metadata.
                        The view factor values can be accessed via mesh.metadata[value_name].
                        Returns None if no surfaces are found or extraction fails.
                        
    Example Usage:
        # Sky View Factor for building surfaces
        mesh = get_surface_view_factor(voxel_data, meshsize, 
                                     target_values=(0,), inclusion_mode=False)
        
        # Tree View Factor for building surfaces  
        mesh = get_surface_view_factor(voxel_data, meshsize,
                                     target_values=(-2,), inclusion_mode=True)
        
        # Custom view factor with OBJ export
        mesh = get_surface_view_factor(voxel_data, meshsize,
                                     target_values=(-3,), inclusion_mode=True,
                                     obj_export=True, output_file_name="building_view_factor")
    """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    import os
    
    # Extract configuration parameters with appropriate defaults
    value_name     = kwargs.get("value_name", 'view_factor_values')
    colormap       = kwargs.get("colormap", 'BuPu_r')
    vmin           = kwargs.get("vmin", 0.0)
    vmax           = kwargs.get("vmax", 1.0)
    N_azimuth      = kwargs.get("N_azimuth", 60)
    N_elevation    = kwargs.get("N_elevation", 10)
    debug          = kwargs.get("debug", False)
    progress_report= kwargs.get("progress_report", False)
    building_id_grid = kwargs.get("building_id_grid", None)
    
    # Tree transmittance parameters for Beer-Lambert law
    tree_k         = kwargs.get("tree_k", 0.6)
    tree_lad       = kwargs.get("tree_lad", 1.0)
    
    # Target specification - defaults to sky view factor configuration
    target_values  = kwargs.get("target_values", (0,))     # Sky voxels by default
    inclusion_mode = kwargs.get("inclusion_mode", False)   # Exclusion mode for sky
    
    # Surface extraction parameters
    building_class_id = kwargs.get("building_class_id", -3)  # Building voxel class
    
    # Extract surface mesh from the specified voxel class
    try:
        building_mesh = create_voxel_mesh(
            voxel_data, 
            building_class_id, 
            meshsize,
            building_id_grid=building_id_grid,
            mesh_type='open_air'  # Extract surfaces exposed to air
        )
        if building_mesh is None or len(building_mesh.faces) == 0:
            print("No surfaces found in voxel data for the specified class.")
            return None
    except Exception as e:
        print(f"Error during mesh extraction: {e}")
        return None
    
    if progress_report:
        print(f"Processing view factor for {len(building_mesh.faces)} faces...")

    # Extract geometric properties from the mesh
    face_centers = building_mesh.triangles_center  # Centroid of each face
    face_normals = building_mesh.face_normals      # Outward normal of each face
    
    # Generate hemisphere ray directions using spherical coordinates
    # These directions will be rotated to align with each face's normal
    azimuth_angles   = np.linspace(0, 2*np.pi, N_azimuth, endpoint=False)
    elevation_angles = np.linspace(0, np.pi/2, N_elevation)  # Upper hemisphere only
    hemisphere_list = []
    for elev in elevation_angles:
        sin_elev = np.sin(elev)
        cos_elev = np.cos(elev)
        for az in azimuth_angles:
            # Convert spherical to Cartesian coordinates
            x = cos_elev * np.cos(az)
            y = cos_elev * np.sin(az)
            z = sin_elev  # Always positive (upper hemisphere)
            hemisphere_list.append([x, y, z])
    hemisphere_dirs = np.array(hemisphere_list, dtype=np.float64)
    
    # Calculate domain bounds for boundary face detection
    nx, ny, nz = voxel_data.shape
    grid_bounds_voxel = np.array([[0,0,0],[nx, ny, nz]], dtype=np.float64)
    grid_bounds_real = grid_bounds_voxel * meshsize
    boundary_epsilon = meshsize * 0.05  # Tolerance for boundary detection
    
    # Compute view factors for all faces using optimized Numba implementation
    face_vf_values = compute_view_factor_for_all_faces(
        face_centers,
        face_normals,
        hemisphere_dirs,
        voxel_data,
        meshsize,
        tree_k,
        tree_lad,
        target_values,   # User-specified target voxel classes
        inclusion_mode,  # User-specified hit interpretation
        grid_bounds_real,
        boundary_epsilon
    )
    
    # Store computed view factor values in mesh metadata for later access
    if not hasattr(building_mesh, 'metadata'):
        building_mesh.metadata = {}
    building_mesh.metadata[value_name] = face_vf_values
       
    # Optional OBJ file export for external visualization/analysis
    obj_export = kwargs.get("obj_export", False)
    if obj_export:
        output_dir      = kwargs.get("output_directory", "output")
        output_file_name= kwargs.get("output_file_name", "surface_view_factor")
        os.makedirs(output_dir, exist_ok=True)
        try:
            building_mesh.export(f"{output_dir}/{output_file_name}.obj")
            print(f"Exported surface mesh to {output_dir}/{output_file_name}.obj")
        except Exception as e:
            print(f"Error exporting mesh: {e}")
    
    return building_mesh

@njit
def trace_ray_to_landmark(voxel_data, origin, target, opaque_values, tree_k, tree_lad, meshsize):
    """Trace a ray from origin to target through voxel data with tree transmittance.
    
    Uses DDA algorithm to efficiently traverse voxels along ray path.
    Checks for opaque voxels and handles tree transmittance using Beer-Lambert law.
    
    Args:
        voxel_data (ndarray): 3D array of voxel values
        origin (ndarray): Starting point (x,y,z) in voxel coordinates
        target (ndarray): End point (x,y,z) in voxel coordinates
        opaque_values (ndarray): Array of voxel values that block the ray
        tree_k (float): Tree extinction coefficient for Beer-Lambert law
        tree_lad (float): Leaf area density in m^-1 for tree transmittance
        meshsize (float): Size of each voxel in meters
        
    Returns:
        bool: True if target is visible from origin, False otherwise
    """
    nx, ny, nz = voxel_data.shape
    x0, y0, z0 = origin[0], origin[1], origin[2]
    x1, y1, z1 = target[0], target[1], target[2]
    
    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0
    
    # Normalize direction vector
    length = np.sqrt(dx*dx + dy*dy + dz*dz)
    if length == 0.0:
        return True  # Origin and target are at the same location
        
    dx /= length
    dy /= length
    dz /= length
    
    # Initialize ray position
    x, y, z = x0 + 0.5, y0 + 0.5, z0 + 0.5
    i, j, k = int(x0), int(y0), int(z0)
    
    # Determine step direction
    step_x = 1 if dx >= 0 else -1
    step_y = 1 if dy >= 0 else -1
    step_z = 1 if dz >= 0 else -1
    
    # Calculate distances to next voxel boundaries
    if dx != 0:
        t_max_x = ((i + (step_x > 0)) - x) / dx
        t_delta_x = abs(1 / dx)
    else:
        t_max_x = np.inf
        t_delta_x = np.inf
        
    if dy != 0:
        t_max_y = ((j + (step_y > 0)) - y) / dy
        t_delta_y = abs(1 / dy)
    else:
        t_max_y = np.inf
        t_delta_y = np.inf
        
    if dz != 0:
        t_max_z = ((k + (step_z > 0)) - z) / dz
        t_delta_z = abs(1 / dz)
    else:
        t_max_z = np.inf
        t_delta_z = np.inf
    
    # Track cumulative tree transmittance
    tree_transmittance = 1.0
    
    # Main ray traversal loop
    while True:
        # Check if current voxel is within bounds
        if (0 <= i < nx) and (0 <= j < ny) and (0 <= k < nz):
            voxel_value = voxel_data[i, j, k]
            
            # Check for tree voxels (-2)
            if voxel_value == -2:
                # Apply Beer-Lambert law for tree transmittance
                tree_transmittance *= np.exp(-tree_k * tree_lad * meshsize)
                if tree_transmittance < 0.01:  # Ray effectively blocked
                    return False
            # Check for other opaque voxels
            elif voxel_value in opaque_values:
                return False  # Ray is blocked
        else:
            return False  # Ray went out of bounds
        
        # Check if we've reached the target voxel
        if i == int(x1) and j == int(y1) and k == int(z1):
            return True  # Ray successfully reached the target
        
        # Move to next voxel using DDA algorithm
        if t_max_x < t_max_y:
            if t_max_x < t_max_z:
                t_max_x += t_delta_x
                i += step_x
            else:
                t_max_z += t_delta_z
                k += step_z
        else:
            if t_max_y < t_max_z:
                t_max_y += t_delta_y
                j += step_y
            else:
                t_max_z += t_delta_z
                k += step_z


@njit
def compute_face_landmark_visibility(face_center, face_normal, landmark_positions, 
                                   voxel_data, meshsize, tree_k, tree_lad, 
                                   grid_bounds_real, boundary_epsilon):
    """Compute binary landmark visibility for a single face.
    
    Args:
        face_center (ndarray): Face centroid position in real coordinates
        face_normal (ndarray): Face normal vector (outward pointing)
        landmark_positions (ndarray): Array of landmark positions in voxel coordinates
        voxel_data (ndarray): 3D array of voxel values
        meshsize (float): Size of each voxel in meters
        tree_k (float): Tree extinction coefficient
        tree_lad (float): Leaf area density
        grid_bounds_real (ndarray): Domain bounds in real coordinates
        boundary_epsilon (float): Tolerance for boundary detection
        
    Returns:
        float: 1.0 if any landmark is visible, 0.0 if none visible, np.nan for boundary faces
    """
    # Check for boundary vertical faces
    is_vertical = (abs(face_normal[2]) < 0.01)
    
    on_x_min = (abs(face_center[0] - grid_bounds_real[0,0]) < boundary_epsilon)
    on_y_min = (abs(face_center[1] - grid_bounds_real[0,1]) < boundary_epsilon)
    on_x_max = (abs(face_center[0] - grid_bounds_real[1,0]) < boundary_epsilon)
    on_y_max = (abs(face_center[1] - grid_bounds_real[1,1]) < boundary_epsilon)
    
    is_boundary_vertical = is_vertical and (on_x_min or on_y_min or on_x_max or on_y_max)
    if is_boundary_vertical:
        return np.nan
    
    # Convert face center to voxel coordinates with small offset
    norm_n = np.sqrt(face_normal[0]**2 + face_normal[1]**2 + face_normal[2]**2)
    if norm_n < 1e-12:
        return 0.0
    
    offset_vox = 0.1  # Offset in voxel units to avoid self-intersection
    ray_origin = (face_center / meshsize) + (face_normal / norm_n) * offset_vox
    
    # Define opaque values (everything except empty space and landmarks)
    unique_values = np.unique(voxel_data)
    landmark_value = -30  # Standard landmark value
    opaque_values = np.array([v for v in unique_values if v != 0 and v != landmark_value], dtype=np.int32)
    
    # Check visibility to each landmark
    for idx in range(landmark_positions.shape[0]):
        target = landmark_positions[idx]
        
        # Check if ray direction points towards the face (not away from it)
        ray_dir = target - ray_origin
        ray_length = np.sqrt(ray_dir[0]**2 + ray_dir[1]**2 + ray_dir[2]**2)
        if ray_length > 0:
            ray_dir = ray_dir / ray_length
            dot_product = (ray_dir[0]*face_normal[0] + 
                          ray_dir[1]*face_normal[1] + 
                          ray_dir[2]*face_normal[2])
            
            # Only trace ray if it points outward from the face
            if dot_product > 0:
                is_visible = trace_ray_to_landmark(voxel_data, ray_origin, target, 
                                                 opaque_values, tree_k, tree_lad, meshsize)
                if is_visible:
                    return 1.0  # Return immediately when first visible landmark is found
    
    return 0.0  # No landmarks were visible


@njit(parallel=True)
def compute_landmark_visibility_for_all_faces(face_centers, face_normals, landmark_positions,
                                            voxel_data, meshsize, tree_k, tree_lad,
                                            grid_bounds_real, boundary_epsilon):
    """Compute binary landmark visibility for all building surface faces.
    
    Args:
        face_centers (ndarray): (n_faces, 3) face centroid positions in real coordinates
        face_normals (ndarray): (n_faces, 3) face normal vectors
        landmark_positions (ndarray): (n_landmarks, 3) landmark positions in voxel coordinates
        voxel_data (ndarray): 3D array of voxel values
        meshsize (float): Size of each voxel in meters
        tree_k (float): Tree extinction coefficient
        tree_lad (float): Leaf area density
        grid_bounds_real (ndarray): Domain bounds in real coordinates
        boundary_epsilon (float): Tolerance for boundary detection
        
    Returns:
        ndarray: Binary visibility values for each face (1=visible, 0=not visible, nan=boundary)
    """
    n_faces = face_centers.shape[0]
    visibility_values = np.zeros(n_faces, dtype=np.float64)
    
    # Process each face in parallel
    for fidx in prange(n_faces):
        visibility_values[fidx] = compute_face_landmark_visibility(
            face_centers[fidx],
            face_normals[fidx],
            landmark_positions,
            voxel_data,
            meshsize,
            tree_k,
            tree_lad,
            grid_bounds_real,
            boundary_epsilon
        )
    
    return visibility_values


def get_surface_landmark_visibility(voxel_data, building_id_grid, building_gdf, meshsize, **kwargs):
    """
    Compute binary landmark visibility for building surface meshes.
    
    This function extracts building surface meshes and computes whether each face
    can see any landmark voxel. It uses direct ray tracing from face centers to
    all landmark positions, accounting for tree transmittance.
    
    Args:
        voxel_data (ndarray): 3D array of voxel values
        building_id_grid (ndarray): 3D array mapping voxels to building IDs
        building_gdf (GeoDataFrame): GeoDataFrame containing building features
        meshsize (float): Size of each voxel in meters
        **kwargs: Configuration options including:
            landmark_building_ids (list): List of building IDs to mark as landmarks
            landmark_polygon (list): Polygon vertices to identify landmarks
            rectangle_vertices (list): Rectangle vertices to identify landmarks
            building_class_id (int): Voxel class for buildings (default: -3)
            tree_k (float): Tree extinction coefficient (default: 0.6)
            tree_lad (float): Leaf area density (default: 1.0)
            colormap (str): Matplotlib colormap (default: 'RdYlGn')
            obj_export (bool): Whether to export mesh as OBJ file
            output_directory (str): Directory for OBJ export
            output_file_name (str): Base filename for OBJ export
            progress_report (bool): Whether to print progress
            
    Returns:
        tuple: (surface_mesh, modified_voxel_data)
            - surface_mesh: trimesh.Trimesh with binary visibility values in metadata
            - modified_voxel_data: voxel data with landmarks marked
            Returns (None, None) if no surfaces or landmarks found
    """
    import matplotlib.pyplot as plt
    import os
    
    # Get landmark building IDs
    landmark_ids = kwargs.get('landmark_building_ids', None)
    landmark_polygon = kwargs.get('landmark_polygon', None)
    if landmark_ids is None:
        if landmark_polygon is not None:
            landmark_ids = get_buildings_in_drawn_polygon(building_gdf, landmark_polygon, operation='within')
        else:
            rectangle_vertices = kwargs.get("rectangle_vertices", None)
            if rectangle_vertices is None:
                print("Cannot set landmark buildings. You need to input either of rectangle_vertices or landmark_ids.")
                return None, None
                
            # Calculate center point of rectangle
            lons = [coord[0] for coord in rectangle_vertices]
            lats = [coord[1] for coord in rectangle_vertices]
            center_lon = (min(lons) + max(lons)) / 2
            center_lat = (min(lats) + max(lats)) / 2
            target_point = (center_lon, center_lat)
            
            # Find buildings at center point
            landmark_ids = find_building_containing_point(building_gdf, target_point)
    
    # Extract configuration parameters
    building_class_id = kwargs.get("building_class_id", -3)
    landmark_value = -30
    tree_k = kwargs.get("tree_k", 0.6)
    tree_lad = kwargs.get("tree_lad", 1.0)
    colormap = kwargs.get("colormap", 'RdYlGn')
    progress_report = kwargs.get("progress_report", False)
    
    # Create a copy of voxel data for modifications
    voxel_data_for_mesh = voxel_data.copy()
    voxel_data_modified = voxel_data.copy()
    
    # Mark landmark buildings with special value in modified data
    voxel_data_modified = mark_building_by_id(voxel_data_modified, building_id_grid, landmark_ids, landmark_value)
    
    # In the mesh extraction data, change landmark buildings to a different value
    # so they won't be included in the surface mesh extraction
    voxel_data_for_mesh = mark_building_by_id(voxel_data_for_mesh, building_id_grid, landmark_ids, 0)
    
    # Find positions of all landmark voxels
    landmark_positions = np.argwhere(voxel_data_modified == landmark_value).astype(np.float64)
    if landmark_positions.shape[0] == 0:
        print(f"No landmarks found after marking buildings with IDs: {landmark_ids}")
        return None, None
    
    if progress_report:
        print(f"Found {landmark_positions.shape[0]} landmark voxels")
        print(f"Landmark building IDs: {landmark_ids}")
    
    # Extract building surface mesh excluding landmark buildings
    try:
        building_mesh = create_voxel_mesh(
            voxel_data_for_mesh,  # Use data where landmarks are excluded
            building_class_id,
            meshsize,
            building_id_grid=building_id_grid,
            mesh_type='open_air'
        )
        if building_mesh is None or len(building_mesh.faces) == 0:
            print("No non-landmark building surfaces found in voxel data.")
            return None, None
    except Exception as e:
        print(f"Error during mesh extraction: {e}")
        return None, None
    
    if progress_report:
        print(f"Processing landmark visibility for {len(building_mesh.faces)} faces...")
    
    # Get mesh properties
    face_centers = building_mesh.triangles_center
    face_normals = building_mesh.face_normals
    
    # Calculate domain bounds
    nx, ny, nz = voxel_data_modified.shape
    grid_bounds_voxel = np.array([[0,0,0],[nx, ny, nz]], dtype=np.float64)
    grid_bounds_real = grid_bounds_voxel * meshsize
    boundary_epsilon = meshsize * 0.05
    
    # Compute binary visibility for all faces using modified voxel data
    visibility_values = compute_landmark_visibility_for_all_faces(
        face_centers,
        face_normals,
        landmark_positions,
        voxel_data_modified,  # Use modified data with landmarks marked
        meshsize,
        tree_k,
        tree_lad,
        grid_bounds_real,
        boundary_epsilon
    )
    
    # Store visibility values in mesh metadata
    if not hasattr(building_mesh, 'metadata'):
        building_mesh.metadata = {}
    building_mesh.metadata['landmark_visibility'] = visibility_values
    
    # Count visible faces (excluding NaN boundary faces)
    valid_mask = ~np.isnan(visibility_values)
    n_valid = np.sum(valid_mask)
    n_visible = np.sum(visibility_values[valid_mask] > 0.5)
    
    if progress_report:
        print(f"Landmark visibility statistics:")
        print(f"  Total faces: {len(visibility_values)}")
        print(f"  Valid faces: {n_valid}")
        print(f"  Faces with landmark visibility: {n_visible} ({n_visible/n_valid*100:.1f}%)")
    
    # Optional OBJ export
    obj_export = kwargs.get("obj_export", False)
    if obj_export:
        output_dir = kwargs.get("output_directory", "output")
        output_file_name = kwargs.get("output_file_name", "surface_landmark_visibility")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Apply colormap to visibility values for visualization
            cmap = plt.cm.get_cmap(colormap)
            face_colors = np.zeros((len(visibility_values), 4))
            
            for i, val in enumerate(visibility_values):
                if np.isnan(val):
                    face_colors[i] = [0.7, 0.7, 0.7, 1.0]  # Gray for boundary faces
                else:
                    face_colors[i] = cmap(val)
            
            building_mesh.visual.face_colors = face_colors
            building_mesh.export(f"{output_dir}/{output_file_name}.obj")
            print(f"Exported surface mesh to {output_dir}/{output_file_name}.obj")
        except Exception as e:
            print(f"Error exporting mesh: {e}")
    
    return building_mesh, voxel_data_modified