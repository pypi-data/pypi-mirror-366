from itertools import chain, tee
from typing import Iterable

# TODO write doc tests?
# TODO add typevar / generics

def pairwise(iterable): 
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b) # TODO test.. 


def chain_flatten(lst: Iterable[Iterable]):
    return list(chain.from_iterable(lst))


def get_unique_items_in_list_keep_order(seq: Iterable):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
