from Tools import Tools # type: ignore
from IElection_Analyzer import IElection_Analyzer # type: ignore


"""
    Class containing all analysis done on the election data specified by the instance according to the Modified Sainte-Laguë method.
"""
class Election_Analyzer(IElection_Analyzer):

    """
        Initializes the Election Analyzer object holding all useful information including a pandas dataframe of the final parliament distribution.

        @param  instance  a loaded yaml-file found in the Instances directory, specifying the data used.
    """
    def __init__(self, instance):

        # Dataframes for the raw data found in the instance
        self.vote_data, self.district_data, self.party_data = Tools.create_dataframes(instance)
        
        # Dataframes for all parties and districts
        self.parties = self.vote_data[self.vote_data["District"] == self.vote_data.loc[0]["District"]]["Party"]
        self.districts = self.district_data["District"]

        # Distributed mandates (per district) using the FPTP electoral system
        mandate_distribution = self.find_mandate_distribution()

        self.df = Tools.dict_to_df(mandate_distribution, self.parties)


    """
        Calculates how the mandates are distributed among the parties for each district.

        @return         a dictionary {district: [mandates_party1, ... , mandates_partyN], ...} with the mandates per party per district.
                        Both the districts and the parties are organised in alphabetical order (as in the data files).
    """
    def find_mandate_distribution(self):
        mandate_distribution = self.find_district_mandate_distribution()        
        distribution_by_district = mandate_distribution[0]
        national_distribution = mandate_distribution[1]
        levelling_mandates = self.find_levelling_mandates(national_distribution)
        party_ratio = [0]*len(self.parties)*len(self.districts)
        for i in range(len(self.districts)):
            district_factor = Tools.find_total_votes(self.vote_data, self.districts[i]) / (int(self.district_data[self.district_data["District"] == self.districts[i]]["Mandates"].values[0]) - 1)
            for j in range(len(self.parties)):
                party_ratio[len(self.parties)*i + j] = int(levelling_mandates[self.parties[j]] > 0) * Tools.find_total_votes(self.vote_data, self.districts[i], self.parties[j]) / (2 * mandate_distribution[0][self.districts[i]][j] + 1)  / district_factor
        mandates_to_party = {}
        for _ in range(len(self.districts)):

            # Find district and party with highest ratio
            max_ratio = max(party_ratio)
            max_index = party_ratio.index(max_ratio)
            district_index = max_index // len(self.parties)
            district = self.districts[district_index]
            party_index = max_index % len(self.parties)
            party_receiving_mandate = self.parties[party_index]

            # Keep track of mandates a party has receives
            if party_receiving_mandate not in mandates_to_party.keys():
                mandates_to_party[party_receiving_mandate] = 0
            mandates_to_party[party_receiving_mandate] += 1

            # Make sure district cannot distribute more than one mandate
            for index in range(district_index * len(self.parties), (district_index + 1) * len(self.parties)):
                party_ratio[index] = 0
            
            # Make sure party cannot receive more mandates than they should
            if mandates_to_party[party_receiving_mandate] == levelling_mandates[party_receiving_mandate]:
                for index in range(len(self.districts)):
                    party_ratio[index*len(self.parties) + party_index] = 0
            distribution_by_district[district][party_index] += 1
        
        for party in self.parties:
            national_distribution[party] += levelling_mandates[party]
        return distribution_by_district

    """
        Calculates how the DISTRICT mandates are distributed among the parties for each district.

        @return         a dictionary {district: [mandates_party1, ... , mandates_partyN], ...} with the mandates per party per district.
                        Both the districts and the parties are organised in alphabetical order (as in the data files).
    """
    def find_district_mandate_distribution(self):

        # Create copy of votes to change as mandates are distributed
        votes = self.vote_data.copy()
        votes["Votes"] = votes["Votes"].astype(float)

        # All votes should be divided by 1.4
        for i in range(len(votes)):
            votes.at[i, "Votes"] /= 1.4

        # Look at one district at the time
        mandate_distribution = {}
        for district in self.districts:
            mandate_distribution[district] = [0]*len(self.parties)
            votes_from_district = votes[votes["District"] == district]

            # Distribute all the district's mandates except one (levelling mandate) one by one by selecting the party with currently highest vote count in the district
            for _ in range(int(self.district_data[self.district_data["District"] == district]["Mandates"].iloc[0]) - 1):

                # Find party with most votes in the district currently
                max_index = votes_from_district["Votes"].idxmax()
                party_receiving_mandate = votes_from_district.loc[max_index]["Party"]
                party_receiving_mandate_index = next(i for i in range(len(self.parties)) if self.parties.loc[i] == party_receiving_mandate)

                # Divide the vote count as the party receives mandates. First 1.4, then 3, 5, 7...
                mandates_already_received = mandate_distribution[district][party_receiving_mandate_index]
                if mandates_already_received == 0:
                    votes_from_district.at[max_index, "Votes"] *= 1.4/3
                else:
                    votes_from_district.at[max_index, "Votes"] *= (1 + 2*mandates_already_received) / (3 + 2*mandates_already_received)

                # Add mandate to party with currently most votes in district
                mandate_distribution[district][party_receiving_mandate_index] += 1

        # Retrieves national mandate distribution from mandate distribution per district
        national_mandate_distribution = {}
        for i in range(len(self.parties)):
            national_mandate_distribution[self.parties[i]] = 0
            for district in mandate_distribution.keys():
                national_mandate_distribution[self.parties[i]] += mandate_distribution[district][i]
        return mandate_distribution, national_mandate_distribution


    """
        Calculates how the LEVELLING mandates are distributed among the parties for each district.

        @return         a dictionary {district: [mandates_party1, ... , mandates_partyN], ...} with the mandates per party per district.
                        Both the districts and the parties are organised in alphabetical order (as in the data files).
    """
    def find_levelling_mandates(self, mandates_from_district, overrepresented_parties = []):
        
        """ National mandate distribution
                - Like find_district_mandate_distribution() but with the entire nation as one district, not for each district. 
                - Gives the correct number of levelling mandates per district, but not from which district they come from.
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
        total_mandates = self.district_data["Mandates"].sum()
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
                - Determines which districts the levelling mandates comes from.
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
    
    def get_districts(self):
        return self.districts
    
    def get_parties(self):
        return self.parties
    
    def get_party_data(self):
        return self.party_data
    
    def get_party_colors(self):
        return self.party_colors

    def get_district_data(self):
        return self.district_data
    
    def get_mandate_distribution(self):
        return self.df