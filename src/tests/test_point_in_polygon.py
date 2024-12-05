"""
Unit test to check if random sampled points are within the provided polygon
for geographical centrality
"""

import unittest
import geopandas as gpd
from shapely.geometry import Polygon
from ..modules.module_geographical_centrality import GeographicalCentrality


class TestGeographicalCentrality(unittest.TestCase):
    """
    Unit test for the GeographicalCentrality class.
    """
    def setUp(self):
        """
        Set up test environment with a GeographicalCentrality instance and study area polygon.
        """
        self.gc_instance = GeographicalCentrality(
            study_area=None,
            weight=None,
            graph=None,
            edges_df=None,
            number_of_routes=50
        )

        wiesenbach_polygon = Polygon([
            (8.769, 49.402),
            (8.769, 49.411),
            (8.782, 49.411),
            (8.782, 49.402),
            (8.769, 49.402)
        ])

        self.gc_instance.poly_study_area = gpd.GeoDataFrame(
            geometry=[wiesenbach_polygon], crs="EPSG:4326")

    def test_random_points_in_polygon(self):
        """
        Test the generation of random points within the study area polygon.
        Test checks:
        1. The poly_study_area attribute is not None.
        2. Generates random points within study area polygon.
        3. Verifies that each sampled point is within study area polygon.
        :raises AssertionError: If any of the conditions mentioned above are not met.
        """
        num_points = 50

        print("Checking if poly_study_area is not None...")
        self.assertIsNotNone(self.gc_instance.poly_study_area)

        print(f"Generating {num_points} random points within the study area polygon...")
        sampled_points = self.gc_instance.random_points_in_polygon(num_points)

        print("Checking if each sampled point is within the study area polygon...")
        for point in sampled_points.geometry:
            self.assertTrue(self.gc_instance.poly_study_area.geometry[0].contains(point),
                            f"Point {point} is not "
                            f"within the study area "
                            f"polygon.")

        print("All points are within the study area polygon.")


if __name__ == '__main__':
    unittest.main()
