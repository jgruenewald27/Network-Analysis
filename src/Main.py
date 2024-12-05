import os
import sys
import tkinter as tk
from tkinter import filedialog
from modules.module_create_region import Region
from modules.module_output_folder import create_output_folder
from modules.module_networkx_centrality import NetworkxCentrality
from modules.module_geographical_centrality import GeographicalCentrality


def get_output_folder():
    """
    Opens dialog to prompt the user to select or create an output folder.
    :return str: Path to selected or created output folder
    :raises SystemExit: If user cancels the folder selection
    """
    root = tk.Tk()
    root.withdraw()

    output_folder = filedialog.askdirectory(title="Select or create an output folder")

    if not output_folder:
        print("Output folder selection canceled.")
        sys.exit(0)

    return output_folder


def main(region, module_type, weight, number_of_routes):
    """
    The main function that orchestrates the workflow for centrality analysis.
    :param region: Region of interest
    :param module_type: Type of centrality analysis module ("networkx" or "geographical")
    :param weight: used weight parameter ("length" or "travel_time")
    :param number_of_routes: Number of random routes only for geographical centrality analysis
    :raises SystemExit: If there is an error in the workflow
    """
    # Get selected or created output folder
    selected_output_folder = get_output_folder()
    output_folder = create_output_folder(
        selected_output_folder, region, module_type, weight, number_of_routes
    )

    # Check if output folder creation was successful
    if not output_folder:
        print("Failed to create the output folder.")
        sys.exit(1)

    # Create a Region instance for the specified region
    my_region = Region(region, "drive")
    edges_df, osm_data = my_region.download_osm()

    # Check module type and weight parameters for networkx analysis
    if module_type == "networkx":
        if weight == "length":
            # Networkx centrality analysis for shortest routes
            my_centrality = NetworkxCentrality(weight=weight)
            output_file_path = os.path.join(output_folder, f"Networkx_centrality_{weight}.gpkg")
            my_centrality.get_centrality_short(
                osm_data, edges_df, output_file=output_file_path
            )
            my_centrality.explore_centrality_short(output_folder=output_folder)
        elif weight == "travel_time":
            # Networkx centrality analysis for fastest routes
            my_centrality = NetworkxCentrality(weight=weight)
            output_file_path = os.path.join(
                output_folder, f"Networkx_centrality_{weight}.gpkg"
            )
            my_centrality.get_centrality_fast(
                osm_data, edges_df, output_file=output_file_path
            )
            my_centrality.explore_centrality_fast(output_folder=output_folder)
        else:
            print("Invalid weight parameter. Use 'length' or 'travel_time'.")
            sys.exit(1)
    # Check module type and weight parameters for geographical analysis
    elif module_type == "geographical":
        output_file_path = os.path.join(
            output_folder, f"Geographical_centrality_{weight}_routes_{number_of_routes}.gpkg"
        )
        my_centrality = GeographicalCentrality(
            study_area=my_region,
            weight=weight,
            graph=osm_data,
            edges_df=edges_df,
            number_of_routes=number_of_routes,
        )
        my_centrality.create_study_area_polygon()
        if weight == "length":
            # Geographical centrality analysis for shortest routes
            my_centrality.generate_random_routes(my_centrality.graph)
            my_centrality.analyze_centrality()
            my_centrality.save_data_in_file(
                output_folder=output_folder,
                output_file=output_file_path,
                image_name=f"geographical_centrality_{weight}_routes_{number_of_routes}.png",
            )
        elif weight == "travel_time":
            # Geographical centrality analysis for fastest routes
            my_centrality.get_graph_travel_time()
            my_centrality.generate_random_routes(my_centrality.graph_with_travel_time)
            my_centrality.analyze_centrality()
            my_centrality.save_data_in_file(
                output_folder=output_folder,
                output_file=output_file_path,
                image_name=f"geographical_centrality_{weight}_routes_{number_of_routes}.png",
            )
        else:
            print("Invalid weight parameter. Use 'length' or 'travel_time'.")
            sys.exit(1)
    else:
        print("Invalid module type. Use 'networkx' or 'geographical'.")
        sys.exit(1)


if __name__ == "__main__":
    # Check if correct number of command-line arguments is provided
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print(
            "Usage: python Main.py <region> <module_type> <weight> [number_of_routes]"
        )
        sys.exit(1)

    # Parse command-line arguments
    used_region = sys.argv[1]
    used_module_type = sys.argv[2]
    used_weight = sys.argv[3]

    # Set number_of_routes parameter if provided
    used_number_of_routes = None
    if len(sys.argv) == 5:
        try:
            used_number_of_routes = int(sys.argv[4])
        except ValueError:
            print("Error: number_of_routes must be an integer.")
            sys.exit(1)

    # Call main function
    main(used_region, used_module_type, used_weight, used_number_of_routes)
