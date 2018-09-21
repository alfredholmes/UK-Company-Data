import sys
import analysis

from scipy.stats import lognorm

sys.path.append('../lib')

from accounts.company import Company 

def main():
	print('loading companies')
	companies_from_file = analysis.load_companies()
	print('done')
	print('creating company objects')
	companies = [Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['accounts']) for c in companies_from_file]
	print('done')

	print('sorting companies')
	companies = order_companies(companies, 2014)
	print('done')


	with open('')



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