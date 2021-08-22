import toCSV
import audit
import toSQL

FILE = "jackson_ms.osm"
# Master Script that runs all cleaning and auditing scripts

# counts keys
#audit.count_keys(FILE)

# counts unique users
#audit.count_users(FILE)

# counts tags
#audit.count_tags(FILE)

# processes data and converts to CSVs
toCSV.process_map(FILE, validate=False)

# Creates database and Inserts CSVs
#toSQL.toSQL()




#toSQL.query_data()

audit.find_phone(FILE)
#print(audit.cleanphone("601-256-8659"))
#print(audit.cleanphone("+1 601-807-4615"))