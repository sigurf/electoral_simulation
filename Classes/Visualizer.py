import json
import os
import plotly.graph_objects as go
from Classes.Election_Analyzer import Election_Analyzer


"""
    Class that can visualize the election data, analysis and result according to the instance.

"""
class Visualizer:

    """
        Initializes the Visualizer class.

        @param  instance    a loaded yaml-file found in the Instances directory, specifying the data used.
    """
    def __init__(self, instance):

        self.instance = instance["name"]
        self.ea = Election_Analyzer(instance)

        # Loads map of Norway
        current_directory = os.path.dirname(__file__)
        json_file_path = os.path.join(current_directory, "../Data/Maps", instance["data"]["map_json"] + ".json")
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
        for county_index in range(len(self.ea.get_counties())):

            # Value is total number of votes in county
            county = self.ea.get_counties()[county_index]
            total_votes_in_county = self.ea.find_total_votes(county)
            total_votes.append(total_votes_in_county)

            # Label with each party's votes in the county hovered over
            label =f"<b>{county}: {total_votes[county_index]}</b><br>"
            for party in self.ea.get_parties():
                total_votes_to_party_in_county = self.ea.find_total_votes(county, party)
                label += f"{party}: {total_votes_to_party_in_county}<br>"
            vote_distribution.append(label)

        # Creates map with data showing how the votes are distributed
        vote_map = go.Choropleth(z=total_votes, geojson=self.geo_map, locations=self.ea.get_counties(),
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
        for county_index in range(len(self.ea.get_counties())):

            # Value is number of mandates in each county
            county = self.ea.get_counties()[county_index]
            total_mandates.append(self.ea.get_mandate_data()[self.ea.get_mandate_data()['County'] == county]['Mandates'].values[0])
            
            # Label with the number of mandates and the winning party in the county hovered over
            most_popular_party = self.ea.find_most_popular_party(county)
            label =f"<b>{county}: {total_mandates[county_index]}</b><br> {most_popular_party}"
            mandate_distribution.append(label)

            # The county is shown in the winning party's color
            colors.append(self.ea.get_party_colors()[self.ea.get_parties()[self.ea.get_parties() == most_popular_party].index[0]])


        # Creates map with data showing how the mandates are distributed according to FPTP
        mandate_map = go.Choropleth(z=colors, geojson=self.geo_map, locations=self.ea.counties,
                                colorscale="Rainbow",
                                zmin=0,
                                zmax=1,
                                featureidkey='properties.name',
                                hoverinfo = 'text',
                                showscale=False,
                                text=mandate_distribution
                            )
        mandate_map_layout = go.Layout(title = "<b>" + self.instance + "</b><br><br>Party receiving mandates from county")
        return mandate_map, mandate_map_layout
       

    """
        Shows the distribution of the political parties in the parliament when using FPTP.
    """
    def show_parliament_distribution(self):
        labels = list(self.ea.get_mandate_distribution().keys())
        values = list(self.ea.get_mandate_distribution().values())
        colors = self.ea.get_color_data()[self.ea.get_color_data()["Party"].isin(labels)]["Color"].tolist()
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))], layout=go.Layout(title="<b>" + self.instance + "</b><br><br>Parties in the parliament using FPTP"))
        fig.show()