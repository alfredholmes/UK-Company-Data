import ijson, csv


def main():
	addresses = {}
	print('loading addresses')
	with open('combined_data.json', 'r') as f:
		for i, x in enumerate(ijson.items(f, 'item')):
			if i % 10000 == 0:
				print(i)
			address = frozenset(x['address'].values())
			if address in addresses:
				addresses[address].append(x['company_number'])
			else:
				addresses[address] = [x['company_number']]
	print('loading companies')
	company_sizes = {}
	with open('2014_sizes.csv') as csvfile:
		reader = csv.reader(csvfile)
		for line in reader:
			company_sizes[line[0]] = int(round(float(line[1])))

	print('combining addresses and company sizes')
	sizes = {}
	i = 0
	for address, companies in addresses.items():
		i += 1
		if i % 10000 == 0:
			print(i)
		size = 0
		for company in companies:
			if company in company_sizes:
				size += company_sizes[company]
		sizes[company] = size

	with open('2014_sizes_no_repeated_addresses.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for company, size in sizes.items():
			writer.writerow([company, size])


if __name__ == '__main__':
	main()