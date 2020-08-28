#!/usr/bin/env python3
# Author: Kyle Bringmans

"""
Show the most contacted person per month
"""

from util import get_messages, get_params_from_config


from datetime import datetime
import time

from pandas.plotting import register_matplotlib_converters

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
    START = '01/10/2019'
    END = '20/08/2020'

    # factor with which unix timestamps differ from millisecond interval
    MS_OFFSET_FACTOR = 1000

    # Convert dates to unix time
    min_date = time.mktime(datetime.strptime(START, "%d/%m/%Y").timetuple()) * MS_OFFSET_FACTOR
    max_date = time.mktime(datetime.strptime(END, "%d/%m/%Y").timetuple()) * MS_OFFSET_FACTOR

    # Get messages from files
    messages = get_messages(FOLDERS_PATH)

    # Map messages to send times
    for p in messages:
        msg = [m['timestamp_ms'] for m in messages[p]]
        messages[p] = msg

    top_contacts = []
    while min_date < max_date:
        nxt_date = min_date + 2592000000
        interactions = {}
        for p, msg in messages.items():
            msg_slice = list(filter(lambda x: min_date <= x < nxt_date, msg))
            interactions[p] = len(msg_slice)
        sorted_interactions = sorted(interactions.items(), reverse=True, key=lambda x: x[1])
        top_contact = sorted_interactions[0]
        top_contacts.append(((min_date, nxt_date), top_contact))
        min_date = nxt_date

    for (start, end), contact in top_contacts:
        start = datetime.utcfromtimestamp(start/MS_OFFSET_FACTOR).strftime('%Y-%m')
        end = datetime.utcfromtimestamp(end/MS_OFFSET_FACTOR).strftime('%Y-%m')
        print("Top contact for ({} - {}) is: {}, with {} messages".format(start, end, contact[0], contact[1]))
