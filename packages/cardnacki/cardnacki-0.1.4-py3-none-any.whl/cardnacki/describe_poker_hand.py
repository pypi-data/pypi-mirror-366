from collections import Counter

from .card import Card


POKER_HANDS = ('Straight Flush', 'Four of a Kind', 'Full House', 'Flush', 'Straight',
               'Three of a Kind', 'Two Pair', 'One Pair', 'High Card')

def describe_poker_hand(h: list[Card], possible_outcomes: tuple[str, ...] = POKER_HANDS) -> str:
    rank_ints = [c.rank_int for c in h]
    rank_ctr = Counter([c.rank_int for c in h]).most_common()

    def is_straight(ri: list[int]) -> bool:
        if len(set(ri)) < 5:
            return False
        ranks: list[int] = sorted(set(ri))
        if ranks[4] - ranks[0] == 4 or (14 in ranks and ranks == [2, 3, 4, 5, 14]):
            return True
        return False

    def is_flush(cards: list[Card]) -> bool:
        return len({c.suit for c in cards}) == 1

    if 'Royal Flush' in possible_outcomes and is_flush(h) and is_straight(rank_ints) and \
            sorted(rank_ints)[4] == 14 and sorted(rank_ints)[3] == 13:
        return 'Royal Flush'

    if is_flush(h) and is_straight(rank_ints):
        return 'Straight Flush'

    if rank_ctr[0][1] == 4:
        return 'Four of a Kind'

    if rank_ctr[0][1] == 3 and rank_ctr[1][1] == 2:
        return 'Full House'

    if is_flush(h):
        return 'Flush'

    if is_straight(rank_ints):
        return 'Straight'

    if rank_ctr[0][1] == 3 and rank_ctr[1][1] != 2:
        return 'Three of a Kind'

    if rank_ctr[0][1] == 2 and rank_ctr[1][1] == 2:
        return 'Two Pair'

    if 'Jacks or Better' in possible_outcomes and rank_ctr[0][1] == 2 and rank_ctr[1][1] == 1 and rank_ctr[0][0] >= 11:
        return 'Jacks or Better'

    if rank_ctr[0][1] == 2 and rank_ctr[1][1] == 1:
        return 'One Pair'

    return 'High Card'