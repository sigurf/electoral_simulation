import yaml
import os

from Classes.Visualizer import Visualizer

current_directory_path = os.path.dirname(__file__)
instance_directory_path = os.path.join(current_directory_path, "Instances")

for f in os.scandir(instance_directory_path):
    file = open(f)
    instance = yaml.safe_load(file)
    file.close()
    
    visualizer = Visualizer(instance)
    visualizer.show_maps()
    visualizer.show_parliament_distribution()
