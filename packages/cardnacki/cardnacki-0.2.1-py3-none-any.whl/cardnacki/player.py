from itertools import count, cycle
from dataclasses import dataclass, field

from .pile import Pile


@dataclass
class Player:
    id_: int = field(default_factory=count().__next__, init=False)
    pos: int = field(init=False)
    is_bot: bool = False
    user = None  # this would be a User
    piles: list[Pile] = field(default_factory=list, init=False)
    game_data: dict = None
    is_dealer: bool = False

    def __post_init__(self):
        self.pos = self.id_
        # commenting this because this is part of the cardnacki package and shouldn't have access to the User class
        # if self.is_bot:
        #     self.user = User('Mr Roboto', '', [{'war': {'wins': 3, 'losses': 5}}])

    @property
    def hand(self):
        return next(pile for pile in self.piles if pile.group == 'hand')

    @property
    def staged(self):
        return next(pile for pile in self.piles if pile.group == 'staged')
