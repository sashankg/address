import csv
import sqlite3
from metaphone import doublemetaphone

class Row:
	def __init__(self, csv_reader):
		self.csv_reader = csv_reader
	def __iter__(self):
		return self
	def next(self):
		name = self.csv_reader.next()[0]
		metaphones = doublemetaphone(name)	
		return [name.upper(), metaphones[0], metaphones[1]]

con = sqlite3.Connection('names.sqlite')
cur = con.cursor()

table_names = ['Villages', 'Cities', 'States', 'Districts', 'Mandals']
file_names = ['villages', 'cities', 'states_uts', 'districts', 'mandals']
for i in range(5):
    cur.execute('DROP TABLE IF EXISTS ' + table_names[i])
    cur.execute('CREATE TABLE ' + table_names[i] + ' (name text, metaphone1 text, metaphone2 text);')

    csv_file = open('resources/' + file_names[i] + '.csv')
    csv_reader = csv.reader(csv_file, delimiter=' ')

    cur.executemany('INSERT INTO ' + table_names[i] + ' VALUES (?, ?, ?)', Row(csv_reader))

cur.close()
con.commit()
con.close()
