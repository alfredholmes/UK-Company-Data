import sys
import ijson, csv, json

from scipy.stats import lognorm

import numpy as np

sys.path.append('../lib')

from accounts.company import Company 

def main():


	companies = get_companies()

	print('sorting companies')
	companies = sort_companies(companies, 2014)
	print('done')

	#parameters calculated for national size dist as in lognormal parameter fitting
	print('calculating sizes')
	mean = 0.55490127
	sd = 1.46275809
	
	sizes = sorted(lognorm.rvs(sd, scale=np.exp(mean), size=len(companies)))
	print('done')


	with open('2014_sizes.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for i in range(len(companies)):
			writer.writerow([companies[i].company_number, sizes[i]])


def get_companies():
	print('loading companies')
	companies = []
	i = 0
	with open('combined_data.json', 'r') as file:
		for c in ijson.items(file, 'item'):
			if i % 10000 == 0:
				print('\t', i)
			i += 1
			if 'death_date' not in c:
				companies.append(Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts']))
			else:
				companies.append(Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts'], c['death_date']))
	print('\t done')
	return companies


def sort_companies(companies, year):
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
	print('\t' + 'Filtering companies')
	companies = [c for c in companies if c.alive_in_year(2014)]
	print('\t' + 'done')
	print('\t' + 'sorting return')
	return sorted(companies, key=lambda c: c.get_account_size(2014))	

	



if __name__ == '__main__':
	main()