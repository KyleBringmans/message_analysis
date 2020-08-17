#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Generates activity histograms of the top-N most contacted facebook friends
"""

from util import get_messages

import os
import sys
import json
from datetime import datetime
import time
import re
import argparse

from pandas.plotting import register_matplotlib_converters
from termcolor import colored


if __name__ == '__main__':
    # Define and create argument parser
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-fn', dest='F_NAME', default='activity.png',
                        help='Filename to write figure to')
    parser.add_argument('-n', dest='N', default=10,
                        help='Number of contacts to plot')
    parser.add_argument('-u', dest='USERNAME', default='Kyle Bringmans',
                        help='Name of user')

    args = parser.parse_args()

    print(colored("Arguments used:\n", 'green'))
    for arg, val in args.__dict__.items():
        print("{}: {}".format(arg, colored(val, 'magenta')))
    print("-----")

    # Allow usage of pandas arrays in matplotlib
    register_matplotlib_converters()

    # Assign arguments to variables
    F_NAME = args.F_NAME
    N = args.N
    USERNAME = args.USERNAME
    FOLDERS_PATH = 'messages/inbox'

    # Start and end date
    START = '01/09/2019'
    END = '20/08/2020'

    # factor with which unix timestamps differ from millisecond interval
    MS_OFFSET_FACTOR = 1000

    # Convert dates to unix time
    min_date = time.mktime(datetime.strptime(START, "%d/%m/%Y").timetuple()) * MS_OFFSET_FACTOR
    max_date = time.mktime(datetime.strptime(END, "%d/%m/%Y").timetuple()) * MS_OFFSET_FACTOR

    # Count number of interactions
    interactions = get_messages(FOLDERS_PATH, interactions=True)

    # Sort contacts by interactions
    print("Calculating top {} contacts".format(colored(N, 'red')))
    sorted_interactions = sorted(interactions.items(), reverse=True, key=lambda x: x[1])

    # Get all messages for top contacts
    messages = {}
    for p, nr in sorted_interactions[:N]:
        # Get proper name for person p without suffix and add spaces between name and surname
        p_rn = re.sub(r"(\w)([A-Z])", r"\1 \2", p.split('_')[0])
        print('Retrieving messages to/from {}'.format(colored(p_rn, 'yellow')))
        try:
            # Iterate over all message files for contact p
            p_path = FOLDERS_PATH + '/' + p
            for fn in os.listdir(p_path):
                if 'message' in fn:
                    with open(p_path + '/' + fn) as json_file:
                        data = json.load(json_file)
                        # Get messages from dataset
                        messages[p_rn] = messages.get(p_rn, []) + data['messages']
        except FileNotFoundError as error:
            print("File {} not found".format(error))
            sys.exit()

    for p, mgs in messages.items():
        a, b = 0, 0
        for m in mgs:
            try:
                if m['sender_name'] == USERNAME:
                    a += 1
                else:
                    b += 1
            except KeyError as error:
                print(error)
        interact_f = round(b / a, 3)
        print("Interaction factor for {} = {}".format(colored(p, 'yellow'), colored(interact_f, 'cyan')))
