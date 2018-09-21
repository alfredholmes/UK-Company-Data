import sys
import ijson, csv

from scipy.stats import lognorm

import numpy as np

sys.path.append('../lib')

from accounts.company import Company 

def main():


	companies = get_companies()

	print('sorting companies')
	companies = order_companies(companies, 2014)
	print('done')

	#parameters calculated for national size dist as in lognormal parameter fitting
	print('calculating sizes')
	mean = 0.42316817
	sd = 1.67381106
	sizes = sorted(lognorm.rvs(sd, scale=np.exp(mean), size=len(companies)))
	print('done')


	with open('2014_sizes.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for i in range(len(companies)):
			writer.writerow([companies[i], sizes[i]])


def get_companies():
	print('loading companies')
	companies = []
	i = 0
	with open('combined_data.json', 'r') as file:
		for c in ijson.items(file, 'item'):
			if i % 10000 == 0:
				print(i)
				if i > 90000:
					break
			i += 1
			if 'death_date' not in c:
				companies.append(Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts']))
			else:
				companies.append(Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts'], c['death_date']))
	print('done')
	return companies


def order_companies(companies, year):
	""" Sorts array of companies, by assets
	
	Arguments:
	---------------
		companies: array of companies
		year: year in which companies are sorted
	
	Returns:
	---------------
		array of companies in order
	"""
	year = str(year)
	#build company dict
	sizes = {}
	for company in companies:
		if 'assets' not in company.accounts:
			continue
		if not company.alive_in_year(year):
			continue
		for date, size in company.accounts['assets'].items():
			if year in date:
				sizes[company.company_number] = size
				break
		else:
			sizes[company.company_number] = 0

	sorted_sizes = sorted(sizes.values())

	#generate sorted list of company ids

	sorted_ids = []

	for size in sorted_sizes:
		sorted_ids += [c for c, s in sizes.items() if s == size]

	return sorted_ids
	



if __name__ == '__main__':
	main()