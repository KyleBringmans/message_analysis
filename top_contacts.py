#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Plots the top-N contacts the user interacts with on Facebook in a pie chart
"""

from util import get_messages, get_params_from_config

from matplotlib import pyplot as plt


if __name__ == '__main__':
    path_to_config = 'config.yaml'
    args = get_params_from_config(path_to_config)

    # Number of contacts to find
    N = args['n']
    # Filename for plot
    F_NAME = args['f_name']
    FOLDERS_PATH = args['messages_folder']

    # Count number of interactions
    interactions = get_messages(FOLDERS_PATH, interactions=True)

    # Sort contacts by interactions
    sorted_interactions = sorted(interactions.items(), reverse=True, key=lambda a: a[1])

    # Prepare to N contacts for plotting
    x, y = zip(*sorted_interactions[:N])

    # Plot data
    fig, ax = plt.subplots(1, 1)
    plt.pie(y, labels=x, autopct='%1.1f%%')

    # Add grid
    plt.grid(True)
    # Move grid to back of figure
    ax.set_axisbelow(True)
    # Set title
    plt.title("Top {} most messaged contacts".format(N))

    # Save figure
    print("Writing figure to '{}'".format(F_NAME))
    plt.savefig('images/' + F_NAME)

    print("Done")
