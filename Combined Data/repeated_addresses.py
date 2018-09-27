import sys, ijson, csv, datetime

sys.path.append('../lib')

from accounts.company import Company 

def main():
	enterprises = {} #dict of {address: companies}
	with open('combined_data.json', 'r') as f:
		for i, c in enumerate(ijson.items(f, 'item')):
			address = frozenset(c['address'].values())
			if 'death_date' not in c:
				company = Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts'])
			else:
				company = Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts'], c['death_date'])
			if address in enterprises:
				enterprises[address].append(company)
			else:
				enterprises[address] = [company]

			if i % 10000 == 0:
				print(i)
	
	totals = []
	for year in [2012, 2013, 2014, 2015, 2016, 2017]:
		total = 0
		for enterprise, companies in enterprises.items():
			if alive(companies, year):
				total += 1
		print(year, total)
		totals.append(total)

	with open('number_of_companies_no_repeated_addresse.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(totals)

def alive(companies, year):
	for c in companies:
		if c.alive_at_date(datetime.datetime(year, 8, 1)):
			return True
			break
	
	return False

if __name__ == '__main__':
	main()
