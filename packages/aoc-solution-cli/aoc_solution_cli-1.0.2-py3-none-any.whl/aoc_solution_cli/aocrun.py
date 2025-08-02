# Copyright (C) taitep <taitep@taitep.se>
#
# This file is licensed under the GNU LGPL v3.
# See <https://www.gnu.org/licenses/>

import click
from aocd import get_data, submit
from importlib import import_module
from .recent_problem_saver import get_recent, day_to_module

import os
import sys
sys.path.insert(0, os.curdir)

@click.command
@click.argument('part')
@click.option('--day', type=int)
@click.option('--year', type=int)
@click.option('--submit/--no-submit', 'submit_attempt', default=False)
def aocrun(part, day, year, submit_attempt):
    part=part.lower()
    if part not in 'ab':
        print(f"'{part}' is not a valid part. Please use 'a' or 'b'.")
        exit(1)

    day, year = get_recent(day, year)
    try:
        module = import_module(day_to_module(day, year))
    except ModuleNotFoundError as e:
        print(f"Error: {e}. The module with solutions was not found. To generate it, run 'aocgen'.")
        exit(1)

    solution_function = getattr(module, f'solution_{part}')
    answer = solution_function(get_data(day=day, year=year).splitlines())
    print(f'Result: {answer}')
    if submit_attempt: submit(answer, day=day, year=year, part=part)

if __name__ == '__main__':
    aocrun()
