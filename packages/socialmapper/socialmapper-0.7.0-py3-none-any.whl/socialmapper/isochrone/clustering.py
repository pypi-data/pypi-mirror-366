#!/usr/bin/env python3
"""Modern Intelligent Spatial Clustering Engine for Isochrone Generation.

This module implements advanced POI clustering using machine learning algorithms
to optimize network downloads and processing for large-scale isochrone generation.

Key Features:
- DBSCAN clustering with haversine distance metric
- Intelligent cluster sizing based on travel time requirements
- Advanced spatial optimization algorithms
- Performance monitoring and benchmarking
"""

import threading
import time
from dataclasses import dataclass
from typing import Any

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
from shapely.geometry import Point
from sklearn.cluster import DBSCAN

# Setup logging
from ..console import get_logger
from .travel_modes import TravelMode, get_default_speed, get_highway_speeds, get_network_type

logger = get_logger(__name__)


@dataclass
class ClusterMetrics:
    """Performance metrics for clustering operations."""

    total_pois: int
    num_clusters: int
    avg_cluster_size: float
    max_cluster_size: int
    min_cluster_size: int
    clustering_time_seconds: float
    network_downloads_saved: int
    estimated_time_savings_percent: float


class IntelligentPOIClusterer:
    """Advanced POI clustering using machine learning algorithms."""

    def __init__(self, max_cluster_radius_km: float = 15.0, min_cluster_size: int = 2):
        """Initialize the intelligent clusterer.

        Args:
            max_cluster_radius_km: Maximum radius for clustering in kilometers
            min_cluster_size: Minimum number of POIs to form a cluster
        """
        self.max_cluster_radius_km = max_cluster_radius_km
        self.min_cluster_size = min_cluster_size
        self._lock = threading.Lock()

    def cluster_pois(self, pois: list[dict], travel_time_minutes: int = 15) -> list[list[dict]]:
        """Cluster POIs using DBSCAN with geographic distance.

        Args:
            pois: List of POI dictionaries with 'lat' and 'lon' keys
            travel_time_minutes: Travel time limit to adjust clustering parameters

        Returns:
            List of POI clusters (each cluster is a list of POIs)
        """
        start_time = time.time()

        if len(pois) <= 1:
            return [pois]

        # Extract coordinates
        coords = np.array([[poi["lat"], poi["lon"]] for poi in pois])

        # Adjust clustering radius based on travel time
        # Larger travel times allow for larger clusters
        adjusted_radius = min(
            self.max_cluster_radius_km, self.max_cluster_radius_km * (travel_time_minutes / 15.0)
        )

        # Use DBSCAN clustering with haversine metric
        # eps in radians for haversine distance
        eps_radians = adjusted_radius / 6371.0  # Earth radius in km

        clustering = DBSCAN(
            eps=eps_radians, min_samples=self.min_cluster_size, metric="haversine"
        ).fit(np.radians(coords))

        # Group POIs by cluster
        clusters = {}
        for idx, label in enumerate(clustering.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(pois[idx])

        # Handle noise points (label = -1) as individual clusters
        result = []
        for label, cluster_pois in clusters.items():
            if label == -1:  # Noise points
                result.extend([[poi] for poi in cluster_pois])
            else:
                result.append(cluster_pois)

        time.time() - start_time

        # Log clustering results
        num_clusters = len(result)
        network_downloads_saved = len(pois) - num_clusters
        savings_percent = (network_downloads_saved / len(pois)) * 100 if len(pois) > 0 else 0

        logger.info(
            f"Clustered {len(pois)} POIs into {num_clusters} clusters "
            f"(saved {network_downloads_saved} downloads, {savings_percent:.1f}% reduction)"
        )

        return result

    def get_cluster_metrics(self, pois: list[dict], clusters: list[list[dict]]) -> ClusterMetrics:
        """Calculate detailed metrics for clustering performance."""
        cluster_sizes = [len(cluster) for cluster in clusters]

        return ClusterMetrics(
            total_pois=len(pois),
            num_clusters=len(clusters),
            avg_cluster_size=np.mean(cluster_sizes) if cluster_sizes else 0,
            max_cluster_size=max(cluster_sizes) if cluster_sizes else 0,
            min_cluster_size=min(cluster_sizes) if cluster_sizes else 0,
            clustering_time_seconds=0,  # Set externally
            network_downloads_saved=len(pois) - len(clusters),
            estimated_time_savings_percent=(
                ((len(pois) - len(clusters)) / len(pois) * 100) if len(pois) > 0 else 0
            ),
        )


class OptimizedPOICluster:
    """Represents an optimized cluster of POIs with advanced spatial algorithms."""

    def __init__(self, cluster_id: int | str, pois: list[dict[str, Any]]):
        self.cluster_id = cluster_id
        self.pois = pois
        self.centroid = self._calculate_centroid()
        self.radius_km = self._calculate_radius()
        self.network = None
        self.network_crs = None
        self.bbox = self._calculate_bbox()

    def _calculate_centroid(self) -> tuple[float, float]:
        """Calculate the geographic centroid of the cluster."""
        if not self.pois:
            return (0.0, 0.0)

        lats = [poi["lat"] for poi in self.pois]
        lons = [poi["lon"] for poi in self.pois]
        return (np.mean(lats), np.mean(lons))

    def _calculate_radius(self) -> float:
        """Calculate the maximum radius from centroid to any POI."""
        if len(self.pois) <= 1:
            return 0.0

        centroid_lat, centroid_lon = self.centroid
        max_distance = 0.0

        for poi in self.pois:
            distance = self._haversine_distance(centroid_lat, centroid_lon, poi["lat"], poi["lon"])
            max_distance = max(max_distance, distance)

        return max_distance

    def _calculate_bbox(self) -> tuple[float, float, float, float]:
        """Calculate bounding box (min_lat, min_lon, max_lat, max_lon)."""
        if not self.pois:
            return (0.0, 0.0, 0.0, 0.0)

        lats = [poi["lat"] for poi in self.pois]
        lons = [poi["lon"] for poi in self.pois]

        return (min(lats), min(lons), max(lats), max(lons))

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points in kilometers."""
        earth_radius_km = 6371.0  # Earth radius in kilometers

        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))

        return earth_radius_km * c

    def get_network_bbox(
        self, travel_time_minutes: int, buffer_km: float = 2.0
    ) -> tuple[float, float, float, float]:
        """Get optimized bounding box for network download."""
        min_lat, min_lon, max_lat, max_lon = self.bbox

        # Calculate buffer based on travel time and cluster size
        # Larger clusters and longer travel times need bigger buffers
        adaptive_buffer = buffer_km + (travel_time_minutes / 15.0) + (len(self.pois) / 10.0)

        # Convert buffer to approximate degrees
        buffer_deg = adaptive_buffer / 111.0

        return (
            min_lat - buffer_deg,
            min_lon - buffer_deg,
            max_lat + buffer_deg,
            max_lon + buffer_deg,
        )

    def __len__(self):
        """Return the number of POIs in this cluster."""
        return len(self.pois)

    def __repr__(self):
        """Return string representation of the cluster."""
        return f"OptimizedPOICluster(id={self.cluster_id}, pois={len(self.pois)}, radius={self.radius_km:.2f}km)"


def create_optimized_clusters(
    pois: list[dict[str, Any]],
    travel_time_minutes: int = 15,
    max_cluster_radius_km: float = 15.0,
    min_cluster_size: int = 2,
) -> list[OptimizedPOICluster]:
    """Create optimized POI clusters using intelligent spatial algorithms.

    Args:
        pois: List of POI dictionaries with 'lat' and 'lon' keys
        travel_time_minutes: Travel time limit for isochrone generation
        max_cluster_radius_km: Maximum clustering radius in kilometers
        min_cluster_size: Minimum POIs per cluster

    Returns:
        List of OptimizedPOICluster objects
    """
    if not pois:
        return []

    # Use intelligent clusterer
    clusterer = IntelligentPOIClusterer(
        max_cluster_radius_km=max_cluster_radius_km, min_cluster_size=min_cluster_size
    )

    poi_clusters = clusterer.cluster_pois(pois, travel_time_minutes)

    # Convert to OptimizedPOICluster objects
    optimized_clusters = []
    for i, cluster_pois in enumerate(poi_clusters):
        cluster = OptimizedPOICluster(cluster_id=i, pois=cluster_pois)
        optimized_clusters.append(cluster)

    return optimized_clusters


def download_network_for_cluster(
    cluster: OptimizedPOICluster,
    travel_time_minutes: int,
    network_buffer_km: float = 2.0,
    travel_mode: TravelMode = TravelMode.DRIVE,
) -> bool:
    """Download and prepare road network for an optimized cluster.

    Args:
        cluster: OptimizedPOICluster to download network for
        travel_time_minutes: Travel time limit in minutes
        network_buffer_km: Additional buffer around cluster
        travel_mode: Mode of travel (walk, bike, drive)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get network type, default speed, and highway speeds for travel mode
        network_type = get_network_type(travel_mode)
        default_speed = get_default_speed(travel_mode)
        highway_speeds = get_highway_speeds(travel_mode)

        if len(cluster.pois) == 1:
            # Single POI - use point-based download
            poi = cluster.pois[0]
            graph = ox.graph_from_point(
                (poi["lat"], poi["lon"]),
                network_type=network_type,
                dist=travel_time_minutes * 1000 + network_buffer_km * 1000,
            )
        else:
            # Multiple POIs - use optimized bounding box
            min_lat, min_lon, max_lat, max_lon = cluster.get_network_bbox(
                travel_time_minutes, network_buffer_km
            )

            # OSMnx expects bbox as (left, bottom, right, top) = (min_lon, min_lat, max_lon, max_lat)
            osm_bbox = (min_lon, min_lat, max_lon, max_lat)
            graph = ox.graph_from_bbox(bbox=osm_bbox, network_type=network_type)

        # Add speeds and travel times with mode-specific defaults
        # OSMnx will use:
        # 1. Existing maxspeed tags from OSM data
        # 2. Highway-type-specific speeds we provide
        # 3. Mean of observed speeds for unmapped highway types
        # 4. Fallback speed as last resort
        graph = ox.add_edge_speeds(graph, hwy_speeds=highway_speeds, fallback=default_speed)
        graph = ox.add_edge_travel_times(graph)

        # Apply mode-specific speed adjustments for more realistic isochrones
        if travel_mode == TravelMode.WALK:
            # For walking, ensure speeds don't exceed reasonable walking speeds
            for u, v, data in graph.edges(data=True):
                if 'speed_kph' in data and data['speed_kph'] > 7.0:
                    data['speed_kph'] = 5.0  # Set to normal walking speed
                    data['travel_time'] = data['length'] / (data['speed_kph'] * 1000 / 3600)
        elif travel_mode == TravelMode.BIKE:
            # For biking, cap speeds to reasonable cycling speeds
            for u, v, data in graph.edges(data=True):
                if 'speed_kph' in data and data['speed_kph'] > 30.0:
                    data['speed_kph'] = 15.0  # Set to normal cycling speed
                    data['travel_time'] = data['length'] / (data['speed_kph'] * 1000 / 3600)

        graph = ox.project_graph(graph)

        # Store network in cluster
        cluster.network = graph
        cluster.network_crs = graph.graph["crs"]

        # Log speed statistics for debugging
        speeds = [data.get('speed_kph', 0) for u, v, data in graph.edges(data=True)]
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            min_speed = min(speeds)
            max_speed = max(speeds)
            logger.info(
                f"Network speeds for {travel_mode.value} mode - "
                f"avg: {avg_speed:.1f} km/h, min: {min_speed:.1f} km/h, max: {max_speed:.1f} km/h"
            )

        logger.debug(
            f"Downloaded network for cluster {cluster.cluster_id}: "
            f"{len(graph.nodes)} nodes, {len(graph.edges)} edges"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to download network for cluster {cluster.cluster_id}: {e}")
        return False


def create_isochrone_from_poi_with_network(
    poi: dict[str, Any],
    network: nx.MultiDiGraph,
    network_crs: str,
    travel_time_minutes: int,
    travel_mode: TravelMode = TravelMode.DRIVE,
) -> gpd.GeoDataFrame | None:
    """Create isochrone for a POI using pre-downloaded network.

    Args:
        poi: POI dictionary with 'lat' and 'lon'
        network: Pre-downloaded road network
        network_crs: CRS of the network
        travel_time_minutes: Travel time limit in minutes
        travel_mode: Mode of travel (walk, bike, drive)

    Returns:
        GeoDataFrame with isochrone or None if failed
    """
    try:
        # Import validation utilities
        from ..util.coordinate_validation import (
            validate_coordinate_point,
        )

        # Validate POI coordinates using Pydantic
        lat = poi.get("lat")
        lon = poi.get("lon")

        if lat is None or lon is None:
            logger.error(f"POI {poi.get('id', 'unknown')} missing lat/lon coordinates")
            return None

        validated_coord = validate_coordinate_point(lat, lon, f"poi_{poi.get('id', 'unknown')}")
        if not validated_coord:
            logger.error(
                f"POI {poi.get('id', 'unknown')} has invalid coordinates: lat={lat}, lon={lon}"
            )
            return None

        # Create point from validated coordinates
        poi_point = validated_coord.to_point()

        # Use PyProj transformer directly to avoid single-point GeoSeries transformation
        # This bypasses the problematic GeoPandas to_crs() call that triggers the NumPy warning
        import pyproj

        transformer = pyproj.Transformer.from_crs("EPSG:4326", network_crs, always_xy=True)

        # Transform the single point directly using PyProj (avoiding NumPy array operations)
        poi_x_proj, poi_y_proj = transformer.transform(poi_point.x, poi_point.y)

        # Find nearest node using the transformed coordinates
        poi_node = ox.nearest_nodes(network, X=poi_x_proj, Y=poi_y_proj)

        # Generate subgraph based on travel time
        subgraph = nx.ego_graph(
            network,
            poi_node,
            radius=travel_time_minutes * 60,  # Convert to seconds
            distance="travel_time",
        )

        if len(subgraph.nodes) == 0:
            logger.warning(f"No reachable nodes for POI {poi.get('id', 'unknown')}")
            return None

        # Create isochrone polygon from reachable nodes
        node_points = [Point((data["x"], data["y"])) for node, data in subgraph.nodes(data=True)]

        if len(node_points) < 3:
            logger.warning(
                f"Insufficient nodes ({len(node_points)}) to create polygon for POI {poi.get('id', 'unknown')}"
            )
            return None

        # Create GeoDataFrame from node points
        nodes_gdf = gpd.GeoDataFrame(geometry=node_points, crs=network_crs)

        # Use convex hull to create the isochrone polygon
        isochrone = nodes_gdf.union_all().convex_hull

        # Create result GeoDataFrame
        isochrone_gdf = gpd.GeoDataFrame(geometry=[isochrone], crs=network_crs).to_crs("EPSG:4326")

        # Add metadata
        isochrone_gdf["poi_id"] = poi.get("id", "unknown")
        isochrone_gdf["poi_name"] = poi.get("tags", {}).get(
            "name", f"poi_{poi.get('id', 'unknown')}"
        )
        isochrone_gdf["travel_time_minutes"] = travel_time_minutes
        isochrone_gdf["travel_mode"] = travel_mode.value

        return isochrone_gdf

    except Exception as e:
        logger.error(f"Failed to create isochrone for POI {poi.get('id', 'unknown')}: {e}")
        return None


def benchmark_clustering_performance(
    pois: list[dict[str, Any]], travel_time_minutes: int = 15, max_cluster_radius_km: float = 15.0
) -> dict[str, Any]:
    """Benchmark clustering performance and provide optimization recommendations.

    Args:
        pois: List of POI dictionaries
        travel_time_minutes: Travel time limit
        max_cluster_radius_km: Maximum clustering radius

    Returns:
        Dictionary with performance metrics and recommendations
    """
    start_time = time.time()

    # Test different clustering parameters
    clusterer = IntelligentPOIClusterer(
        max_cluster_radius_km=max_cluster_radius_km, min_cluster_size=2
    )

    clusters = clusterer.cluster_pois(pois, travel_time_minutes)
    clustering_time = time.time() - start_time

    # Calculate metrics
    metrics = clusterer.get_cluster_metrics(pois, clusters)
    metrics.clustering_time_seconds = clustering_time

    # Performance analysis
    total_downloads_original = len(pois)
    total_downloads_optimized = len(clusters)
    time_savings_estimate = (
        total_downloads_original - total_downloads_optimized
    ) * 30  # 30s per download estimate

    return {
        "metrics": metrics,
        "performance": {
            "original_downloads": total_downloads_original,
            "optimized_downloads": total_downloads_optimized,
            "downloads_saved": total_downloads_original - total_downloads_optimized,
            "estimated_time_savings_seconds": time_savings_estimate,
            "clustering_overhead_seconds": clustering_time,
            "net_time_savings_seconds": time_savings_estimate - clustering_time,
        },
        "recommendations": {
            "optimal_radius_km": max_cluster_radius_km,
            "efficiency_rating": (
                "Excellent"
                if metrics.estimated_time_savings_percent > 50
                else "Good"
                if metrics.estimated_time_savings_percent > 25
                else "Fair"
            ),
        },
    }
