#!/usr/bin/python

""" Generate website
"""
from collections import OrderedDict

from datetime import datetime

import pytz

from website import create_page, generate_sitemap
from website import SOURCE_DIR
from website import PAGE_FILE

import os

#
# Start the engine
#

tz = pytz.timezone('America/Los_Angeles')

sitemap_urls = OrderedDict()

for folder, subs, files in os.walk(SOURCE_DIR):

    map_folder = folder.replace(SOURCE_DIR, "")

    if map_folder != "404":
        file_time = int(os.path.getmtime(folder + "/" + PAGE_FILE))

        sitemap_data = dict()
        sitemap_data['url'] = map_folder
        sitemap_data['priority'] = 1 - (map_folder.count("/") * 0.15)
        sitemap_data['date'] = datetime.fromtimestamp(
            file_time
            , tz
        ).isoformat(' ')

        if map_folder not in sitemap_urls:
            sitemap_urls[map_folder] = dict()
        sitemap_urls[map_folder] = sitemap_data

    with open(os.path.join(folder, PAGE_FILE), 'r') as destination:
        for filename in files:
            if filename != PAGE_FILE:
                continue

            if os.path.isfile(folder + "/" + PAGE_FILE):
                create_page(folder, filename)

generate_sitemap(sorted(sitemap_urls.items()))
