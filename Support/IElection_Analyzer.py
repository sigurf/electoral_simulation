from abc import ABC, abstractmethod


"""
    Class containing abstract methods to be implemented in all Election_Analyzer classes.
"""
class IElection_Analyzer(ABC):

    @abstractmethod
    def get_vote_data(self):
        pass

    @abstractmethod
    def get_mandate_data(self):
        pass

    @abstractmethod
    def get_color_data(self):
        pass

    @abstractmethod
    def get_mandate_distribution(self):
        pass