import colorsys
import os
import pandas as pd


class Tools:
        
    """
        Retrieves number of votes. Either in total, on one party, in one county or in one party in one county.

        @param  vote_data   dataframe used to find total votes
        @param  county      name of the county to retrieve the votes from. Value None if all counties should
                            be selected. Default value None.
        @param  party       name of the party to retrieve the votes for. Value None if all parties should
                            be selected. Default value None.
        @return             number of votes for the specified party in the specified county. All parties or counties if parameter is None.
    """
    @staticmethod
    def find_total_votes(vote_data, county = None, party = None):
        if county == None and party == None:
            return vote_data['Votes'].sum()
        elif county == None:
            return vote_data.loc[vote_data['Party'] == party, 'Votes'].sum()
        elif party == None:
            return vote_data.loc[vote_data['County'] == county, 'Votes'].sum()
        else:
            return vote_data[(vote_data['County'] == county) & (vote_data['Party'] == party)]['Votes'].values[0]
    

    """
        Retrieves the party with most votes in the specified county.

        @param  vote_data   dataframe used to find total votes
        @param  county  name of the county to find the most popular party.
        @return         name of the party with most votes in the county. 
    """
    @staticmethod
    def find_most_popular_party(vote_data, county):
        votes_from_county = vote_data[vote_data["County"] == county]
        max_index = votes_from_county["Votes"].idxmax()
        return vote_data.loc[max_index]["Party"]
    

    """
        Calculates the hue value (0-1) of the rgb color of each party.

        @param  color_data  dataframe with parties and their colors in hex code
        @return             an array of the hue value of the parties' colors, where the
                            parties are in alphabetical order (as in the data file).
    """
    @staticmethod
    def find_party_colors(color_data):
        colors = []
        for _, row_data in color_data.iterrows():
            hex_color = row_data["Color"]
            r = int(hex_color[1:3], 16) / 255.0
            g = int(hex_color[3:5], 16) / 255.0
            b = int(hex_color[5:7], 16) / 255.0
            h, _, _ = colorsys.rgb_to_hls(r, g, b)
            colors.append(1 - h)
        return colors
    

    """
        Retrieves the data from the specified filepath.

        @param  filepath    path of csv-file containing data (relative to the Data-directory).
        @return             dataframe of csv-file using pandas.

    """
    @staticmethod
    def create_dataframe(filepath):
        current_directory = os.path.dirname(__file__)
        csv_file_path = os.path.join(current_directory, "../Data/", filepath)
        return pd.read_csv(csv_file_path)
    

    """
        Converts mandate distribution from dict on to pandas dataframe. 
        
        @param  mandate_distribution_dict   dictionary showing how the mandates should be distributed for parties and counties.
                                            Dictionary must be on form:    {
                                                                                County1: [party1_mandates, party2_mandates, ..., partyN_mandates],
                                                                                County2: [party1_mandates, ..., partyN_mandates],
                                                                                ... 
                                                                                CountyM: [party1_mandates, ..., partyN_mandates]
                                                                            } 
        @param  party_list                  list of all participating parties ordered alphabetically.
        @return                             pandas dataframe with columns:  [County, Party, Mandates].    
    """
    @staticmethod
    def dict_to_df(mandate_distribution_dict, party_list):

        # Initialize an empty row
        row = []

        # Iterate over each county and list in the dictionary
        for county, vote_list in mandate_distribution_dict.items():
            for i in range(len(vote_list)):
                row.append((county, party_list[i], vote_list[i]))

        # Create a pandas dataFrame from the list of tuples
        return pd.DataFrame(row, columns=['County', 'Party', 'Mandates'])  