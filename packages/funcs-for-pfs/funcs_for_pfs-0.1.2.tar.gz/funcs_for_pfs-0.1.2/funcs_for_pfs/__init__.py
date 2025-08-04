# toolzのドキュメント：https://toolz.readthedocs.io/en/latest/api.html
from toolz.curried import *
# operatorのドキュメント：https://docs.python.org/ja/3/library/operator.html
from operator import eq, ne, lt, le, ge, gt, add, sub, mul, truediv, floordiv, mod, contains, not_, and_, or_, xor, methodcaller, attrgetter
from itertools import cycle, filterfalse
import re
import os
import json
from glob import glob
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor


c_ = compose
c_l_ = compose_left
or__ = lambda a,b:a or b
and__ = lambda a,b:a and b
next_d = curry(lambda iter_, default: next(iter_, default))
join_ = lambda f1, f2, f3: lambda x: f1(f2(x), f3(x))
join_2 = lambda f1, f2, f3: lambda x, y: f1(f2(x), f3(y))
fork = lambda join, f1, f2: lambda x: join(f1(x), f2(x))
fork_2 = lambda join, f1, f2: lambda x, y: join(f1(x), f2(y))
if_ = lambda f1, f2, f3: lambda x: f2(x) if f1(x) else f3(x)
true_ = lambda x: lambda *args: x
true_f = lambda x: lambda *args: x()
true_do = true_f
filter_l = curry(compose(list, filter))
map_l = curry(compose(list, map))
reduce_init = curry(lambda f, seq, init=None: reduce(f, seq, init) if init else reduce(f, seq))
@curry
def find_first(condition, iterable, default=None):
    return next(filter(condition, iterable), default)

eq = curry(eq)
ne = curry(ne)
lt_ = curry(flip(lt))
le_ = curry(flip(le))
ge_ = curry(flip(ge))
gt_ = curry(flip(gt))
lt = curry(lt)
le = curry(le)
ge = curry(ge)
gt = curry(gt)
and_ = curry(and_)
xor = curry(xor)
or_ = curry(or_)
floordiv_ = curry(flip(floordiv))
add = curry(add)
add_ = curry(flip(add))
increment = add(1)
sub = curry(sub)
sub_ = curry(flip(sub))
mul = curry(mul)
div = curry(truediv)
div_ = curry(flip(truediv))
floordiv = curry(floordiv)
mod = curry(mod)
is_even = lambda n: n % 2 == 0
is_odd = complement(is_even)
contains = curry(contains)
filterfalse = curry(filterfalse)
sorted = curry(sorted)

create_list = lambda *args:list(args)
create_tuple = lambda *args:args

# １つの関数の各引数に、１つの関数を適用する関数を返す
def composes(f, *arg_fs):
    def exec_(*args):
        if len(arg_fs) > len(args):
            return partial(exec_, *args)
        vals = [arg_f(arg) for arg_f, arg in zip(arg_fs, args)]
        return f(*vals, *args[len(vals):])
    return exec_

@curry
def alternation(f1, f2, val):
    f1_val = f1(val)
    return f1_val if f1_val else f2(val)

# how to : alt(default, value)
alt = composes(partial(alternation, identity), true_)

@curry
def every(func, iterable):
    for element in iterable:
        if not func(element):
            return False
    return True

@curry
def some(func, iterable):
    for element in iterable:
        if func(element):
            return True
    return False

@curry
def while_(judge_f, process_f):
    def while_process(x):
        while judge_f(x):
            x = process_f(x)
        return x
    return while_process

@curry
def rangemap(rangemap, var, default=None):
    for k, v in rangemap.items():
        if var < k:
            return v
    return v if default else default

@curry
def parallel_map(func, iterable, max_workers=None, timeout=None):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return executor.map(func, iterable)

re_search = curry(re.search)
re_sub = curry(re.sub)
re_split = curry(re.split)
re_findall = curry(re.findall)

def get_dict(key, dic, default):
    return dic[key] if key in dic.keys() else default
