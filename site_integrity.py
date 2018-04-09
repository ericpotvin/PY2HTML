#!/usr/bin/python
""" Validate the site integrity
    Make sure the page.ini exists
    Make sure the index.html exists
"""

import os
import string
import sys

from website import PAGE_FILE, PAGE_INDEX

AUTO_CREATE_PAGE_INI = False
REQUEST_INPUT = False


def get_page_ini(title, description):
    """Get the page.ini content
    """
    content = "[info]\n"
    content += "title = " + title + "\n"
    content += "description = " + description + "\n\n"
    content += "created_date = 0 \n"
    content += "updated_date = 0 \n\n"

    return content


def replace_char(data):
    """ Replace URL to Words
    """
    replacements = (
        {'./': ''},
        {'-': ' '},
        {'/': ' - '}
    )
    for replacement in replacements:
        for rep_from, rep_to in replacement.items():
            data = data.replace(rep_from, rep_to)

    return data


def create_page_ini(path):
    """ Create a sample page.ini
    """
    title = string.capwords(replace_char(path))
    description = ""

    if REQUEST_INPUT:
        tmp = raw_input("     Title of the page [" + title + "]: ")
        if tmp:
            title = tmp
        tmp = raw_input("     Description of the page []: ")
        if tmp:
            description = tmp

    # ask for input and show default

    page_file = open(path + "/" + PAGE_FILE, 'w')
    page_file.write(get_page_ini(title, description))
    page_file.close()


def check_ini(path):
    """ Check if the page.ini file is present
    """
    return os.path.isfile(path + "/" + PAGE_FILE)


def check_html(path):
    """ Check if the index.html file is present
    """
    return os.path.isfile(path + "/" + PAGE_INDEX)


for root, dirs, files in os.walk(sys.argv[1]):

    if root[0:6] == './.git':
        continue

    if not check_ini(root):
        print " * The page.ini file is missing for: %s" % root

        if AUTO_CREATE_PAGE_INI:
            print "   Creating the page.ini for: %s" % root
            create_page_ini(root)

    if not check_html(root):
        print " * The index.html file is missing for: %s" % root

print "Done"
