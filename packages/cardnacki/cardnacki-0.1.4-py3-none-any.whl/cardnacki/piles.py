from copy import copy

from .card import Card
from .pile import Pile, PileType


class Piles:
    """ This class is used to reach across multiple Pile objects; useful for moving cards between piles, etc.
    Grouping these methods into this class should make for a simpler import """

    @staticmethod
    def move_card(card: Card, from_: Pile, to: Pile, *, from_location='top', to_location='top', face_up: bool = None):
        card_to_move = copy(card)
        from_.remove_card(card, from_location)
        to.add_card(card_to_move, to_location, face_up)

    @staticmethod
    def move_all_cards(from_: Pile, to: Pile, to_location='top', face_up: bool = None):
        cards: list[Card] = from_.cards[:]
        from_.remove_all_cards()
        [to.add_card(card, to_location, face_up) for card in cards]

    @staticmethod
    def get_staged_piles(piles: list[Pile]) -> list[Pile]:
        return [pile for pile in piles if pile.type == PileType.STAGED]

    @staticmethod
    def last_face_up_cards_in_staged_piles(piles: list[Pile]) -> list[Card]:
        return [pile.last_face_up_card for pile in Piles.get_staged_piles(piles)]

    @staticmethod
    def clear_staged_piles(piles: list[Pile]) -> None:
        [pile.remove_all_cards() for pile in piles if pile.type == PileType.STAGED]

    @staticmethod
    def deal(piles: list[Pile], button_pos: int, cards_per_pile: int, from_: Pile, cards_per_shove: int = 1):
        """ If cards_per_pile is -1, deal entire pile
        Set order; dealer is last.  Ex: player positions=[0, 1, 2], button=1, order = [2, 0, 1]
        Cards per shove currently isn't supported ... """

        ordered_piles = piles if button_pos == len(piles) else piles[button_pos+1:] + piles[:button_pos+1]
        if cards_per_pile == -1:
            # Deal cards to players and remove them from the deck
            for i in range(len(from_)):
                pile_idx = i % len(piles)
                Piles.move_card(from_.top_card, from_, ordered_piles[pile_idx], face_up=True)
        else:
            for i in range(cards_per_pile * len(piles)):
                pile_idx = i % len(piles)
                Piles.move_card(from_.top_card, from_, ordered_piles[pile_idx], face_up=True)
