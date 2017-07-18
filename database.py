import csv
import sqlite3

con = sqlite3.Connection('names.sqlite')
cur = con.cursor()

table_names = ['Villages', 'Cities', 'States', 'Districts', 'Mandals']
file_names = ['villages', 'cities', 'states_uts', 'districts', 'mandals']
for i in range(5):
    cur.execute('CREATE TABLE ' + table_names[i] + ' (name varchar(225));')

    csv_file = open('resources/' + file_names[i] + '.csv')
    csv_reader = csv.reader(csv_file, delimiter=' ')

    cur.executemany('INSERT INTO ' + table_names[i] + ' VALUES (?)', csv_reader)

cur.close()
con.commit()
con.close()
