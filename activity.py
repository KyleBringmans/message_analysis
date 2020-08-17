#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Generates activity histograms of the top-N most contacted facebook friends
"""

from util import get_messages, get_color, get_params_from_config

import os
import sys
import json
from datetime import datetime
import time
import re

from pandas.plotting import register_matplotlib_converters
from matplotlib import pyplot as plt
import numpy as np
from termcolor import colored

if __name__ == '__main__':
    path_to_config = 'config.yaml'
    args = get_params_from_config(path_to_config)

    # Allow usage of pandas arrays in matplotlib
    register_matplotlib_converters()

    # Assign arguments to variables
    F_NAME = args['f_name']
    N = args['n']
    EQ_Y = args['eq_y']
    CUMULATIVE = args['cumulative']
    N_BINS = args['n_bins']
    FOLDERS_PATH = args['messages_folder']

    # Start and end date
    START = '01/09/2019'
    END = '20/08/2020'

    # factor with which unix timestamps differ from millisecond interval
    MS_OFFSET_FACTOR = 1000

    # Convert dates to unix time
    min_date = time.mktime(datetime.strptime(START, "%d/%m/%Y").timetuple()) * MS_OFFSET_FACTOR
    max_date = time.mktime(datetime.strptime(END, "%d/%m/%Y").timetuple()) * MS_OFFSET_FACTOR

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
    # Create bins for histogram
    bins = np.linspace(min_date, max_date, num=N_BINS)

    # Create strings of readable dates from unix time bins
    bins_f = [datetime.utcfromtimestamp(hist_bin / MS_OFFSET_FACTOR).strftime('%Y-%m-%d')
              for hist_bin in bins]
    # Remove half of the labels to space out the labels better
    for i, _ in enumerate(bins_f):
        if i % 3 != 0:
            bins_f[i] = ''

    # Remove people who you have not contacted within the timeframe
    to_remove = []
    for i, (p, mgs) in enumerate(messages.items()):
        # Get timestamps from messages
        try:
            mgs = [m['timestamp_ms'] for m in mgs]
        except KeyError as error:
            print("Key {} is missing in message".format(error))
            sys.exit()
        if not list(filter(lambda x: x > min_date, mgs)):
            to_remove.append(p)

    for p in to_remove:
        messages.pop(p)

    # Plot the data
    # Create subplots
    # Create 2 columns of plots
    print("Creating plots")
    WIDTH = 2
    HEIGHT = len(messages) // 2
    fig, axes = plt.subplots(HEIGHT, WIDTH, figsize=(20, 15))
    # Generate random colours for each histogram
    colors = np.random.rand(len(messages) ** 2, 3)
    # For each person plot their interaction activity
    msg_tuples = list(messages.items())
    for i, ax_lst in enumerate(axes):
        for j, ax in enumerate(ax_lst):
            p, mgs = msg_tuples[j + WIDTH * i]
            # Get timestamps from messages
            try:
                mgs = [m['timestamp_ms'] for m in mgs]
            except KeyError as error:
                print("Key {} is missing in message".format(error))
                sys.exit()
            # Plot user data in histogram their name as label and 50% colour transparency
            # i+1 and j+1 to avoid the zeros since 0*x = x*0 = 0*0 which is not unique
            if CUMULATIVE:
                values, base = np.histogram(mgs, bins=bins)
                # evaluate the cumulative
                cumulative = np.cumsum(values)
                # plot the cumulative function
                ax.fill_between(x=base[:-1], y1=0, y2=cumulative, label=p, color=next(get_color()), alpha=0.5)
            else:
                ax.hist(mgs, bins=bins, label=p, color=next(get_color()), alpha=0.8)
            # Set the x-ticks to the bins used in the histograms
            ax.xaxis.set_ticks(bins)
            # Set the x-tick labels to be the formatted bin labels
            ax.set_xticklabels(bins_f)
            # Set y-axis title
            ax.set_ylabel('# messages')
            # Show grid
            ax.grid(True)
            # Place grid behind other graph elements
            ax.set_axisbelow(True)
            # Show the legend
            ax.legend(loc='upper center')
            # Rotate x-axis labels 90 degrees to make them readable
            plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            # Add white space at the bottom to show the x-tick labels
    plt.tight_layout()

    # Make y-axes equal height if requested
    if EQ_Y:
        # Calculate maximum y value
        MAX_Y = 0
        for axes_lst in axes:
            for ax in axes_lst:
                _, top = ax.get_ylim()
                MAX_Y = max(MAX_Y, top)
        # Set all y-axis to this maximum measurement
        for axes_lst in axes:
            for ax in axes_lst:
                ax.set_ylim((0, MAX_Y))

    # Save figure
    print("Writing figure to '{}'".format(colored(F_NAME, 'cyan')))
    plt.savefig('images/' + F_NAME)

    print("Done")
