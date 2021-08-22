# -*- coding: utf-8 -*-
import sqlite3
import csv
import pprint 

def toSQL():

    sql_file = 'jackson_ms.db'
    conn = sqlite3.connect(sql_file)
    conn.text_factory = str
    
    cur = conn.cursor()
    # ================================================== #
    #                   NODES Table                      #
    # ================================================== #
     # Drop nodes table if exists
    cur.execute("DROP TABLE IF EXISTS nodes;" );
    conn.commit()
    # create table nodes
    cur.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY NOT NULL,lat REAL,lon REAL,user TEXT,uid INTEGER,version INTEGER,changeset INTEGER,timestamp TEXT);")
 
    conn.commit()

    # Read formatted data from nodes.csv into table
    with open('nodes.csv','rb') as f: 
        dr = csv.DictReader(f)
        to_db = [(i['id'].decode("utf-8"),i['lat'].decode("utf-8"),i['lon'].decode("utf-8"),i['user'].decode("utf-8"),i['uid'].decode("utf-8"),i['version'].decode("utf-8"),i['changeset'].decode("utf-8"),i['timestamp'].decode("utf-8")) for i in dr]
        
    # insert the formatted data
    cur.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?,?,?,?,?,?,?,?);", to_db)
    conn.commit()
    f.close()

    # ================================================== #
    #               NODES_TAGS Table                     #
    # ================================================== #

    # Drop nodes_tags table if exists
    cur.execute("DROP TABLE IF EXISTS nodes_tags;")
    conn.commit()
    # create table nodes_tags
    cur.execute("CREATE TABLE nodes_tags (id INTEGER,key TEXT,value TEXT,type TEXT,FOREIGN KEY (id) REFERENCES nodes(id));")
    conn.commit()

    # Read formatted data from nodes_tags.csv into table
    with open('nodes_tags.csv','rb') as f: 
        dr = csv.DictReader(f)
        to_db = [(i['id'].decode("utf-8"),i['key'].encode("utf-8"),i['value'].decode("utf-8"),i['type'].decode("utf-8")) for i in dr]

    # insert the formatted data
    cur.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?,?,?,?);", to_db)
    conn.commit()
    f.close()

    # ================================================== #
    #                  WAYS Table                        #
    # ================================================== #

    #drop ways table if exists
    cur.execute("DROP TABLE IF EXISTS ways;");
    conn.commit()
    #create ways table
    cur.execute("CREATE TABLE ways(id INTEGER PRIMARY KEY NOT NULL,user TEXT,uid INTEGER,version TEXT,changeset INTEGER,timestamp TEXT);")
    conn.commit()

    # Read data from ways.csv into table
    with open('ways.csv','rb') as f: 
        dr = csv.DictReader(f)
        to_db = [(i['id'],i['user'].decode("utf-8"),i['uid'],i['version'],i['changeset'],i['timestamp']) for i in dr]

    # insert the formatted data      
    cur.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?,?,?,?,?,?);", to_db)
    conn.commit()
    f.close()

    # ================================================== #
    #                 WAYS_NODES Table                   #
    # ================================================== #

    #Drop ways_nodes table if exists
    cur.execute("DROP TABLE IF EXISTS ways_nodes;")
    conn.commit()
    # Create ways_nodes table
    cur.execute("CREATE TABLE ways_nodes (id INTEGER NOT NULL,node_id INTEGER NOT NULL,position INTEGER NOT NULL,FOREIGN KEY (id) REFERENCES ways(id),FOREIGN KEY (node_id) REFERENCES nodes(id));")
    conn.commit()

    # Read data from ways_nodes.csv into table
    with open('ways_nodes.csv','rb') as f: 
        dr = csv.DictReader(f)
        to_db = [(i['id'].decode("utf-8"),i['node_id'].decode("utf-8"),i['position'].decode("utf-8")) for i in dr]

        
    # insert the formatted data   
    cur.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?,?,?);", to_db)
    conn.commit()
    f.close()

    # ================================================== #
    #                WAYS_TAGS Table                     #
    # ================================================== #

    #Drops ways_tags table if exists
    query="DROP TABLE IF EXISTS ways_tags;"   
    cur.execute(query);
    conn.commit()
    #creates ways_tags table
    query = "CREATE TABLE ways_tags (id INTEGER NOT NULL,key TEXT NOT NULL,value TEXT NOT NULL,type TEXT,FOREIGN KEY (id) REFERENCES ways(id));"
    cur.execute(query)
    conn.commit()


    # Read data from ways_tags.csv into table
    with open('ways_tags.csv','rb') as f: 
        dr = csv.DictReader(f)
        to_db = [(i['id'].decode("utf-8"),i['key'].decode("utf-8"),i['value'].decode("utf-8"),i['type'].decode("utf-8")) for i in dr]

    # insert the formatted data 
    cur.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?,?,?,?);", to_db)
    conn.commit()
    f.close()


    '''
    #sample query
    query = "SELECT * FROM nodes LIMIT 10;"
    cur.execute(query)
    results = cur.fetchall()

    print(results)

    pprint.pprint(results)
    '''
    return

def query_data():
    
    #create database
    db = sqlite3.connect("jackson_ms.db")
    db.text_factory = str
    #get cursor
    cur = db.cursor()
    
    #sample query
    query = "SELECT * FROM nodes LIMIT 5;"
    cur.execute(query)
    results = cur.fetchall()


    pprint.pprint(results)
    return