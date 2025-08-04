from dataclasses import dataclass, field

deck_unshuffled = [[2, '2', 'hearts', '🂲'], [3, '3', 'hearts', '🂳'], [4, '4', 'hearts', '🂴'],
                    [5, '5', 'hearts', '🂵'], [6, '6', 'hearts', '🂶'], [7, '7', 'hearts', '🂷'],
                    [8, '8', 'hearts', '🂸'], [9, '9', 'hearts', '🂹'], [10, 'T', 'hearts', '🂺'],
                    [11, 'J', 'hearts', '🂻'], [12, 'Q', 'hearts', '🂽'], [13, 'K', 'hearts', '🂾'],
                    [14, 'A', 'hearts', '🂱'], [2, '2', 'clubs', '🃒'], [3, '3', 'clubs', '🃓'],
                    [4, '4', 'clubs', '🃔'], [5, '5', 'clubs', '🃕'], [6, '6', 'clubs', '🃖'],
                    [7, '7', 'clubs', '🃗'], [8, '8', 'clubs', '🃘'], [9, '9', 'clubs', '🃙'],
                    [10, 'T', 'clubs', '🃚'], [11, 'J', 'clubs', '🃛'], [12, 'Q', 'clubs', '🃝'],
                    [13, 'K', 'clubs', '🃞'], [14, 'A', 'clubs', '🃑'], [2, '2', 'diamonds', '🃂'],
                    [3, '3', 'diamonds', '🃃'], [4, '4', 'diamonds', '🃄'], [5, '5', 'diamonds', '🃅'],
                    [6, '6', 'diamonds', '🃆'], [7, '7', 'diamonds', '🃇'], [8, '8', 'diamonds', '🃈'],
                    [9, '9', 'diamonds', '🃉'], [10, 'T', 'diamonds', '🃊'], [11, 'J', 'diamonds', '🃋'],
                    [12, 'Q', 'diamonds', '🃍'], [13, 'K', 'diamonds', '🃎'], [14, 'A', 'diamonds', '🃁'],
                    [2, '2', 'spades', '🂢'], [3, '3', 'spades', '🂣'], [4, '4', 'spades', '🂤'],
                    [5, '5', 'spades', '🂥'], [6, '6', 'spades', '🂦'], [7, '7', 'spades', '🂧'],
                    [8, '8', 'spades', '🂨'], [9, '9', 'spades', '🂩'], [10, 'T', 'spades', '🂪'],
                    [11, 'J', 'spades', '🂫'], [12, 'Q', 'spades', '🂭'], [13, 'K', 'spades', '🂮'],
                    [14, 'A', 'spades', '🂡']]

rank_name_dict = {2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine',
                  10: 'Ten', 11: 'Jack', 12: 'Queen', 13: 'King', 14: 'Ace'}


@dataclass
class Card:
    id_: int
    rank_int: int
    rank_str: str
    suit: str
    img_front: str
    img_back: str = '🂠'
    rank_full_name: str = field(init=False)
    full_name: str = field(init=False)
    rank_suit: str = field(init=False)
    face_up: bool = False
    is_flippable: bool = True
    attributes: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.rank_full_name = rank_name_dict[self.rank_int]
        self.full_name = f'{self.rank_full_name} of {self.suit}'
        self.rank_suit = f'{self.rank_str}{self.suit[:1]}'

    def __repr__(self):
        return f'{self.rank_suit} {self.img}'

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return any([self.rank_suit == other.rank_suit, self.suit == other.suit and self.rank_int == other.rank_int])

    @property
    def img(self):
        return self.img_front if self.face_up else self.img_back

    def flip(self):
        self.face_up = False if self.face_up else True

    def flip_face_down(self):
        self.face_up = False

    def flip_face_up(self):
        self.face_up = True
