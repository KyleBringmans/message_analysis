#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Generates the distribution of interactions throughout the day for the top-N facebook contacts
"""

from util import listdir_no_hidden, get_color, get_params_from_config

import json
import os
from datetime import datetime
import time
import re

from pandas.plotting import register_matplotlib_converters
from matplotlib import pyplot as plt
import numpy as np


if __name__ == '__main__':
    # Allow usage of pandas arrays in matplotlib
    register_matplotlib_converters()

    path_to_config = 'config.yaml'
    args = get_params_from_config(path_to_config)

    # Filename to write figure to
    F_NAME = args['f_name']
    # Number of contacts to plot
    N = args['n']
    # Make all y-axes same height
    EQ_Y = args['eq_y']

    FOLDERS_PATH = args['messages_folder']
    # Start and end date
    START = '01/09/2019'
    END = '20/08/2020'

    # Convert dates to unix time
    min_date = time.mktime(datetime.strptime(START, "%d/%m/%Y").timetuple()) * 1000
    max_date = time.mktime(datetime.strptime(END, "%d/%m/%Y").timetuple()) * 1000

    # Get all contacts
    ppl = listdir_no_hidden(FOLDERS_PATH)

    # Count number of interactions
    interactions = {}
    # Iterate over all contacts
    for p in ppl:
        # Get proper name of person without suffix
        try:
            p_path = FOLDERS_PATH + '/' + p
            # Iterate over all message files for contact p
            for fn in listdir_no_hidden(p_path):
                if 'message' in fn:
                    with open(p_path + '/' + fn) as json_file:
                        data = json.load(json_file)
                        # Add total interactions to existing coun
                        interactions[p] = interactions.get(p, 0) + len(data['messages'])
        except FileNotFoundError as error:
            print("ERROR key {} not found in dict".format(error))

    # Sort contacts by interactions
    sorted_interactions = sorted(interactions.items(), reverse=True, key=lambda x: x[1])

    # Get all messages for top contacts
    messages = {}
    for p, nr in sorted_interactions[:N]:
        # Get proper name for person p without suffix and add spaces between name and surname
        p_rn = re.sub(r"(\w)([A-Z])", r"\1 \2", p.split('_')[0])
        print('processing {}'.format(p_rn))
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

    # Create bins for histogram
    bins = list(range(24))

    # Plot the data
    # Create subplots
    # Create 2 columns of plots
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
            mgs = [int(datetime.utcfromtimestamp(m['timestamp_ms'] / 1000)
                       .strftime('%H')) for m in mgs]
            # Plot user data in histogram their name as label and 50% colour transparency
            # i+1 and j+1 to avoid the zeros since 0*x = x*0 = 0*0 which is not unique
            ax.hist(mgs, bins=bins, label=p, color=next(get_color()), alpha=0.8, rwidth=0.8, density=True)
            # Set the x-ticks to the bins used in the histograms
            ax.xaxis.set_ticks(bins)
            # Set the x-tick labels to be the formatted bin labels
            ax.set_xticklabels(bins)
            # Set y-axis title
            ax.set_ylabel('% messages')
            # Show grid
            ax.grid(True)
            # Place grid behind other graph elements
            ax.set_axisbelow(True)
            # Show the legend
            ax.legend()
            # Rotate x-axis labels 90 degrees to make them readable
            plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
            # Add white space at the bottom to show the x-tick labels
    plt.tight_layout()

    # Save figure
    print("Writing figure to '{}'".format(F_NAME))
    plt.savefig('images/' + F_NAME)

    print("Done")
