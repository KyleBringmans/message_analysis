#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Generates activity histograms of the top-N most contacted facebook friends
"""

from util import get_messages, get_params_from_config

import os
import sys
import json
from datetime import datetime
import time
import re

from pandas.plotting import register_matplotlib_converters
from termcolor import colored


if __name__ == '__main__':
    path_to_config = 'config.yaml'
    args = get_params_from_config(path_to_config)

    # Allow usage of pandas arrays in matplotlib
    register_matplotlib_converters()

    # Assign arguments to variables
    F_NAME = args['f_name']
    N = args['n']
    USERNAME = args['username']
    FOLDERS_PATH = args['messages_folder']

    # Start and end date
    START = '01/09/2019'
    END = '20/08/2020'

    # factor with which unix timestamps differ from millisecond interval
    MS_OFFSET_FACTOR = 1000

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
