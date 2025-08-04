from enum import Enum, auto

from .card import Card


class CardComparisonRule(Enum):
    HIGHEST_RANK = auto()
    TRUMP_LEAD_SUIT = auto()
    LEAD_SUIT_HIGHEST_RANK = auto()


class CompareCards:
    """ Takes a list of cards and -- based on arguments -- returns index of the max value. If ties, return -1. """

    # ties probably shouldn't return negative one, maybe it should return all hand_id's that tied.
    # this is critical if more than two hands come in

    def __init__(self, compare_rule: CardComparisonRule):
        self.compare_rule = compare_rule
        self.compare_funcs = {CardComparisonRule.HIGHEST_RANK:
                              lambda cards, trump, lead_card: self.get_highest_rank(cards, trump, lead_card),
                              CardComparisonRule.TRUMP_LEAD_SUIT:
                              lambda cards, trump, lead_card: self.get_trump_lead_suit(cards, trump, lead_card),
                              CardComparisonRule.LEAD_SUIT_HIGHEST_RANK:
                              lambda cards, trump, lead_card: self.get_lead_suit_highest_rank(cards, trump, lead_card)}

    def compare(self, cards: list[Card], trump: str = None, lead_card: Card = None):
        return self.compare_funcs[self.compare_rule](cards, trump, lead_card)

    @staticmethod
    def get_highest_rank(cards: list[Card], trump: str, lead_card: Card) -> int:
        """Ties return -1"""
        rank_ints = [c.rank_int for c in cards]
        return rank_ints.index(max(rank_ints)) if rank_ints.count(max(rank_ints)) == 1 else -1
        # is this going to come back to bite me that i'm not returning the ties ???

    @staticmethod
    def get_trump_lead_suit(cards: list[Card], trump: str, lead_card: Card):
        raise NotImplementedError

    @staticmethod
    def get_lead_suit_highest_rank(cards: list[Card], trump: str, lead_card: Card):
        raise NotImplementedError
