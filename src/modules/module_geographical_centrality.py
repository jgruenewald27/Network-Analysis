"""
Module to calculate geographically adapted betweenness centrality
"""

import os
import numpy as np
import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt


class GeographicalCentrality:
    """
    Class to calculate geographically adapted betweenness centrality
    """
    def __init__(self, study_area, weight, graph, edges_df, number_of_routes):
        """
        Initialize GeographicalCentrality instance.
        :param study_area: representing the study area
        :param weight: The weight used in routing calculations
        :param graph: The road network graph
        :param edges_df: DataFrame containing edge information
        :param number_of_routes: The number of random routes to generate
        """
        self.study_area = study_area
        self.weight = weight
        self.graph = graph
        self.edges_df = edges_df
        self.number_of_routes = number_of_routes
        self.poly_study_area = None
        self.routes_gdf = None
        self.graph_with_travel_time = None
        self.centrality_geographical_gdf = None

    def create_study_area_polygon(self):
        """
        Create a study area polygon based on the specified location.
        :return GeoDataFrame: representation of the polygon.
        """
        location_string = self.study_area.area
        self.poly_study_area = ox.geocode_to_gdf(location_string)
        return self.poly_study_area

    def random_points_in_polygon(self, number):
        """
        Generate random points within the study area polygon.
        :param number: The number of random points to generate
        :returns GeoDataFrame: containing random points within the polygon.
        Note: The study area polygon must be set using the 'create_study_area_polygon' method
        before calling this function.
        """
        polygon = self.poly_study_area.geometry.values[0]
        minx, miny, maxx, maxy = polygon.bounds
        x = np.random.uniform(minx, maxx, number)
        y = np.random.uniform(miny, maxy, number)
        points = [Point(xy) for xy in zip(x, y)]
        gdf_points = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
        spatial_join = gpd.tools.sjoin(
            gdf_points, self.poly_study_area, predicate="within", how="left"
        )
        pts_in_poly = gdf_points[spatial_join.index_right == 0.0]
        while len(pts_in_poly) < number:
            additional_points = number - len(pts_in_poly)
            x_loop = np.random.uniform(minx, maxx, size=additional_points)
            y_loop = np.random.uniform(miny, maxy, size=additional_points)
            add_points = [Point(xy) for xy in zip(x_loop, y_loop)]
            additional_gdf = gpd.GeoDataFrame(geometry=add_points, crs="EPSG:4326")
            spatial_join_loop = gpd.tools.sjoin(
                additional_gdf, self.poly_study_area, predicate="within", how="left"
            )
            pts_loop = additional_gdf[spatial_join_loop.index_right == 0.0]
            pts_in_poly = pd.concat([pts_in_poly, pts_loop], ignore_index=True)
        pts_in_poly["x"] = pts_in_poly["geometry"].x
        pts_in_poly["y"] = pts_in_poly["geometry"].y
        return pts_in_poly

    def get_graph_travel_time(self):
        """
        Calculate travel times on graph edges based on specified road speeds.
        :returns graph_with_travel_time: Networkx graph with edge travel times.
        Note: The graph must be set using the 'graph' attribute before calling this function.
        """
        hwy_speeds = {
            "motorway": 100,
            "motorway_link": 60,
            "motorroad": 90,
            "trunk": 85,
            "trunk_link": 60,
            "primary": 65,
            "primary_link": 50,
            "secondary": 60,
            "secondary_link": 50,
            "tertiary": 50,
            "tertiary_link": 40,
            "unclassified": 30,
            "residential": 30,
            "living_street": 10,
            "service": 20,
            "road": 20,
            "track": 15,
        }
        graph_with_speeds = ox.add_edge_speeds(self.graph, hwy_speeds)
        if graph_with_speeds is None:
            raise ValueError("Failed to add edge speeds to the graph.")
        graph_travel_time = ox.add_edge_travel_times(graph_with_speeds)
        self.graph_with_travel_time = graph_travel_time
        return self.graph_with_travel_time

    def generate_random_routes(self, graph_version):
        """
        Generate random routes on the specified graph.
        :param graph_version: The network graph version
        :returns routes_gdf: GeoDataFrame containing random routes.
        Note: The study area polygon, graph, and the number of routes must be set before calling this function.
        """
        all_sample_points = []
        count = 0

        while count < self.number_of_routes:
            sample_points = self.random_points_in_polygon(2)
            nodes = [
                ox.nearest_nodes(graph_version, x, y)
                for x, y in zip(sample_points["x"], sample_points["y"])
            ]
            origin_node, destination_node = nodes
            random_route = ox.shortest_path(
                graph_version, origin_node, destination_node, weight=self.weight
            )

            while origin_node == destination_node or random_route is None:
                sample_points = self.random_points_in_polygon(2)
                nodes = [
                    ox.nearest_nodes(graph_version, x, y)
                    for x, y in zip(sample_points["x"], sample_points["y"])
                ]
                origin_node, destination_node = nodes
                random_route = ox.shortest_path(
                    graph_version, origin_node, destination_node, weight=self.weight
                )

            if random_route is None:
                raise ValueError("Failed to generate a valid random route.")
            one_route_gdf = ox.utils_graph.route_to_gdf(
                graph_version, random_route, weight=self.weight
            )
            all_sample_points.append(one_route_gdf)
            count += 1

        routes_gdf = pd.concat(all_sample_points)
        self.routes_gdf = routes_gdf
        return routes_gdf

    def analyze_centrality(self):
        """
        Analyze centrality of the edges using the generated routes.
        Note: The 'routes_gdf' and 'edges_df' must be set before calling this function.
        """
        if self.routes_gdf is not None:
            centrality_geo = pd.DataFrame(
                self.routes_gdf["osmid"].groupby(["u", "v", "key"]).count()
            )
            centrality_geo.columns = ["centrality"]
            centrality_geo_join_edge_df = centrality_geo.join(
                self.edges_df[["osmid", "geometry"]]
            )
            for col in centrality_geo_join_edge_df.columns:
                if centrality_geo_join_edge_df[col].apply(type).eq(list).any():
                    centrality_geo_join_edge_df[col] = centrality_geo_join_edge_df[
                        col
                    ].apply(lambda x: str(x) if isinstance(x, list) else x)
            centrality_geo_gdf = gpd.GeoDataFrame(centrality_geo_join_edge_df, crs=4326)
            self.centrality_geographical_gdf = centrality_geo_gdf

    def save_data_in_file(self, output_folder=None, output_file=None, image_name=None):
        """
        Save centrality data to files.
        :param output_folder: Output folder path to save the image
        :param output_file: Output file path to save the GeoDataFrame
        :param image_name: Name of the output image file
        Note: The 'centrality_geographical_gdf' must be available before calling this function.
        """
        plot = self.centrality_geographical_gdf.plot(
            column="centrality", cmap="magma_r", legend=True
        )
        plot.set_xlabel("Longitude")
        plot.set_ylabel("Latitude")
        lat_formatter = "{:.2f}".format
        plot.yaxis.set_major_formatter(lat_formatter)
        plt.title(f"Geographical Centrality {self.weight} routes={self.number_of_routes}")
        if output_folder:
            output_image_path = os.path.join(output_folder, image_name)
            plt.savefig(output_image_path, bbox_inches="tight")
        if output_file:
            self.centrality_geographical_gdf.to_file(output_file, driver="GPKG")
        else:
            print("Storage of data failed.")
