import yaml
import os
import sys

from Visualizer import Visualizer

"""
    --------------------------------- Main run file ------------------------------------

    Runs each instance within the electoral system provided in the command line argument.
"""

# Ensures that the command line argument is provided and is correct
if len(sys.argv) != 2:
    print("Error: Please provide the electoral system as a command line argument.")
    sys.exit(1)

# Retrieves the electoral system provided
electoral_system = sys.argv[1]

# Finds directory with the electoral system's instances
current_directory_path = os.path.dirname(__file__)
instance_directory_path = os.path.join(current_directory_path, "..", "ElectoralSystems" , electoral_system, "Instances")

# Runs simulation for each instance
for f in os.scandir(instance_directory_path):

    # Loads instance
    file = open(f)
    instance = yaml.safe_load(file)
    file.close()
    
    # Runs simulation and visualizes the result
    visualizer = Visualizer(electoral_system, instance)
    visualizer.show_maps()
    visualizer.show_parliament_distribution()
