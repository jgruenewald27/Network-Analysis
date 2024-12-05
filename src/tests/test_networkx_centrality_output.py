"""
Test the creation of GeoDataFrames during networkx centrality calculations.
"""

import unittest
import geopandas as gpd
from ..modules.module_networkx_centrality import NetworkxCentrality
from ..modules.module_create_region import Region


class TestGeoDataFrameCreation(unittest.TestCase):
    """
    Class for testing the creation of GeoDataFrames during networkx centrality calculations.
    """
    def test_output_geo_dataframes_creation(self):
        """
        Test the creation of GeoDataFrames during networkx centrality calculations.
        """
        # Initialize a sample region
        sample_region = Region(region="Wiesenbach, Germany", network_type="drive")
        osm_data = sample_region.download_osm()
        if osm_data is None:
            self.fail("Failed to download OSM data for testing.")

        edges_df, graph = osm_data
        centrality_calculator = NetworkxCentrality(weight="length")

        # Call the method to calculate centrality_short_gdf
        print("Calculating centrality_short_gdf...")
        centrality_calculator.get_centrality_short(graph, edges_df)
        centrality_short_gdf = centrality_calculator.centrality_short_gdf

        # Verify that centrality_short_gdf is created and has the expected columns
        self.assertIsInstance(centrality_short_gdf, gpd.GeoDataFrame)
        expected_columns_short = ['centrality', 'geometry', 'osmid']
        assert sorted(list(centrality_short_gdf.columns)) == sorted(expected_columns_short)
        print("centrality_short_gdf is created and has the expected columns.")

        # Check "centrality" values are under 1 and not null
        self.assertTrue(centrality_short_gdf['centrality'].notnull().all())
        self.assertTrue((centrality_short_gdf['centrality'] < 1).all())
        print("centrality_short_gdf values are under 1 and not null.")

        # Call the method to calculate centrality_fast_gdf
        print("Calculating centrality_fast_gdf...")
        centrality_calculator.get_centrality_fast(graph, edges_df)
        centrality_fast_gdf = centrality_calculator.centrality_fast_gdf

        # Verify that centrality_fast_gdf is created and has the expected columns
        self.assertIsInstance(centrality_fast_gdf, gpd.GeoDataFrame)
        expected_columns_fast = ['centrality', 'geometry', 'osmid']
        assert sorted(list(centrality_fast_gdf.columns)) == sorted(expected_columns_fast)
        print("centrality_fast_gdf is created and has the expected columns.")

        # Check "centrality" values are under 1 and not null
        self.assertTrue(centrality_fast_gdf['centrality'].notnull().all())
        self.assertTrue((centrality_fast_gdf['centrality'] < 1).all())
        print("centrality_fast_gdf values are under 1 and not null.")


if __name__ == '__main__':
    unittest.main()
