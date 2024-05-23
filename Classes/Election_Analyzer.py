import os
import pandas as pd
import colorsys

"""
    Class containing all analysis done on the election data specified by the instance.
"""

class Election_Analyzer:

    """
        Initializes the Election Analyzer object holding all useful information.

        @param  instance  a loaded yaml-file found in the Instances directory, specifying the data used.
    """
    def __init__(self, instance):

        # Dataframes for the raw data found in the instance
        self.vote_data = self.create_dataframe("VoteData/" + instance["data"]["vote_data_csv"] + ".csv")
        self.mandate_data = self.create_dataframe("MandateData/" + instance["data"]["mandate_data_csv"] + ".csv")
        self.color_data = self.create_dataframe("PartyColorData/" + instance["data"]["party_color_csv"] + ".csv")
        
        # Dataframes for all parties and counties
        self.parties = self.vote_data[self.vote_data["County"] == self.vote_data.loc[0]["County"]]["Party"]
        self.counties = self.mandate_data["County"]

        # Party colors converted to hue (0-1) used for visualization
        self.party_colors = self.find_party_colors()

        # Distributed mandates (per county) using the FPTP electoral system
        mandate_distribution = self.find_mandate_distribution()
        self.mandate_distribution_by_county = mandate_distribution[1]
        self.mandate_distribution = mandate_distribution[0]
        

    """
        Retrieves the data from the specified filepath.

        @param  filepath    path of csv-file containing data (relative to the Data-directory).
        @return             dataframe of csv-file using pandas.

    """
    def create_dataframe(self, filepath):
        current_directory = os.path.dirname(__file__)
        csv_file_path = os.path.join(current_directory, "../Data/", filepath)
        return pd.read_csv(csv_file_path)


    """
        Retrieves the party with most votes in the specified county.

        @param  county  name of the county to find the most popular party.
        @return         name of the party with most votes in the county. 
    """
    def find_most_popular_party(self, county):
        votes_from_county = self.vote_data[self.vote_data["County"] == county]
        max_index = votes_from_county["Votes"].idxmax()
        return self.vote_data.loc[max_index]["Party"]


    """
        Calculates how the mandates are distributed among the parties, both for the entire
        country and for each county.

        @return         a dictionary with the party as key and the number of mandates it
                        receives from the entire country as value.
        @return         a 2D array [#counties, #parties] with the number of mandates a party receives from a county.
                        Both the counties and the parties are organised in alphabetical order (as in the data files).
    """
    def find_mandate_distribution(self):
        mandate_distribution_by_county = []
        mandate_distribution = {}

        # Iterates over counties and finds party with most votes
        for county_index, row_data in self.mandate_data.iterrows():
            mandate_distribution_by_county.append([])
            county = row_data["County"]

            # Find party with most votes in party and the number of mandates they will receive
            party_receiving_all_mandates = self.find_most_popular_party(county)
            mandates_from_county = self.mandate_data[self.mandate_data["County"] == county]["Mandates"].values[0]
            
            # Add county-winner's mandates to the party's total mandates
            if party_receiving_all_mandates in mandate_distribution:
                mandate_distribution[party_receiving_all_mandates] += mandates_from_county
            else:
                mandate_distribution[party_receiving_all_mandates] = mandates_from_county
            
            # Add county-winner's mandates to party's mandates from county.
            # All other parties receives zero votes.
            for party in self.parties:
                if party == party_receiving_all_mandates:
                    mandate_distribution_by_county[county_index].append(mandates_from_county)
                else:
                    mandate_distribution_by_county[county_index].append(0)
        
        # Sort parties receiving mandates alphabetically.
        mandate_distribution = dict(sorted(mandate_distribution.items()))
        return mandate_distribution, mandate_distribution_by_county
    

    """
        Calculates the hue value (0-1) of the rgb color of each party.

        @return         an array of the hue value of the parties' colors, where the
                        parties are in alphabetical order (as in the data file).
    """
    def find_party_colors(self):
        colors = []
        for _, row_data in self.color_data.iterrows():
            hex_color = row_data["Color"]
            r = int(hex_color[1:3], 16) / 255.0
            g = int(hex_color[3:5], 16) / 255.0
            b = int(hex_color[5:7], 16) / 255.0
            h, _, _ = colorsys.rgb_to_hls(r, g, b)
            colors.append(1 - h)
        return colors
    

    """
        Retrieves number of votes. Either in total, on one party, in one county or in one party in one county.

        @param  county  name of the county to retrieve the votes from. Value None if all counties should
                        be selected. Default value None.
        @param  party   name of the party to retrieve the votes for. Value None if all parties should
                        be selected. Default value None.
    """
    def find_total_votes(self, county = None, party = None):
        if county == None and party == None:
            return self.vote_data['Votes'].sum()
        elif county == None:
            return self.vote_data.loc[self.vote_data['Party'] == party, 'Votes'].sum()
        elif party == None:
            return self.vote_data.loc[self.vote_data['County'] == county, 'Votes'].sum()
        else:
            return self.vote_data[(self.vote_data['County'] == county) & (self.vote_data['Party'] == party)]['Votes'].values[0]
        
    
    def get_counties(self):
        return self.counties
    
    def get_parties(self):
        return self.parties
    
    def get_color_data(self):
        return self.color_data
    
    def get_party_colors(self):
        return self.party_colors

    def get_mandate_data(self):
        return self.mandate_data
    
    def get_mandate_distribution(self):
        return self.mandate_distribution