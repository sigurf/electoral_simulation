import json
import os
import plotly.graph_objects as go
import sys

# Adds the path to Tools to sys.path
support_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Support"))
sys.path.append(support_path)
from Tools import Tools # type: ignore


"""
    Class that can visualize the election data, analysis and result according to the instance.

"""
class Visualizer:

    """
        Initializes the Visualizer class.

        @param  electoral_system    a chosen electoral system to simulate the instance on
        @param  instance            a loaded json-file found in the Instances directory, specifying the data used.
    """
    def __init__(self, electoral_system, instance):

        self.electoral_system = electoral_system

        # Adds the path to the electoral system to sys.path
        electoral_system_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ElectoralSystems", electoral_system))
        sys.path.append(electoral_system_path)
        from Election_Analyzer import Election_Analyzer # type: ignore
        ea = Election_Analyzer(instance)

        # Name of the instance ran
        self.instance = instance["name"]

        # Unprocessed dataframes
        self.election_data = ea.get_election_data()
        self.district_data = ea.get_district_data()
        self.party_data = ea.get_party_data()

        # Dataframes for all parties and districts
        self.parties = self.election_data[self.election_data["District"] == self.election_data.loc[0]["District"]]["Party"]
        self.districts = self.district_data["District"]

        self.party_colors = Tools.find_party_colors(self.party_data)

        # Dataframe of parliament mandate distribution for the given electoral system and instance
        self.mandate_distribution = ea.get_mandate_distribution()

        # Loads map of Norway
        current_directory = os.path.dirname(__file__)
        json_file_path = os.path.join(current_directory, "..", "Data", "Maps", instance["data"]["map_json"] + ".json")
        with open(json_file_path) as map:
            self.geo_map = json.load(map)
        
        # Visualizes maps and charts
        self.show_maps()
        self.show_parliament_distribution()


    """
        Visualizes the vote distribution and each districts winner using an interactive map.
    """
    def show_maps(self):
        maps = [self.get_vote_map(), self.get_mandate_map()]
        for map in maps:
            fig = go.Figure(data=map[0], layout=map[1])
            fig.update_geos(fitbounds='geojson', visible=False)
            fig.show()
        

    """
        Interactive map with information about the votes of each district.

        @return         map of districts containing the voting data.
        @return         layout of the map.
    """
    def get_vote_map(self):

        # Specifies value and label appearing when hovering over district
        total_votes = []
        vote_distribution = []
        for district_index in range(len(self.districts)):

            # Value is total number of votes in district
            district = self.districts[district_index]
            total_votes_in_district = Tools.find_total_votes(self.election_data, district)
            total_votes.append(total_votes_in_district)

            # Label with each party's votes in the district hovered over
            label =f"<b>{district}: {total_votes[district_index]}</b><br>"
            for party in self.parties:
                total_votes_to_party_in_district = Tools.find_total_votes(self.election_data, district, party)
                label += f"{self.party_data[self.party_data["Party"] == party]["EnglishName"].values[0]}: {total_votes_to_party_in_district}<br>"
            vote_distribution.append(label)

        # Creates map with data showing how the votes are distributed
        vote_map = go.Choropleth(z=total_votes, geojson=self.geo_map, locations=self.districts,
                                colorscale="Peach",
                                colorbar_title="Total amount of votes",
                                featureidkey='properties.name',
                                hoverinfo = 'text',
                                text=vote_distribution
                            )
        title_text = "<b style='font-size: 20>" + self.instance + "</b><br><br>Total votes by district and votes to party by district"
        vote_map_layout = go.Layout(title=go.layout.Title(text=title_text, font=go.layout.title.Font(size=16)))
        return vote_map, vote_map_layout


    """
        Interactive map showing the party with most votes in each district, and how many mandates
        the party receive.

        @return         map of districts showing the party with most votes and the mandates they receive.
        @return         layout of the map.
    """
    def get_mandate_map(self):

        # Specifies value and label appearing when hovering over district
        total_mandates = []
        mandate_distribution = []
        colors = []
        for district_index in range(len(self.districts)):

            # Value is the total number of mandates in each district
            district = self.districts[district_index]
            total_mandates.append(self.district_data[self.district_data['District'] == district]['Mandates'].values[0])
            
            # The label consists of number of mandates each party receives in each district
            label =f"<b>{district}: {total_mandates[district_index]}</b><br>"
            district_mandate_distribution = self.mandate_distribution[self.mandate_distribution['District'] == district][['Party', 'Mandates']]
            for _, row in district_mandate_distribution.iterrows():
                if row['Mandates'] > 0:
                    label += f"{self.party_data[self.party_data["Party"] == row['Party']]["EnglishName"].values[0]}: {row['Mandates']}<br>"
            mandate_distribution.append(label)


            # The district is shown in the most popular party's color
            colors.append(self.party_colors[self.parties[self.parties == Tools.find_most_popular_party(self.election_data, district)].index[0]])

        # Creates map with data showing how the mandates are distributed according to FPTP
        mandate_map = go.Choropleth(z=colors, geojson=self.geo_map, locations=self.districts,
                                colorscale="Rainbow",
                                zmin=0,
                                zmax=1,
                                featureidkey='properties.name',
                                hoverinfo = 'text',
                                showscale=False,
                                text=mandate_distribution
                            )
        title_text = "<b style='font-size: 20'>" + self.instance + "</b><br><br>Party receiving mandates from district using " + self.electoral_system
        mandate_map_layout = go.Layout(title=go.layout.Title(text=title_text, font=go.layout.title.Font(size=16), x=0.5))
        return mandate_map, mandate_map_layout
       

    """
        Shows the distribution of the political parties in the parliament when using FPTP.
    """
    def show_parliament_distribution(self):
        
        # Retrieves national mandate distribution from mandate distribution per district
        parliament_distribution = {}
        for _, row in self.mandate_distribution.iterrows():
            #party = self.party_data[self.party_data["Party"] == row['Party']]["EnglishName"].values[0]
            party = row['Party']
            mandates = row['Mandates']
            if mandates > 0:
                if party not in parliament_distribution.keys():
                    parliament_distribution[party] = 0
                parliament_distribution[party] += mandates
        
        # Sorts the dictionary alphabetically to visualize party in the correct color
        parliament_distribution = {party: parliament_distribution[party] for party in sorted(parliament_distribution, key=str.lower)}
        
        # Extracts lists from dictionary
        parties = list(parliament_distribution.keys())
        values = list(parliament_distribution.values())

        # Allocates the correct color to the parties
        colors = self.party_data[self.party_data["Party"].isin(parties)]["Color"].tolist()

        # Create label of English name of parties
        labels = [self.party_data[self.party_data["Party"] == party]["EnglishName"].values[0] for party in parties]


        # Visualizes pie chart showing parliament distribution
        title_text = "<b style='font-size: 20'>" + self.instance + "</b><br><br>Parties in the parliament using " + self.electoral_system + "<br> "
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors),  title=go.pie.Title(text=title_text, font=go.pie.title.Font(size=16)), showlegend=False, textinfo='label+value')])
        fig.show()