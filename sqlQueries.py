# -*- coding: utf-8 -*-
import sqlite3
import csv
import pprint 


def query_data():
    
    #create database
    db = sqlite3.connect("jackson_ms.db")
    db.text_factory = str
    #get cursor
    cur = db.cursor()
   
    # count distinct users
    query = ("SELECT COUNT (DISTINCT uid) "  
            "FROM "
            "( SELECT uid FROM ways "
            "UNION ALL "
            "SELECT uid FROM nodes) a;"
            )
    cur.execute(query)
    results = cur.fetchone()
    pprint.pprint( results)
    
    # print top 5 contributing users
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
    print "Top contributing users: ", results
    
    # print bottom 5 contributing users
    query = ("SELECT a.user, COUNT (*) as contributions "  
            "FROM "
            "( SELECT user FROM ways "
            "UNION ALL "
            "SELECT user FROM nodes) a "
            "GROUP BY a.user "
            "ORDER BY contributions ASC "
            "LIMIT 5;"
            )
    cur.execute(query)
    results = cur.fetchall()
    print "Bottom contributing users: ", results

    # print all one time contributing users
    query = ("SELECT a.user, COUNT (*) as contributions "  
            "FROM "
            "( SELECT user FROM ways "
            "UNION ALL "
            "SELECT user FROM nodes) a "
            "GROUP BY a.user "
            "HAVING contributions = 1 ; "
            )
    cur.execute(query)
    results = cur.fetchall()
    print "Bottom contributing users: ", results
    
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
        
    
    
    # count nodes
    query = ("SELECT COUNT (DISTINCT id) "  
            "FROM nodes;"
            )
    cur.execute(query)
    results = cur.fetchone()
    print "Number of nodes: ", results
    
     # count ways
    query = ("SELECT COUNT (DISTINCT id) "  
            "FROM ways;"
            )
    cur.execute(query)
    results = cur.fetchone()
    print "Number of ways: ", results
  
    
    # count drive throughs
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
    print "Number of drive throughs: ", results
  
    
    
    # display counts of streets greater than one
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
    results = cur.fetchall()
    pprint.pprint(results)
  
  
    return
    
    
    
    
    
    
    
    
    
    