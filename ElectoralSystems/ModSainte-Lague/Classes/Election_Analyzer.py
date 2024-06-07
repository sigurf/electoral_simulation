from Tools import Tools # type: ignore
from IElection_Analyzer import IElection_Analyzer # type: ignore


"""
    Class containing all analysis done on the election data specified by the instance according to the Modified Saint-Laguë method.
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
        mandate_distribution = self.find_district_mandate_distribution()        
        distribution_by_county = mandate_distribution[0]
        national_distribution = mandate_distribution[1]
        levelling_mandates = self.find_levelling_mandates(national_distribution)
        party_ratio = [0]*len(self.parties)*len(self.counties)
        for i in range(len(self.counties)):
            for j in range(len(self.parties)):
                party_ratio[len(self.parties)*i + j] = int(levelling_mandates[self.parties[j]] > 0) * 2 * (mandate_distribution[0][self.counties[i]][j] + 1)  / Tools.find_total_votes(self.vote_data, self.counties[i]) / int(self.mandate_data[self.mandate_data["County"] == self.counties[i]]["Mandates"].values[0])
        mandates_to_party = {}
        for _ in range(len(self.counties)):

            # Find county and party with highest ratio
            max_ratio = max(party_ratio)
            max_index = party_ratio.index(max_ratio)
            county_index = max_index // len(self.parties)
            county = self.counties[county_index]
            party_index = max_index % len(self.parties)
            party_receiving_mandate = self.parties[party_index]

            # Keep track of mandates a party has receives
            if party_receiving_mandate not in mandates_to_party.keys():
                mandates_to_party[party_receiving_mandate] = 0
            mandates_to_party[party_receiving_mandate] += 1

            # Make sure county cannot distribute more than one mandate
            for index in range(county_index * len(self.parties), (county_index + 1) * len(self.parties)):
                party_ratio[index] = 0
            
            # Make sure party cannot receive more mandates than they should
            if mandates_to_party[party_receiving_mandate] == levelling_mandates[party_receiving_mandate]:
                for index in range(len(self.counties)):
                    party_ratio[index*len(self.parties) + party_index] = 0
            distribution_by_county[county][party_index] += 1
        
        for party in self.parties:
            national_distribution[party] += levelling_mandates[party]
        return distribution_by_county

    """
        Calculates how the DISTRICT mandates are distributed among the parties for each county.

        @return         a dictionary {county: [mandates_party1, ... , mandates_partyN], ...} with the mandates per party per county.
                        Both the counties and the parties are organised in alphabetical order (as in the data files).
    """
    def find_district_mandate_distribution(self):

        # Create copy of votes to change as mandates are distributed
        votes = self.vote_data.copy()
        votes["Votes"] = votes["Votes"].astype(float)

        # All votes should be divided by 1.4
        for i in range(len(votes)):
            votes.at[i, "Votes"] /= 1.4

        # Look at one county at the time
        mandate_distribution = {}
        for county in self.counties:
            mandate_distribution[county] = [0]*len(self.parties)
            votes_from_county = votes[votes["County"] == county]

            # Distribute all the county's mandates except one (levelling mandate) one by one by selecting the party with currently highest vote count in the county
            for _ in range(int(self.mandate_data[self.mandate_data["County"] == county]["Mandates"].iloc[0]) - 1):

                # Find party with most votes in the county currently
                max_index = votes_from_county["Votes"].idxmax()
                party_receiving_mandate = votes_from_county.loc[max_index]["Party"]
                party_receiving_mandate_index = next(i for i in range(len(self.parties)) if self.parties.loc[i] == party_receiving_mandate)

                # Divide the vote count as the party receives mandates. First 1.4, then 3, 5, 7...
                mandates_already_received = mandate_distribution[county][party_receiving_mandate_index]
                if mandates_already_received == 0:
                    votes_from_county.at[max_index, "Votes"] *= 1.4/3
                else:
                    votes_from_county.at[max_index, "Votes"] *= (1 + 2*mandates_already_received) / (3 + 2*mandates_already_received)

                # Add mandate to party with currently most votes in county
                mandate_distribution[county][party_receiving_mandate_index] += 1

        # Retrieves national mandate distribution from mandate distribution per county
        national_mandate_distribution = {}
        for i in range(len(self.parties)):
            national_mandate_distribution[self.parties[i]] = 0
            for county in mandate_distribution.keys():
                national_mandate_distribution[self.parties[i]] += mandate_distribution[county][i]
        return mandate_distribution, national_mandate_distribution


    """
        Calculates how the LEVELLING mandates are distributed among the parties for each county.

        @return         a dictionary {county: [mandates_party1, ... , mandates_partyN], ...} with the mandates per party per county.
                        Both the counties and the parties are organised in alphabetical order (as in the data files).
    """
    def find_levelling_mandates(self, mandates_from_district, overrepresented_parties = []):
        
        """ National mandate distribution
                - Like find_district_mandate_distribution() but with the entire nation as one district, not for each county. 
                - Gives the correct number of levelling mandates per county, but not from which county they come from.
        """

        # All votes in country
        total_votes = Tools.find_total_votes(self.vote_data)

        # Parties under threshold (4% of total votes)
        tiny_parties = []
        for party in self.parties:
            if Tools.find_total_votes(self.vote_data, None, party) / total_votes  < 0.04:
                tiny_parties.append(party)
        
        mandate_distribution = {}

        # Current votes to party from entire country. Overrepresented parties have 0 votes.
        total_votes_per_party = [0]*len(self.parties)
        for i in range(len(self.parties)):
            total_votes_per_party[i] = int(self.parties[i] not in overrepresented_parties and self.parties[i] not in tiny_parties) * Tools.find_total_votes(self.vote_data, None, self.parties[i]) / 1.4
            mandate_distribution[self.parties[i]] = 0

        # All mandates to be distributed. Mandates from overrepresented parties removed
        total_mandates = self.mandate_data["Mandates"].sum()
        for party in overrepresented_parties:
            total_mandates -= mandates_from_district[party]

        for party in tiny_parties:
            total_mandates -= mandates_from_district[party]

        # Distribute all mandates
        for _ in range(total_mandates):

            # Find party with most votes in entire country currently
            most_votes = max(total_votes_per_party)
            max_index = total_votes_per_party.index(most_votes)
            party_receiving_mandate = self.parties[max_index]

            # Reduce votes to party according to rule: divided by 1.4, 3, 5, 7...
            mandates_already_received = mandate_distribution[party_receiving_mandate]
            if mandates_already_received == 0:
                total_votes_per_party[max_index] *= 1.4/3
            else:
                total_votes_per_party[max_index] *= (1 + 2*mandates_already_received) / (3 + 2*mandates_already_received)
            
            # Add mandate to party
            mandate_distribution[party_receiving_mandate] += 1

        """ Levelling mandate allocation
                - Determines which counties the levelling mandates comes from.
        """

        # Add levelling mandates to party and mark overrepresented parties
        new_overrepresented_party = False
        levelling_mandates = {}
        for party in mandate_distribution.keys():
            if mandate_distribution[party] < mandates_from_district[party] and mandate_distribution[party] > 0:
                overrepresented_parties.append(party)
                new_overrepresented_party = True
            else:
                levelling_mandates[party] = int(Tools.find_total_votes(self.vote_data, None, party) / total_votes  >= 0.04) * max(mandate_distribution[party] - mandates_from_district[party], 0)

        # Start over if overrepresented party is added
        if new_overrepresented_party:
            return self.find_levelling_mandates(mandates_from_district, overrepresented_parties) 
        else:
            return levelling_mandates

    
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