from abc import ABC, abstractmethod


class Currency(ABC):

    @abstractmethod
    def __init__(self, name, amount, rate):
        self.name = name
        self.amount = amount
        self.rate = rate
