import toCSV
import audit
import toSQL
import sqlQueries
FILE = "jackson_ms.osm"
# Master Script that runs all cleaning and auditing scripts

# counts keys
audit.count_keys(FILE)

# counts unique users
audit.count_users(FILE)

# counts tags
audit.count_tags(FILE)

# processes data and converts to CSVs
toCSV.process_map(FILE, validate=True)

# Creates database and Inserts CSVs
toSQL.toSQL()


sqlQueries.query_data()