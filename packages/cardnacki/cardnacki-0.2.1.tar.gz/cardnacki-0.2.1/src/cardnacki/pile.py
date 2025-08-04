from dataclasses import dataclass
from itertools import count
import random
from typing import Optional
from enum import Enum, auto

from .card import Card, deck_unshuffled


class PileType(Enum):
    DECK = auto()
    DISCARD = auto()
    STAGED = auto()
    HAND = auto()


@dataclass
class PileProps:
    """Dataclass that evaluates aspects of a list of cards. Can be part of a Pile or instantiated independently.
    Attributes: cards: list[Card] & the_suit: str (helpful if used in some type of trump game)
    """
    cards: list[Card]
    the_suit: str = None

    @property
    def suits(self) -> set:
        """Return a set of suits contains in cards"""
        return {c.suit for c in self.cards}

    @property
    def suit_cards(self) -> list[Card]:
        """Returns cards of a self.the_suit ordered by rank_int desc"""
        return sorted([c for c in self.cards if c.suit == self.the_suit], key=lambda x: x.rank_int, reverse=True)

    @property
    def non_suit_cards(self) -> list[Card]:
        return [c for c in self.cards if c.suit != self.the_suit]

    @property
    def suit_length(self) -> int:
        return len(self.suit_cards)

    @property
    def suit_rank_ints(self) -> list[int]:
        return sorted([c.rank_int for c in self.suit_cards], reverse=True)

    def suit_length_by_ranks(self, ranks: list[int]) -> int:
        return len([c for c in self.suit_cards if c.rank_int in ranks])

    def suit_has_rank(self, rank: int) -> bool:
        """Accepts a rank (e.g. 11 for Jack), returns bool if card exists for self.the_suit"""
        return rank in self.suit_rank_ints

    def suit_has_any_ranks(self, ranks: list[int]) -> bool:
        return any(c in self.suit_rank_ints for c in ranks)

    @property
    def suit_highest_card(self) -> Card | None:
        return self.suit_cards[0] if self.suit_length else None

    @property
    def suit_second_highest_card(self) -> Card | None:
        return self.suit_cards[1] if self.suit_length >= 2 else None

    def has_a_non_suit_rank(self, rank: int) -> bool:
        return rank in [c.rank_int for c in self.non_suit_cards]


def create_cards_from_rank_suits(deck: "Deck", rank_suits: str) -> list[Card] | list[None]:
    """Accepts a deck & string of rank_suits, such as 'Ah Kh As Tc' or 'Ah'.
    Error thrown if rank_suits aren't unique or rank_suit doesn't exist in a standard deck.
    If nothing is provided, return an empty list.
    Note: the deck is important because properties may be applied to the cards in that deck, so we need to ACCESS cards,
    not CREATE them here"""
    if not rank_suits:
        return []
    deck_rank_suits = {c.rank_suit for c in deck.cards}
    rank_suits = rank_suits.split(' ')
    if len(set(rank_suits)) != len(rank_suits):
        raise ValueError("You have a duplicate card")
    cards = []
    for rank_suit in rank_suits:
        if rank_suit not in deck_rank_suits:
            raise ValueError(f"'{rank_suit}' not in the deck.")
        cards.append(next(c for c in deck.cards if c.rank_suit == rank_suit))
    return cards

class Pile:
    def __init__(self, cards: list[Card | None], *,
                 type_=None, owner=None, start_shuffled=False, face_up_default=False):
        self.id_ = count().__next__
        self.cards: list[Card] = cards if cards else []
        self.owner: str = owner
        self.face_up_default: bool = face_up_default
        self.pile_props: PileProps = PileProps(self.cards)
        self.type: str = type_
        if start_shuffled:
            self.shuffle()

    @classmethod
    def create_from_rank_suits(cls, deck, rank_suits: str):
        """Alternate constructor from a string of rank_suits, such as 'Ah Kh As Tc' or 'Ah'.
        Error thrown if Rank_suits aren't unique or rank_suit doesn't exist in a standard deck.
        If nothing is provided, return an empty list."""
        cards = create_cards_from_rank_suits(deck, rank_suits)
        return cls(cards)

    def to_rank_suits(self) -> str:
        return ' '.join([c.rank_suit for c in self])

    def __repr__(self):
        return f'{self.cards}'

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, rank_suits: str) -> Card | list[Card] | None:
        """This is helpful for tests where the test needs a card or list of cards.
        Example call would be: deck['Kh'] or deck['Ah Kh'].
        deck['Kh'] returns Card; deck['Ah Kh'] returns list[Card]; deck[''] returns None; deck['Xa'] throws."""
        rank_suit_list: list[str] = rank_suits.split(' ')
        if len(set(rank_suit_list)) != len(rank_suit_list):
            raise ValueError('Your cards must be unique')
        if rank_suits == '' or len(rank_suit_list) == 0:
            return None
        if len(rank_suit_list) == 1:
            return next((c for c in self.cards if c.rank_suit == rank_suit_list[0]), ValueError(f"Card not in the deck."))
        return [c for c in self.cards for rs in rank_suit_list if c.rank_suit == rs]

    @property
    def card_cnt(self) -> int:
        return len(self)

    @property
    def top_card(self) -> Card:
        return self.cards[0]

    @property
    def bottom_card(self) -> Card:
        return self.cards[-1]

    @property
    def last_face_up_card(self) -> Optional[Card]:
        """May return None"""
        for c in self.cards[::-1]:
            if c.face_up:
                return c

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def add_card(self, card: Card, location: str = 'top', face_up: bool = None):
        self.cards.append(card) if location == 'bottom' else self.cards.insert(0, card)
        self.set_face_side(card, face_up)

    def set_face_side(self, card, face_up: bool = None):
        card.face_up = self.face_up_default if face_up is None else face_up

    def add_all_cards(self, cards: list[Card], location: str = 'top', face_up: bool = None):
        [self.cards.append(card) if location == 'bottom' else self.cards.insert(0, card) for card in cards]
        for card in cards:
            card.face_up = self.face_up_default if face_up is None else face_up

    def remove_card(self, card: Card = None, location: str = 'top'):
        if card:
            self.cards.remove(card)
        else:
            self.cards.pop() if location == 'bottom' else self.cards.pop(0)

    def remove_all_cards(self):
        self.cards.clear()

    def sort_by_rank(self, descending: bool = False):
        self.cards.sort(key=lambda card: card.rank_int, reverse=descending)

    def move_card(self, card: Card, location: str = 'top'):
        self.cards.remove(card)
        self.cards.append(card) if location == 'bottom' else self.cards.insert(0, card)


def create_deck():
    return [Card(idx, *c) for idx, c in enumerate(deck_unshuffled)]


class Deck(Pile):
    def __init__(self, start_shuffled: bool = False):
        super().__init__(create_deck(), type_=PileType.DECK)
        if start_shuffled:
            self.shuffle()


class Discard(Pile):
    def __init__(self):
        super().__init__([], type_=PileType.DISCARD, face_up_default=True)
