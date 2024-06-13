from Tools import Tools # type: ignore
from IElection_Analyzer import IElection_Analyzer # type: ignore

"""
    Class containing all analysis done on the election data specified by the instance according to the First-past-the-post (FPTP) electoral system.
"""

class Election_Analyzer(IElection_Analyzer):

    """
        Initializes the Election Analyzer object holding all useful information including a pandas dataframe of the final parliament distribution.

        @param  instance  a loaded yaml-file found in the Instances directory, specifying the data used.
    """
    def __init__(self, instance):

        # Dataframes for the raw data found in the instance
        self.vote_data = Tools.create_dataframe(instance["data"]["vote_data_csv"] + ".csv")
        self.mandate_data = Tools.create_dataframe(instance["data"]["mandate_data_csv"] + ".csv")
        self.party_data = Tools.create_dataframe(instance["data"]["party_data_csv"] + ".csv")
        
        # Dataframes for all parties and districts
        self.parties = self.vote_data[self.vote_data["District"] == self.vote_data.loc[0]["District"]]["Party"]
        self.districts = self.mandate_data["District"]

        # Distributed mandates (per district) using the FPTP electoral system
        mandate_distribution = self.find_mandate_distribution()
        self.df = Tools.dict_to_df(mandate_distribution, self.parties)
        


    """
        Calculates how the mandates are distributed among the parties for each district.

        @return         a dictionary {district: [mandates_party1, ... , mandates_partyN], ...} with the mandates per party per district.
                        Both the districts and the parties are organised in alphabetical order (as in the data files).
    """
    def find_mandate_distribution(self):
        mandate_distribution_by_district = {}
        mandate_distribution = {}

        # Iterates over districts and finds party with most votes
        for _, row_data in self.mandate_data.iterrows():
            district = row_data["District"]
            mandate_distribution_by_district[district] = [0]*len(self.parties)


            # Find party with most votes in party and the number of mandates they will receive
            party_receiving_all_mandates = Tools.find_most_popular_party(self.vote_data, district)
            mandates_from_district = self.mandate_data[self.mandate_data["District"] == district]["Mandates"].values[0]
            
            # Add district-winner's mandates to the party's total mandates
            if party_receiving_all_mandates in mandate_distribution:
                mandate_distribution[party_receiving_all_mandates] += mandates_from_district
            else:
                mandate_distribution[party_receiving_all_mandates] = mandates_from_district
            
            # Add district-winner's mandates to party's mandates from district.
            # All other parties receives zero votes.
            for i in range(len(self.parties)):
                if self.parties[i] == party_receiving_all_mandates:
                    mandate_distribution_by_district[district][i] = mandates_from_district
        
        # Sort parties receiving mandates alphabetically.
        mandate_distribution = dict(sorted(mandate_distribution.items()))
        return mandate_distribution_by_district
    

    # Getters

    def get_vote_data(self):
        return self.vote_data
    
    def get_districts(self):
        return self.districts
    
    def get_parties(self):
        return self.parties
    
    def get_party_data(self):
        return self.party_data
    
    def get_party_colors(self):
        return self.party_colors

    def get_mandate_data(self):
        return self.mandate_data
    
    def get_mandate_distribution(self):
        return self.df