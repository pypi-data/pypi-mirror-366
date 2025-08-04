from collections import Counter

from .card import Card


POKER_HANDS = ('Straight Flush', 'Four of a Kind', 'Full House', 'Flush', 'Straight',
               'Three of a Kind', 'Two Pair', 'One Pair', 'High Card')

def describe_poker_hand(h: list[Card], possible_outcomes: tuple[str, ...] = POKER_HANDS) -> str:
    rank_ints = [c.rank_int for c in h]
    rank_ctr = Counter([c.rank_int for c in h]).most_common()
    sorted_rank_set = sorted(set(rank_ints))

    is_flush = len({c.suit for c in h}) == 1
    is_straight = len(sorted_rank_set) == 5 and ((sorted_rank_set[-1] - sorted_rank_set[0] == 4) or (sorted_rank_set == [2, 3, 4, 5, 14]))

    if is_flush and is_straight:
        if 'Royal Flush' in possible_outcomes and sorted_rank_set[4] == 14 and sorted_rank_set[3] == 13:
            return 'Royal Flush'
        return 'Straight Flush'

    max_pair_cnt = rank_ctr[0][1] if len(rank_ctr) > 0 else 0
    second_max_pair_cnt = rank_ctr[1][1] if len(rank_ctr) > 1 else 0

    if max_pair_cnt == 4:
        return 'Four of a Kind'

    if max_pair_cnt == 3 and second_max_pair_cnt == 2:
        return 'Full House'

    if is_flush:
        return 'Flush'

    if is_straight:
        return 'Straight'

    if max_pair_cnt == 3 and second_max_pair_cnt != 2:
        return 'Three of a Kind'

    if max_pair_cnt == 2 and second_max_pair_cnt == 2:
        return 'Two Pair'

    if 'Jacks or Better' in possible_outcomes and max_pair_cnt == 2 and rank_ctr[0][0] >= 11:
        return 'Jacks or Better'

    if max_pair_cnt == 2 and second_max_pair_cnt == 1:
        return 'One Pair'

    return 'High Card'