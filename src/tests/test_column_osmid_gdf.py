"""
Unit test to check if the osm-id of generated routes GeoDataFrame is present in all rows.
"""

import unittest
import geopandas as gpd
from shapely.geometry import Polygon
import osmnx as ox
from ..modules.module_geographical_centrality import GeographicalCentrality


class TestGeographicalCentrality(unittest.TestCase):
    """
    A test class for the GeographicalCentrality module.
    """
    def setUp(self):
        """
        Set up the test environment with an instance of
        GeographicalCentrality, study area and a graph.
        """
        self.gc_instance = GeographicalCentrality(
            study_area=None,
            weight="length",
            graph=None,
            edges_df=None,
            number_of_routes=50
        )

        wiesenbach_polygon_coords = Polygon([
            (8.769, 49.402),
            (8.769, 49.411),
            (8.782, 49.411),
            (8.782, 49.402),
            (8.769, 49.402)
        ])

        self.gc_instance.poly_study_area = gpd.GeoDataFrame(
            geometry=[wiesenbach_polygon_coords], crs="EPSG:4326")
        self.gc_instance.graph = ox.graph_from_place(
            "Wiesenbach, Germany", network_type="drive")

    def test_generate_random_routes_osmid(self):
        """
        Test if the osm-id of generated routes GeoDataFrame is present in all rows.
        """
        routes_gdf = self.gc_instance.generate_random_routes(self.gc_instance.graph)
        print("Number of rows in routes_gdf:", len(routes_gdf))

        self.assertIn("osmid", routes_gdf.columns)
        self.assertTrue(routes_gdf["osmid"].notnull().all())


if __name__ == '__main__':
    unittest.main()
