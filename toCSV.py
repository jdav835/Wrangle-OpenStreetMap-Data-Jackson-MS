#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Validates in 

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import sys
import cerberus

import schema

OSM_PATH = "interpreter.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# maps poor street names to corrected names
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


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

   
    if element.tag == 'node':
        for attrib in element.attrib:
           
            # fill in "node" field
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]
          
          
        # fill in node_tags
        for child in element:
            node_tag = {}
            #split at first colon
            
            if LOWER_COLON.match(child.attrib['k']):
                node_tag['id'] = element.attrib['id']
                split = child.attrib['k'].split(':', 1)
                node_tag['key'] = split[1]
                if is_street_name(child):
                    value = update_name(child.attrib['v'], mapping)
                    node_tag['value'] = value
                elif node_tag['key'] == 'phone':
                    value = clean_phone(child.attrib['v'])
                    node_tag['value'] = value
                else:
                    node_tag['value'] = child.attrib['v']
                node_tag['type'] = split[0]
             #ignore problemchars   
            elif PROBLEMCHARS.match(child.attrib['k']):
                continue
            
            else:
                node_tag['id'] = element.attrib['id']
                node_tag['key'] = child.attrib['k']
                if node_tag['key'] == 'phone':
                    
                    value = clean_phone(child.attrib['v'])
                 
                    node_tag['value'] = value
                else:
                    node_tag['value'] = child.attrib['v']
                
                node_tag['type'] = 'regular'
            tags.append
            (node_tag)
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        
        position = 0;     
        
        # fill in node_tags
        for child in element:
            way_tag = {}
            way_node = {}
            #split at first colon
            if child.tag == 'tag':
                if LOWER_COLON.match(child.attrib['k']):
                    way_tag['id'] = element.attrib['id']
                    split = child.attrib['k'].split(':', 1)
                    way_tag['key'] = split[1]
                    if is_street_name(child):
                        value = update_name(child.attrib['v'], mapping)
                        way_tag['value'] = value
                    elif way_tag['key'] == 'phone':
                        value = clean_phone(child.attrib['v'])
                        way_tag['value'] = value
                    else:   
                        way_tag['value'] = child.attrib['v']                    
                    way_tag['type'] = split[0]
             #ignore problemchars   
                elif PROBLEMCHARS.match(child.attrib['k']):
                    continue
            
                else:
                    way_tag['id'] = element.attrib['id']
                    way_tag['key'] = child.attrib['k']
                    if is_street_name(child):
                        value = update_name(child.attrib['v'], mapping)
                        way_tag['value'] = value
                    elif way_tag['key'] == 'phone':
                        value = clean_phone(child.attrib['v'])
                        way_tag['value'] = value
                    else:   
                        way_tag['value'] = child.attrib['v']  
                    
                    way_tag['type'] = 'regular'
                tags.append(way_tag)
            elif child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position +=1
                way_nodes.append(way_node)
                
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()
        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
           # print(el)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
    
def is_phone_number(elem):
    return (elem.attrib['k'] == "phone")
    
def update_name(name, mapping):
    m = street_type_re.search(name)
    street_type = m.group()
    if street_type in mapping:
       better_name = name.replace(street_type, mapping[street_type])
       return better_name
    else:
        return name

def clean_phone(phone):
    # strips all non-numeric chararacters from string
    numeric_string = re.sub("[^0-9]", "", phone)
    # remove leading 1 if exists
    if numeric_string[0] == '1':
        numeric_string = numeric_string.replace('1', '', 1)
    # seperate phone number by dashes: ###-###-####
    formatted_phone = numeric_string[0:3] + '-' + numeric_string[3:6] +  '-' + numeric_string[6:]

    return(formatted_phone)

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
    print(sys.version)
    print("me")
