# Copyright (C) taitep <taitep@taitep.se>
#
# This file is licensed under the GNU LGPL v3.
# See <https://www.gnu.org/licenses/>

import collections
import aocd

AoCDay = collections.namedtuple('AoCDay', ['day', 'year'])

def get_recent(day=None, year=None, file='.recent_problem'):
    try:
        with open(file, 'r') as f:
                saved_year, saved_day = tuple([int(i) for i in f.read().strip().split(' ')])
    except FileNotFoundError:
        saved_day, saved_year = None, None
    
    if not day: day = saved_day
    if not year: year = saved_year

    if not day or not year:
        aocd_day, aocd_year = aocd.get_day_and_year()
        if not day: day = aocd_day
        if not year: year = aocd_year

    if (day, year) != (saved_day, saved_year):
        with open(file, 'w') as f:
            f.write(f"{year} {day}")
    
    return AoCDay(day, year)


day_to_module = lambda day, year: f'aoc_{year}_{day}'
