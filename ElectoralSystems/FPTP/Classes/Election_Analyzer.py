from Tools import Tools # type: ignore
from IElection_Analyzer import IElection_Analyzer # type: ignore

"""
    Class containing all analysis done on the election data specified by the instance according to the First-past-the-post (FPTP) electoral system.
"""

class Election_Analyzer(IElection_Analyzer):

    """
        Initializes the Election Analyzer object holding all useful information.

        @param  instance  a loaded yaml-file found in the Instances directory, specifying the data used.
    """
    def __init__(self, instance):

        # Dataframes for the raw data found in the instance
        self.vote_data = Tools.create_dataframe(instance["data"]["vote_data_csv"] + ".csv")
        self.mandate_data = Tools.create_dataframe(instance["data"]["mandate_data_csv"] + ".csv")
        self.color_data = Tools.create_dataframe(instance["data"]["party_color_csv"] + ".csv")
        
        # Dataframes for all parties and counties
        self.parties = self.vote_data[self.vote_data["County"] == self.vote_data.loc[0]["County"]]["Party"]
        self.counties = self.mandate_data["County"]

        # Distributed mandates (per county) using the FPTP electoral system
        mandate_distribution = self.find_mandate_distribution()
        self.df = Tools.dict_to_df(mandate_distribution, self.parties)
        


    """
        Calculates how the mandates are distributed among the parties for each county.

        @return         a dictionary {county: [mandates_party1, ... , mandates_partyN], ...} with the mandates per party per county.
                        Both the counties and the parties are organised in alphabetical order (as in the data files).
    """
    def find_mandate_distribution(self):
        mandate_distribution_by_county = {}
        mandate_distribution = {}

        # Iterates over counties and finds party with most votes
        for _, row_data in self.mandate_data.iterrows():
            county = row_data["County"]
            mandate_distribution_by_county[county] = [0]*len(self.parties)


            # Find party with most votes in party and the number of mandates they will receive
            party_receiving_all_mandates = Tools.find_most_popular_party(self.vote_data, county)
            mandates_from_county = self.mandate_data[self.mandate_data["County"] == county]["Mandates"].values[0]
            
            # Add county-winner's mandates to the party's total mandates
            if party_receiving_all_mandates in mandate_distribution:
                mandate_distribution[party_receiving_all_mandates] += mandates_from_county
            else:
                mandate_distribution[party_receiving_all_mandates] = mandates_from_county
            
            # Add county-winner's mandates to party's mandates from county.
            # All other parties receives zero votes.
            for i in range(len(self.parties)):
                if self.parties[i] == party_receiving_all_mandates:
                    mandate_distribution_by_county[county][i] = mandates_from_county
        
        # Sort parties receiving mandates alphabetically.
        mandate_distribution = dict(sorted(mandate_distribution.items()))
        return mandate_distribution_by_county
    

    # Getters

    def get_vote_data(self):
        return self.vote_data
    
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
        return self.df