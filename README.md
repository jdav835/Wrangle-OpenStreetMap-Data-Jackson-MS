# Wrangle OpenStreetMap Data Project
### By Jennifer Davis

## Map Area
Jackson, MS, United States and surrounding area

![mapImage](https://github.com/jdav835/Wrangle-OpenStreetMap-Data-Jackson-MS/blob/main/SupportingImages/mapImage.PNG)


  - The osm can be generated by the following query on http://overpass-api.de/query_form.html
  ```
  (
  node(32.2761, -90.5016, 32.5663, -89.8749);
  <;
  );
  out meta;
  ```

  This area is of interest to me because it is where I spent the bulk of my childhood. 

  ## Problems Encountered in Map


  After taking a look at the data, I found a few problems:
  - Inconsistent phone number formatting (eg. '+1 601-321-9100', '601.856.0049', '601-992-2490', etc.)
  - Overabbreviated street names (eg. 'Pkwy', 'Rd', 'Ave', etc.)
 
### Inconsistent Phone Number Formatting
  After some simple queries, it was clear that the phone numbers were stored in many different formats.

  ![SamplePhones](https://github.com/jdav835/Wrangle-OpenStreetMap-Data-Jackson-MS/blob/main/SupportingImages/SamplePhones.PNG)

   In order to clean these up, checked for the key attribute 'phone' when converting data into 
  CSV format. 
  ```python
  elif node_tag['key'] == 'phone':
                    value = clean_phone(child.attrib['v'])
                    node_tag['value'] = value
  ```
  I then passed the phone number into a function which first removes all non-numeric 
  characters, then removes the leading 1 if it exists, and finally inserts dashes appropriately into
  the string to create a number in the format ###-###-####. 
  ```python
  def clean_phone(phone):
    # strips all non-numeric chararacters from string
    numeric_string = re.sub("[^0-9]", "", phone)
    # remove leading 1 if exists
    if numeric_string[0] == '1':
        numeric_string = numeric_string.replace('1', '', 1)
    # seperate phone number by dashes: ###-###-####
    formatted_phone = numeric_string[0:3] + '-' + numeric_string[3:6] +  '-' + numeric_string[6:]

    return(formatted_phone)
```

### Over Abbreviated Street Names
The next thing I noticed was the inconsistently/overabbreviated street names. While most were written out
as "Street", "Drive", etc., many were abbreviated to "St.", "Dr", etc. 

![sampleStreetAbr](https://github.com/jdav835/Wrangle-OpenStreetMap-Data-Jackson-MS/blob/main/SupportingImages/sampleStreetAbr.PNG)

In order to make these more consistent, I first printed all of the street endings by using the regex `street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)`
I placed all abbreviations that needed expanding into a mapping:
```python
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
```
Then while cleaning and formatting the data for CSVs, I checked each tag for a street name `if is_street_name(child):` by 
utilizing this function:
```python
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
```
If a street name was found, I called `value = update_name(child.attrib['v'], mapping)` and set `way_tag['value'] = value`
 In update_name() I mapped the targeted abbreviations to their full words: 
 ```python
 def update_name(name, mapping):
    m = street_type_re.search(name)
    street_type = m.group()
    if street_type in mapping:
       better_name = name.replace(street_type, mapping[street_type])
       return better_name
    else:
        return name
```
This function returns the better name if the ending is found in 'mapping', but
does not change the name if it is not found.

## Overview of Dataset

### Size of files
The osm file used for this project is 53,385kb. 

After running toCSV.py, the following files were created:

![new_files](https://github.com/jdav835/Wrangle-OpenStreetMap-Data-Jackson-MS/blob/main/SupportingImages/new_files.PNG)

### Number of unique users
By executing the query 
```python
    query = ("SELECT COUNT (DISTINCT uid) "  
            "FROM "
            "( SELECT uid FROM ways "
            "UNION ALL "
            "SELECT uid FROM nodes) a;"
            )
    cur.execute(query)
    results = cur.fetchone()
```
I learned that 627 unique users contributed to this map. 

### Most and Least contributing users

I found the large amount of contributing users interesting, so I decided to take a closer look at the 5 users that contributed the most and the number of users who only contributed once. 

Executing the query 

```python 
query = ("SELECT a.user, COUNT (*) as contributions "  
            "FROM "
            "( SELECT user FROM ways "
            "UNION ALL "
            "SELECT user FROM nodes) a "
            "GROUP BY a.user "
            "ORDER BY contributions DESC "
            "LIMIT 5;"
            )
    cur.execute(query)
    results = cur.fetchall()
```

Gave the 5 users that contributed the most: 
   - ELadner: 42,627
   - woodpeck_fixbot: 26,019
   - ediyes: 20490
   - Glen: 18732
   - Lance Cooper 12,694

And executing the query 
```python
    # count users who contributed once
    query = ("SELECT COUNT (*) "
            "FROM "
            "( SELECT a.user, COUNT (*) as contributions "  
            "FROM "
            "( SELECT user FROM ways "
            "UNION ALL "
            "SELECT user FROM nodes) a "
            "GROUP BY a.user "
            "HAVING contributions = 1 ) b; "
            )
    cur.execute(query)
    results = cur.fetchall()
    print "Bottom contributing users: ", results
```

Showed that there were 66 users who only contributed one time.

### Number of nodes and ways

By executing the queries 
```python
    query = ("SELECT COUNT (DISTINCT id) "  
            "FROM nodes"
            )
    cur.execute(query)
    results = cur.fetchone()
```
and
```python
    query = ("SELECT COUNT (DISTINCT id) "  
            "FROM ways"
            )
    cur.execute(query)
    results = cur.fetchone()
```
I learned that there are 239,317 nodes and 25,420 ways in this dataset.

### Number of drive-throughs

By executing the query 
```python
    query = ("SELECT COUNT (DISTINCT id) "  
            "FROM "
            "( SELECT id FROM ways_tags "
            "WHERE key = 'drive_through' "
            "AND value = 'yes' "
            "UNION ALL "
            "SELECT id FROM nodes_tags "
            "WHERE key = 'drive_through' "
            "AND value = 'yes') a;"
            )
    cur.execute(query)
    results = cur.fetchone()
```
I learned that there are 30 drive throughs represented in this dataset. This is interesting, because I would expect a much higher number in an area this large. I believe this to be an example of an incomplete dataset. Because OpenStreetMap is entirely user-created, the data is not a complete representation of everything available in the region. 

## Additional Thoughts on Dataset

The biggest issues that have not been accounted for when exploring the data were inconsistency of formatting and duplication. 

For instance, when performing queries on the ways_tags, it became apparent that many streets are duplicated. I performed the following query to see just how many were duplicated: 

```python 
    query = ("SELECT a.value, a.counted "
            "FROM "
            "(SELECT value, COUNT(value) as counted "
            "FROM ways_tags "
            "GROUP BY value "            
            "HAVING key = 'street' "
            "ORDER BY counted ASC ) a "
            "WHERE a.counted > 1 ;"
            )
    cur.execute(query)
```
This gave the results: 
![duplicatedStreets](https://github.com/jdav835/Wrangle-OpenStreetMap-Data-Jackson-MS/blob/main/SupportingImages/duplicatedStreets.PNG)

Which shows that Natchez Trace Parkway is listed a shocking 91 times. 

Throughout the other queries performed in this report, I saw many places with inconsistently formatted data - specifically phone numbers and street names. These inconsistencies continue throughout the data set. 

The best way to solve both of these problems would be to do more input validation when users upload more data. Input could be through a form that gives drop down boxes to choose existing keys like "phone" and "addr:street" that would then check the text box for the corresponding format. Street types could be left off and chosen from a drop down box. This validation would also check the input against the dataset to ensure no duplication occurs. 

I foresee two main issues with this solution. The first is resources. It would take a lot of work and time in order to create and maintain an input validation system. The second is outliers. It would be exceedingly tedious and difficult to include every possible street type in existence. While coming up with the most common is simple, such as found in 'mapping', there will always be outliers that would need to be accounted for. Additionally, determining whether a duplication is in fact duplication or simply a separate street with the same name would also be incredibly difficult given the commonality of so many street names. 

All things considered, OpenStreetMap is an amazing source of user-created map data that allows you to view some interesting information and statistics about different regions. 
