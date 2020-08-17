#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Plots the top-N contacts the user interacts with on Facebook in a pie chart
"""
from util import get_messages

from datetime import datetime

from matplotlib import pyplot as plt

if __name__ == '__main__':
    # Number of contacts to find
    N = 15
    # Filename for plot
    F_NAME = 'top_n.png'
    FOLDERS_PATH = 'messages/inbox'

    messages = get_messages(FOLDERS_PATH)

    # Get the year number for each message of each person
    for p, mgs in messages.items():
        # Get year
        mgs = [int(datetime.utcfromtimestamp(m['timestamp_ms'] / 1000).strftime('%Y')) for m in mgs]
        # Overwrite messages with years
        messages[p] = mgs

    # For each year get the contacts sorted by amount of messages
    yrs = list(range(2010, 2021))
    # Top contacts for each year
    top_for_yrs = []
    for yr in yrs:
        # Top contacts for a single year
        top_for_yr = []
        # Get the messages for each person
        for p, mgs in messages.items():
            # Keep the name and amount of messages for later color calculation
            top_for_yr.append([p, mgs.count(yr)])
        # Sort them in reverse
        top_for_yr = sorted(top_for_yr, reverse=True, key=lambda a: a[1])
        # Add them to the total list
        top_for_yrs.append([yr, top_for_yr])

    # Create subplots
    fig, ax = plt.subplots(len(yrs), 1, figsize=(20, 30))
    for i, (yr, top_n) in enumerate(top_for_yrs):
        # Unzip the list of all the contacts for a single year
        ppl, mgs = zip(*top_n)
        ppl = list(ppl)
        # Calculate the colours of the histogram
        colors = []
        if i != 0:
            for p, _ in top_n:
                # Get the top contacts for the previous year
                _, l_ppl = top_for_yrs[i - 1]
                # Unzip the contact list of last year and get only the names
                l_ppl, _ = zip(*l_ppl)
                try:
                    # Get the index of the person for last year
                    prev_index = l_ppl.index(p)
                except ValueError:
                    # If the contact was not befriended with you the year before, assume the amount of messages
                    # has increased and assign the green colour (-1 is smaller than any natural number)
                    prev_index = -1
                # Red if the interactions have decreased (higher index, more to the right in the plot)
                if prev_index < ppl.index(p):
                    colors.append('red')
                # Yellow if the interactions have stayed the same
                elif prev_index == ppl.index(p):
                    colors.append('yellow')
                # Green if the interactions have increased (lower index, more to the left in the plot)
                else:
                    colors.append('green')
        # Set colour of the first year to blue
        if not colors:
            colors = 'blue'
        # Remove entries if they have 0 messages because this will not provide useful data
        for j, mg in enumerate(mgs):
            if mg == 0:
                ppl[j] = ''
        # Create bar plot for a given year with the provided colours
        ax[i].bar(ppl[:N], mgs[:N], color=colors, alpha=0.8)
        # Set y-axis title
        ax[i].set_ylabel('# messages')
        # Show grid
        ax[i].grid(True)
        # Place grid behind other graph elements
        ax[i].set_axisbelow(True)
        # Show the legend
        colors = {'higher compared to prev year': 'green', 'Same compared to prev year': 'yellow',
                  'Lower compared to prev year': 'red', }
        labels = list(colors.keys())
        handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label]) for label in labels]
        ax[i].legend(handles, labels)
        # Rotate x-axis labels 90 degrees to make them readable
        plt.setp(ax[i].get_xticklabels(), rotation=5, horizontalalignment='right')
        # Set the title for the subplot to the year for which the data is shown
        ax[i].set_title(yr)
    # Resize the saved image to the correct resolution so all items are shown
    plt.tight_layout()
    plt.savefig('images/' + 'activity_over_the_years.png')
