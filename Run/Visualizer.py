import json
import os
import plotly.graph_objects as go
import sys

# Adds the path to Tools to sys.path
tool_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Support"))
sys.path.append(tool_path)
from Tools import Tools # type: ignore


"""
    Class that can visualize the election data, analysis and result according to the instance.

"""
class Visualizer:

    """
        Initializes the Visualizer class.

        @param  electoral_system    a chosen electoral system to simulate the instance on
        @param  instance            a loaded yaml-file found in the Instances directory, specifying the data used.
    """
    def __init__(self, electoral_system, instance):

        self.electoral_system = electoral_system

        # Adds the path to the electoral system to sys.path
        electoral_system_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ElectoralSystems", electoral_system, "Classes"))
        sys.path.append(electoral_system_path)
        from Election_Analyzer import Election_Analyzer # type: ignore
        ea = Election_Analyzer(instance)

        # Name of the instance ran
        self.instance = instance["name"]

        # Unprocessed dataframes
        self.vote_data = ea.get_vote_data()
        self.mandate_data = ea.get_mandate_data()
        self.color_data = ea.get_color_data()


        # Dataframes for all parties and counties
        self.parties = self.vote_data[self.vote_data["County"] == self.vote_data.loc[0]["County"]]["Party"]
        self.counties = self.mandate_data["County"]

        self.party_colors = Tools.find_party_colors(self.color_data)

        # Dataframe of parliament mandate distribution for the given electoral system and instance
        self.mandate_distribution = ea.get_mandate_distribution()

        # Loads map of Norway
        current_directory = os.path.dirname(__file__)
        json_file_path = os.path.join(current_directory, "..", "Data", "Maps", instance["data"]["map_json"] + ".json")
        with open(json_file_path) as map:
            self.geo_map = json.load(map)


    """
        Visualizes the vote distribution and each counties winner using an interactive map.
    """
    def show_maps(self):
        maps = [self.get_vote_map(), self.get_mandate_map()]
        for map in maps:
            fig = go.Figure(data=map[0], layout=map[1])
            fig.update_geos(fitbounds='geojson', visible=False)
            fig.show()
        

    """
        Interactive map with information about the votes of each county.

        @return         map of counties containing the voting data.
        @return         layout of the map.
    """
    def get_vote_map(self):

        # Specifies value and label appearing when hovering over county
        total_votes = []
        vote_distribution = []
        for county_index in range(len(self.counties)):

            # Value is total number of votes in county
            county = self.counties[county_index]
            total_votes_in_county = Tools.find_total_votes(self.vote_data, county)
            total_votes.append(total_votes_in_county)

            # Label with each party's votes in the county hovered over
            label =f"<b>{county}: {total_votes[county_index]}</b><br>"
            for party in self.parties:
                total_votes_to_party_in_county = Tools.find_total_votes(self.vote_data, county, party)
                label += f"{party}: {total_votes_to_party_in_county}<br>"
            vote_distribution.append(label)

        # Creates map with data showing how the votes are distributed
        vote_map = go.Choropleth(z=total_votes, geojson=self.geo_map, locations=self.counties,
                                colorscale="Peach",
                                colorbar_title="Total amount of votes",
                                featureidkey='properties.name',
                                hoverinfo = 'text',
                                text=vote_distribution
                            )
        vote_map_layout = go.Layout(title = "<b>" + self.instance + "</b><br><br>Total votes by county and votes to party by county")
        return vote_map, vote_map_layout


    """
        Interactive map showing the party with most votes in each county, and how many mandates
        the party receive.

        @return         map of counties showing the party with most votes and the mandates they receive.
        @return         layout of the map.
    """
    def get_mandate_map(self):

        # Specifies value and label appearing when hovering over county
        total_mandates = []
        mandate_distribution = []
        colors = []
        for county_index in range(len(self.counties)):

            # Value is the total number of mandates in each county
            county = self.counties[county_index]
            total_mandates.append(self.mandate_data[self.mandate_data['County'] == county]['Mandates'].values[0])
            
            # The label consists of number of mandates each party receives in each county
            label =f"<b>{county}: {total_mandates[county_index]}</b><br>"
            county_mandate_distribution = self.mandate_distribution[self.mandate_distribution['County'] == county][['Party', 'Mandates']]
            for _, row in county_mandate_distribution.iterrows():
                if row['Mandates'] > 0:
                    label += f"{row['Party']}: {row['Mandates']}<br>"
            mandate_distribution.append(label)


            # The county is shown in the most popular party's color
            colors.append(self.party_colors[self.parties[self.parties == Tools.find_most_popular_party(self.vote_data, county)].index[0]])

        # Creates map with data showing how the mandates are distributed according to FPTP
        mandate_map = go.Choropleth(z=colors, geojson=self.geo_map, locations=self.counties,
                                colorscale="Rainbow",
                                zmin=0,
                                zmax=1,
                                featureidkey='properties.name',
                                hoverinfo = 'text',
                                showscale=False,
                                text=mandate_distribution
                            )
        mandate_map_layout = go.Layout(title = "<b>" + self.instance + "</b><br><br>Party receiving mandates from county using " + self.electoral_system)
        return mandate_map, mandate_map_layout
       

    """
        Shows the distribution of the political parties in the parliament when using FPTP.
    """
    def show_parliament_distribution(self):
        
        # Retrieves national mandate distribution from mandate distribution per county
        parliament_distribution = {}
        for _, row in self.mandate_distribution.iterrows():
            party = row['Party']
            mandates = row['Mandates']
            if mandates > 0:
                if party not in parliament_distribution.keys():
                    parliament_distribution[party] = 0
                parliament_distribution[party] += mandates
        
        # Sorts the dictionary alphabetically to visualize party in the correct color
        parliament_distribution = {party: parliament_distribution[party] for party in sorted(parliament_distribution, key=str.lower)}
        
        # Extracts lists from dictionary
        labels = list(parliament_distribution.keys())
        values = list(parliament_distribution.values())

        # Allocates the correct color to the parties
        colors = self.color_data[self.color_data["Party"].isin(labels)]["Color"].tolist()

        # Visualizes pie chart showing parliament distribution
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))], layout=go.Layout(title="<b>" + self.instance + "</b><br><br>Parties in the parliament using " + self.electoral_system))
        fig.show()