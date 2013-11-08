# -*- coding: utf-8 -*- 
from bot import SerendipityBot
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help="Don't submit anything to reddit.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Be verbose')
    parser.add_argument('-f', '--force-subreddit', 
                        help='Select the specified subreddit.')
    args = parser.parse_args()

    s = SerendipityBot(**args.__dict__)
    s.run()

if __name__ == "__main__":
    main()