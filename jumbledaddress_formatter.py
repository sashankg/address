import csv

unformatted_file = open('resources/jumbledaddress.csv')
csv_reader = csv.reader(unformatted_file, delimiter=' ')

formatted_file = open('resources/formatted_address.csv', 'w')
csv_writer = csv.writer(formatted_file, delimiter=' ')

for row in csv_reader:
	csv_writer.writerow([row[0].replace('!', ', ')])

unformatted_file.close()
formatted_file.close()
