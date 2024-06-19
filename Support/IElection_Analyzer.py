from abc import ABC, abstractmethod


"""
    Class containing abstract methods to be implemented in all Election_Analyzer classes.
"""
class IElection_Analyzer(ABC):

    @abstractmethod
    def get_election_data(self):
        pass

    @abstractmethod
    def get_district_data(self):
        pass

    @abstractmethod
    def get_party_data(self):
        pass

    @abstractmethod
    def get_mandate_distribution(self):
        pass