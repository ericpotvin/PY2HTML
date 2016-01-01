#!/usr/bin/python

""" Generate website
"""

from website import create_page
from website import SOURCE_DIR
from website import PAGE_FILE
import os

#
# Start the engine
#

for folder, subs, files in os.walk(SOURCE_DIR):

    with open(os.path.join(folder, PAGE_FILE), 'r') as dest:
        for filename in files:
            if filename != PAGE_FILE:
                continue

            if os.path.isfile(PAGE_FILE):
                create_page(folder, filename)
