#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Plots the amount of user interactions with the chat for each user sorted by amount of interactions
"""

from util import get_params_from_config

import json
import os

from pandas.plotting import register_matplotlib_converters
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # Allow usage of pandas arrays in matplotlib
    register_matplotlib_converters()

    path_to_config = 'config.yaml'
    args = get_params_from_config(path_to_config)

    N = args['n']
    F_NAME = args['f_name']
    GROUPCHAT_NAME = 'E_4nFvy2IPiQ'
    PATH = args['messages_folder'] + GROUPCHAT_NAME

    # Find all users in groupchat
    messages = []
    for fn in os.listdir(PATH):
        if 'message' in fn:
            with open(PATH + '/' + fn) as json_file:
                data = json.load(json_file)
                messages = data['messages']
                ppl = [p['name'] for p in data['participants']]

    # Count number of messages per person
    info = {}
    for message in messages:
        sender = message['sender_name']
        info[sender] = info.get(sender, 0) + 1

    # Sort users by number of sent messages
    info = sorted(info.items(), reverse=True, key=lambda p: p[1])

    # Prepare data for plot
    x, y = list(zip(*info))

    # Plot data
    fig, ax = plt.subplots(1, 1)
    plt.scatter(x, y, marker='x', color='r')
    plt.plot(x, y)

    line_y = [max(y) * 0.375] * len(y)

    plt.plot(x, line_y, label='Admin cut-off', color='green')

    plt.legend()

    # Configuration options
    # Add grid
    plt.grid(True)
    # Move grid behind other graph elements
    ax.set_axisbelow(True)
    # Add more whitespace below plots to show full labels
    plt.gcf().subplots_adjust(bottom=0.25)
    # Rotate x-axis labels so they are all readable
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    # Rename y-axis
    ax.set_ylabel('# messages')
    # Set title
    plt.title("Activity in groupchat")

    # Save figure
    print("Writing figure to '{}'".format(F_NAME))
    plt.savefig('images/' + F_NAME)

    print("Done")
