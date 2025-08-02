"""
This package provides high-performance GPS track processing, route density analysis,
and geospatial utilities through Rust-compiled Python extensions.
"""

from ._fastgeotoolkit import (
    # Core processing functions
    process_gpx_files,
    decode_polyline,
    process_polylines,
    
    # Analysis functions
    calculate_track_statistics,
    validate_coordinates,
    find_track_intersections,
    calculate_coverage_area,
    cluster_tracks_by_similarity,
    
    # Manipulation functions
    simplify_coordinates,
    merge_nearby_tracks,
    split_track_by_gaps,
    filter_coordinates_by_bounds,
    
    # Conversion functions
    coordinates_to_geojson,
    coordinates_to_polyline,
    export_to_gpx,
    
    # Utility functions
    calculate_distance_between_points,
    get_bounding_box,
    resample_track,
    get_file_info,
    extract_file_metadata,
)

from .types import (
    Coordinate,
    HeatmapTrack,
    HeatmapResult,
    ValidationResult,
    TrackStatistics,
    FileInfo,
    IntersectionPoint,
    TrackCluster,
)

from .utils import (
    load_gpx_file,
    load_multiple_gpx_files,
    save_heatmap_to_geojson,
    visualize_heatmap,
    create_folium_map,
)

__version__ = "0.1.7"
__author__ = "a0a7"
__email__ = "contact@a0.ax"
__license__ = "MIT"

__all__ = [
    # Core functions
    "process_gpx_files",
    "decode_polyline",
    "process_polylines",
    
    # Analysis functions
    "calculate_track_statistics",
    "validate_coordinates",
    "find_track_intersections",
    "calculate_coverage_area",
    "cluster_tracks_by_similarity",
    
    # Manipulation functions
    "simplify_coordinates",
    "merge_nearby_tracks",
    "split_track_by_gaps",
    "filter_coordinates_by_bounds",
    
    # Conversion functions
    "coordinates_to_geojson",
    "coordinates_to_polyline",
    "export_to_gpx",
    
    # Utility functions
    "calculate_distance_between_points",
    "get_bounding_box",
    "resample_track",
    "get_file_info",
    "extract_file_metadata",
    
    # Python utilities
    "load_gpx_file",
    "load_multiple_gpx_files",
    "save_heatmap_to_geojson",
    "visualize_heatmap",
    "create_folium_map",
    
    # Types
    "Coordinate",
    "HeatmapTrack",
    "HeatmapResult",
    "ValidationResult",
    "TrackStatistics",
    "FileInfo",
    "IntersectionPoint",
    "TrackCluster",
]
