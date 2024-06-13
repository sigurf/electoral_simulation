
# Simulation of different electoral systems


## Table of Contents

- **Description**
- **Installation**
- **Usage**
- **Setup**
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

Run simulation by using bash console:

```bash
python Run LawName
``` 

## Setup

Create a folder *name of new law* within the ElectoralSystems-folder using the following structure:
+ Classes: contains classes for data analysis and visualization.
    + Election_Analyzer.py: contains the class Election_Analyzer which should inherit IELection_Analyzer forcing the class to contain the following methods:
        + get_vote_data():  returns the dataframe of the votes per party per district (from vote_data_csv).
        + get_mandate_data(): returns the dataframe for the districts and how many mandates they choose (from mandate_data_csv).
        + get_party_data(): returns the dataframe for the English name of the parties and their colors in hex code (from party_data_csv).
        + get_mandate_distribution(): returns the dataframe of the mandates per party per district. Should be with colums [District, Party, Mandates].
    + Optional: other classes to support the class Election_Analyzer.

+ Instances: contains information about the data used for an instance. Each instance should have the following structure:
    + name: *name of instance of data*
    + data:
        + vote_data_csv: *csv containing votes per party per district* Columns: [Party, Party, Votes] (see Norwegian_parliament_election_2021.csv).
        + mandate_data_csv: *csv containing mandates per district* Columns: [Party, Mandates] (see Norwegian_mandates_per_district.csv).
        + party_data_csv: *csv containing English name and color per party* Columns: [Party, EnglishName, Color] (see Norwegian_party_data.csv).
        + map_json: *json feature_collection map of with same districts as rest of data* (see Norway_map.json).

Add additional data and maps to the Data-folder using the existing structure if needed.

Support-folder contains Tools-class with some static methods which can be useful when generating election outcome of new electoral systems.


## Credits

First release of framework, FPTP electoral law and Modified Sainte-Laguë method: Sigurd Fagerholt [@sigurf] (https://github.com/sigurf/) and Bharat Premkumar [@BharatPremkumar] (https://github.com/BharatPremkumar).

Framework structure is inspired by Lorenzo Ruffati [@LRuffati] (https://github.com/LRuffati/SimulatoreSistemiElettorali).