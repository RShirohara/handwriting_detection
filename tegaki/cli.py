# -*- coding: utf-8 -*-
# author: @RShirohara


import argparse

import tegaki


def get_args():
    parser = argparse.ArgumentParser(
        description=tegaki.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'model', type=str,
        help='Path to the directory where the tensorflow model exists.'
    )
    parser.add_argument(
        '-i', '--input', type=str, default=0,
        help='Resource URI of the input stream.'
    )
    parser.add_argument(
        '-m', '--max_size', type=int,
        help='Upperbound limit on the item in the queue.'
    )
    args = parser.parse_args()
    return args


def run():
    args = get_args()
    core = tegaki.Tegaki(
        model_dir=args.model,
        src=args.input,
        maxsize=args.max_size
    )
    core.run()


if __name__ == "__main__":
    run()
