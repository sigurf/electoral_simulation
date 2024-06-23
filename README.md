
# Simulation of different electoral systems


## Table of Contents

- **Description**
- **Installation**
- **Usage**
- **Adding new electoral systems**
- **Adding new election data instances**

- **Credits**


## Description

The project uses voting data to determine the composition of the parliament according to the chosen voting system. A brief visualization of the voting data is also provided.


## Installation

Clone the repository and install the dependencies.

```bash
git git clone https://github.com/sigurf/electoral_simulation.git
cd electoral_simulation
pip install -r requirements.txt
```


## Usage

Run simulation of electoral system *system* using instance *instance* with bash console:

```bash
python Run <system> <instance>
``` 


## Adding new electoral systems

Create a folder *name of new electoral system* within the ElectoralSystems-folder containing classes for data analysis. The folder must have the following stricture:
+ Election_Analyzer.py: contains the class Election_Analyzer which should inherit IELection_Analyzer forcing the class to contain the following methods:
    + get_vote_data():  returns the dataframe of the votes per party per district (from vote_data_csv).
    + get_district_data(): returns the dataframe for the districts and how many mandates they choose (from district_data_csv).
    + get_party_data(): returns the dataframe for the English name of the parties and their colors in hex code (from party_data_csv).
    + get_mandate_distribution(): returns the result dataframe with mandates per party per district. Should be with colums [District, Party, Mandates].
+ Optional classes: other optional classes to support the class Election_Analyzer.

Support-folder contains Tools-class with some static methods which can be useful when generating election outcome of new electoral systems.


## Adding new election data instances 

Create a new json-file *name of new instance* within the Instances-folder containing the set of data files used for the instance. Each instance must have the following structure (see Norwegian_parliament_election_2021.json):
+ name: *name of instance of data*
+ data:
    + election_data_csv: *csv containing votes per party per district* CSV-file from the Election Data-folder with columns: [District, Party, Votes] (see Norwegian_parliament_election_2021.csv).
    + district_data_csv: *csv containing mandates per district* CSV-file from the District Data-folder with columns: [Party, Mandates] (see Norwegian_districts.csv).
    + party_data_csv: *csv containing English name and color per party* CSV-file from the Party Data-folder with columns: [Party, EnglishName, Color] (see Norwegian_parties.csv).
    + map_json: *json feature_collection map of with same districts as rest of data* JSON-file from Maps-folder (see Norway_map.json).

The data must correlate with each other, meaning the *election_data_csv* must describe the votes from the districts in *district_data_csv* given to the parties in *party_data_csv*.

Add additional data and maps to the Data-folder using the existing structure if needed for the instance.


## Credits

First release of framework, FPTP electoral law and Modified Sainte-Laguë method: Sigurd Fagerholt [@sigurf] (https://github.com/sigurf/) and Bharat Premkumar [@BharatPremkumar] (https://github.com/BharatPremkumar).

Framework structure is inspired by Lorenzo Ruffati [@LRuffati] (https://github.com/LRuffati/SimulatoreSistemiElettorali).