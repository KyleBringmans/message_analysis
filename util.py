# Author: Kyle Bringmans

import json
import yaml
import os
import sys

import numpy as np
import re

from termcolor import colored


def listdir_no_hidden(path):
    """
    Yield subdirectories without hidden files
    Parameters
    ----------
    path : str
        The path to the directory to list

    Returns
    -------
    f : str
        a subdirectory name
    """
    for directory in os.listdir(path):
        if not directory.startswith('.'):
            yield directory


def get_color():
    """
    Return a random RGB colour

    Returns
    -------
    list
        list of 3 random floats which represents an RGB colour
    """
    while True:
        yield np.random.uniform(low=0, high=1, size=(3,))


def get_messages(path_to_folders, interactions=False):
    # List all contacts
    ppl = listdir_no_hidden(path_to_folders)

    # Count number of interactions
    messages = {}
    # Iterate over all contacts
    for p in ppl:
        # Get proper name of person without suffix and add space between name and surname
        p_name = re.sub(r"(\w)([A-Z])", r"\1 \2", p.split('_')[0])
        try:
            p_path = path_to_folders + '/' + p
            # Iterate over all message files for contact p
            for fn in listdir_no_hidden(p_path):
                if 'message' in fn:
                    with open(p_path + '/' + fn) as json_file:
                        data = json.load(json_file)
                        # Add total interactions to existing count for person p
                        if interactions:
                            messages[p] = messages.get(p, 0) + len(data['messages'])
                        else:
                            messages[p_name] = messages.get(p_name, []) + data['messages']
        except FileNotFoundError as error:
            print("ERROR key {} not found in dict".format(error))
    return messages


def get_params_from_config(path):
    with open(path, 'r') as stream:
        try:
            params = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    path_to_script = sys.argv[0]
    f_name = path_to_script.split('/')[-1]
    image_name = f_name.replace('.py', '.png')
    params['f_name'] = image_name

    print(colored("Arguments used:\n", 'green'))

    for arg, val in params.items():
        print("{}: {}".format(arg, colored(val, 'magenta')))
    print("-----")
    return params
