"""
Module to create a Region object and download OpenStreetMap data.
"""

import osmnx as ox


class Region:
    """
    Represents a geographic region and provides methods to download OpenStreetMap data.
    """
    def __init__(self, region, network_type):
        """
        Initializes Region object with the specified region and network type.
        :param region: name or area identifier for region of interest
        :param network_type: type of street network to download
        """
        self.area = region
        self.network_type = network_type

    def download_osm(self):
        """
        Downloads OpenStreetMap data for the specified region and network type.
        :return tuple or None: tuple containing edge data frame and OSM network graph.
        :exception: Returns None if an error occurs.
        """
        try:
            print(f"Downloading OpenStreetMap data for {self.area}...")
            graph = ox.graph_from_place(self.area, network_type=self.network_type)
            print("Download complete.")
            _, edges_df = ox.graph_to_gdfs(graph)
            return edges_df, graph
        except Exception as error:
            print(f"Error downloading OpenStreetMap data: {error}")
            return None
