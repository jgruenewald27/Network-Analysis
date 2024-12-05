"""
Module to calculate and explore edge betweenness centrality using Networkx.
"""

import os
import networkx as nx
import osmnx as ox
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


class NetworkxCentrality:
    """
    Class to calculate and explore edge betweenness centrality using NetworkX.
    """
    def __init__(self, weight):
        """
        Initializes a NetworkxCentrality object with the specified weight.
        :param weight: used in centrality calculations
        """
        self.weight = weight
        self.centrality_short_gdf = None
        self.centrality_fast_gdf = None

    def get_centrality_short(self, graph, edges_df, output_file=None):
        """
        Calculates edge betweenness centrality using the shortest routes and returns a DataFrame.
        :param graph: Networkx graph object
        :param edges_df: DataFrame containing edge information
        :param output_file: path to save GeoDataFrame. Default None
        :return pd.DataFrame: DataFrame containing edge betweenness centrality values
        """
        betweenness_centrality = nx.edge_betweenness_centrality(
            graph, weight=self.weight
        )
        centrality_short_df = pd.DataFrame(
            index=betweenness_centrality.keys(),
            data=betweenness_centrality.values()
        )
        centrality_short_df.reset_index(inplace=True)
        centrality_short_df.columns = ["u", "v", "key", "centrality"]
        centrality_short_df = centrality_short_df.set_index(["u", "v", "key"])
        centrality_short_df = centrality_short_df.join(edges_df[["osmid", "geometry"]])

        for col in centrality_short_df.columns:
            if centrality_short_df[col].apply(type).eq(list).any():
                centrality_short_df[col] = centrality_short_df[col].apply(
                    lambda x: str(x) if isinstance(x, list) else x
                )

        self.centrality_short_gdf = gpd.GeoDataFrame(centrality_short_df, crs=4326)

        if output_file:
            self.centrality_short_gdf.to_file(output_file, driver="GPKG")

        return centrality_short_df

    def get_centrality_fast(self, graph, edges_df, output_file=None):
        """
        Calculates edge betweenness centrality using the fastest routes. Returns DataFrame.
        :param graph: Networkx graph object
        :param edges_df: DataFrame containing edge information.
        :param output_file: path to save GeoDataFrame. Default None
        :return pd.DataFrame: DataFrame containing edge betweenness centrality values
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

        graph_with_speeds = ox.add_edge_speeds(graph, hwy_speeds)
        graph_travel_time = ox.add_edge_travel_times(graph_with_speeds)

        betweenness_centrality_time = nx.edge_betweenness_centrality(
            graph_travel_time, weight="travel_time"
        )
        centrality_fast_df = pd.DataFrame(
            index=betweenness_centrality_time.keys(),
            data=betweenness_centrality_time.values(),
        )
        centrality_fast_df.reset_index(inplace=True)
        centrality_fast_df.columns = ["u", "v", "key", "centrality"]
        centrality_fast_df = centrality_fast_df.set_index(["u", "v", "key"])
        centrality_fast_df = centrality_fast_df.join(edges_df[["osmid", "geometry"]])

        for col in centrality_fast_df.columns:
            if centrality_fast_df[col].apply(type).eq(list).any():
                centrality_fast_df[col] = centrality_fast_df[col].apply(
                    lambda x: str(x) if isinstance(x, list) else x
                )

        self.centrality_fast_gdf = gpd.GeoDataFrame(centrality_fast_df, crs=4326)

        if output_file:
            self.centrality_fast_gdf.to_file(output_file, driver="GPKG")

        return centrality_fast_df

    def explore_centrality(
        self,
        centrality_gdf,
        weight,
        output_folder=None,
        image_name="Centrality_Plot.png",
    ):
        """
        Plots the edge betweenness centrality on a map.
        :param centrality_gdf: containing edge betweenness centrality values
        :param weight: used in centrality calculations
        :param output_folder: path to save plot. Default is None
        :param image_name: of plot. Default is "Centrality_Plot.png"
        """
        title = (
            f"Betweenness centrality using the {'shortest' if weight == 'length' else 'fastest'} routes"
        )
        if centrality_gdf is not None:
            plot = centrality_gdf.plot(column="centrality", cmap="magma_r", legend=True)

            plot.set_xlabel("Longitude")
            plot.set_ylabel("Latitude")

            lat_formatter = "{:.2f}".format
            plot.yaxis.set_major_formatter(lat_formatter)

            plt.title(title)

            if output_folder:
                output_image_path = os.path.join(output_folder, image_name)
                plt.savefig(output_image_path, bbox_inches="tight")
        else:
            print(f"Centrality data not available. Run {title.lower()} first.")

    def explore_centrality_short(self, output_folder=None):
        """
        Plots the edge betweenness centrality using the shortest routes on a map.
        :param output_folder: path to save plot. Default is None
        """
        self.explore_centrality(
            centrality_gdf=self.centrality_short_gdf,
            weight=self.weight,
            output_folder=output_folder,
            image_name="Centrality_Plot_ShortestRoutes.png",
        )

    def explore_centrality_fast(self, output_folder=None):
        """
        Plots the edge betweenness centrality using the fastest routes on a map.
        :param output_folder: path to save plot. Default is None
        """
        self.explore_centrality(
            centrality_gdf=self.centrality_fast_gdf,
            weight=self.weight,
            output_folder=output_folder,
            image_name="Centrality_Plot_FastestRoutes.png",
        )
