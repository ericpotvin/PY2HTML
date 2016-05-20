# PY2HTML

A simple Python script that generates a static HTML website

## Requirements

Python 2.7
Jinja2

### Install Jinja2
```
sudo apt-get install python-pip
sudo pip install jinja2
```

### page.ini

This is the page.ini used for each page of the website.

```
[info]
title = My page title
description = My page full description

created_date = 0 " timestamp
updated_date = 0 " timestamp
```

### config.ini

This is the config.ini for the website. This file is required.

Example:
```
[config]
name = Name Of My Website
url = mydomain.com
destination = /path/where/the/website/is/generated/

[menu]
ignore_files = about,privacy-policy,terms-of-conditions,404 
```

### index.html

The content of the page in HTML format

## Generate

./generate.py /path/to/website-source/
