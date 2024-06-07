
# Simulation of different electoral systems


## Table of Contents

- **Description**
- **Installation**
- **Usage**
- **Setup**
- **Credits**
- **Contributing**


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

Create a folder *name of new law* with this structure:
+ Classes: contains classes for data analysis and visualization.
    + Election_Analyzer.py: contains the class Election_Analyzer which should inherit IELection_Analyzer forcing the class to contain the following methods:
        + get_vote_data(): returns the dataframe of the votes per party per county (see Norwegian_parliament_election_2021.csv)
        + get_mandate_data(): returns the dataframe for the counties and how many mandates they choose (see Norwegian_mandates_per_county.csv)
        + get_color_data(): returns the dataframe for the parties and their colors in hex code (see Norwegian_party_colors.csv)
        + get_mandate_distribution(): returns the dataframe of the mandates per party per county. Should be with colums [County, Party, Mandates]
    + Optional: other classes to support the class Election_Analyzer.
+ Instances: contains information about the data used for an instance. Each instance should have the following structure:
    + name: *name of instance of data*
    + data:
        + vote_data_csv: *csv containing votes per party per county* (see Norwegian_parliament_election_2021.csv)
        + mandate_data_csv: *csv containing mandates per county* (see Norwegian_mandates_per_county.csv)
        + party_color_csv: *csv containing colors per party* (see Norwegian_party_colors.csv)
        + map_json: *json feature_collection map of with same counties as rest of data* (see Norway_map.json)

Add additional data to the Data-folder if useful.s


## Credits

First release of framework, FPTP electoral law and Modified Sainte-Laguë method: Sigurd Fagerholt [@sigurf] (https://github.com/sigurf/) and Bharat Premkumar [@BharatPremkumar] (https://github.com/BharatPremkumar).

Framework structure is inspired by Lorenzo Ruffati [@LRuffati] (https://github.com/LRuffati/SimulatoreSistemiElettorali).


## Contributing

Pull requests are welcome.