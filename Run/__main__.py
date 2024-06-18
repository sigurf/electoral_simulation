import os
import sys
import json

from Visualizer import Visualizer

"""
    --------------------------------- Main run file ------------------------------------

    Runs each instance within the electoral system provided in the command line argument.
"""

# Ensures that the command line argument is provided and is correct
if len(sys.argv) != 3:
    print("Error: Please provide the electoral system and election data instance as a command line argument.")
    sys.exit(1)

# Retrieves the electoral system and election data instance
electoral_system = sys.argv[1]
instance_name = sys.argv[2]

# Finds directory with the electoral system's instances
current_directory_path = os.path.dirname(__file__)
instance_directory_path = os.path.join(current_directory_path, "..", "Instances", instance_name + ".json")

# Loads instance
file = open(instance_directory_path)
instance = json.load(file)
file.close()

# Runs simulation and visualizes the result
visualizer = Visualizer(electoral_system, instance)
visualizer.show_maps()
visualizer.show_parliament_distribution()