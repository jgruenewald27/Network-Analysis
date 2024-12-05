"""
Module to handle the creation of output folders based on analysis parameters.
"""

import os


def create_output_folder(selected_output_folder, region, module_type, weight, number_of_routes):
    """
    Creates an output folder based on the provided parameters.
    :param selected_output_folder: selected or specified output folder path
    :param region: region for which the analysis is performed
    :param module_type: type of module used for analysis ('networkx' or 'geographical')
    :param weight: weight parameter used in the analysis ('length' or 'travel_time')
    :param number_of_routes: number of routes only for geographical
    :return full_output_path: full path of created output folder.
    :exception: Returns None if selected_output_folder is empty.
    """
    if not selected_output_folder:
        print("Selected output folder is empty.")
        return None

    region_cleaned = region.replace(",", "_")

    if number_of_routes is not None:
        output_folder_name = (
            f"Output_{region_cleaned}_{module_type}_{weight}_{number_of_routes}_routes"
        )
    else:
        output_folder_name = f"Output_{region_cleaned}_{module_type}_{weight}"

    full_output_path = os.path.join(selected_output_folder, output_folder_name)

    if not os.path.exists(full_output_path):
        os.makedirs(full_output_path)

    return full_output_path
