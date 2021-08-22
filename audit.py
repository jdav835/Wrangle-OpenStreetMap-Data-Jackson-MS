#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

#counts unique UIDs
def count_users(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "node": 
            users.add(element.attrib['uid'])
    print " Number of unique Users: " ,len(users)    
    return 
    
def key_type(element, keys):
    if element.tag == "tag":
        
        if (lower.match(element.attrib['k'])):
            keys["lower"] += 1;
        elif (lower_colon.match(element.attrib['k'])):
            keys["lower_colon"] += 1;
        elif (problemchars.match(element.attrib['k'])):
            keys["problemchars"] += 1;
        else:
            keys["other"] += 1;
    return keys


#identify keys with different patterns
def count_keys(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    pprint.pprint(keys)
    return keys


   
#count all tags in file   
def count_tags(filename):

   dict = {}
   for event, elem in  ET.iterparse(filename):
       if elem.tag in dict.keys():
           dict[elem.tag] += 1;
       else:
           dict[elem.tag] = 1;
   print(dict)
   return dict

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


# ================================================== #
#           Functions to View Phones/Streets         #
# ================================================== #

def find_phone(filename):
        for element in get_element(filename, tags="('node')"):
            for child in element: 
                if child.attrib['k'] == "phone":
                    print(child.attrib['v'])
                    cleaned = cleanphone(child.attrib['v'])
                    print(cleaned)


def cleanphone(phone):
    
    numeric_string = re.sub("[^0-9]", "", phone)
    if numeric_string[0] == '1':
        numeric_string = numeric_string.replace('1', '', 1)
    formatted_phone = numeric_string[0:3] + '-' + numeric_string[3:6] +  '-' + numeric_string[6:]

    
    return(formatted_phone)
    
def find_street(filename):
    for element in get_element(filename, tags=('node')):
        for child in element:
            if child.attrib['k'] == "addr:street":
                get_abbr(child.attrib['v'], mapping)
                
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
mapping = { "st": "Street",
            "St.": "Street", 
            "Ave": "Avenue",
            "Rd": "Road",
            "Ln": "Lane",
            "Dr.": "Drive",
            "Pkwy": "Parkway",
            "Cir": "Circle",
            "Dr": "Drive",
            "N" : "North",
            "S": "South",
            "E": "East",
            "W": "West"
            }


def get_abbr(name, mapping):

    m = street_type_re.search(name)
    street_type = m.group()
    if street_type in mapping:
        print name