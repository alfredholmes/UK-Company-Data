import sys
import ijson, csv, json, datetime

from scipy.stats import lognorm

import numpy as np

sys.path.append('../lib')

from accounts.company import Company

def main():


	enterprises = get_enterprises()

	print('sorting companies')
	enterprises = sort_enterprises(enterprises, 2014)
	print('done')

	#parameters calculated for national size dist as in lognormal parameter fitting
	print('calculating sizes')
	mean = 0.20971199
	sd = 2.09891958
	
	sizes = sorted(lognorm.rvs(sd, scale=np.exp(mean), size=len(enterprises)))
	print('done')


	with open('2014_enterprise_sizes.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for i in range(len(enterprises)):
			writer.writerow([json.dumps(enterprises[i]['address']), sizes[i]])


def get_enterprises(year=None):
	print('loading enterprises')
	enterprises = []
	i = 0
	with open('enterprises.json', 'r') as file:
		try:
			for c in ijson.items(file, 'item'):
				if i % 10000 == 0:
					print('\t', i)
				i += 1
				if year is not None:
					if not enterprise_alive_in_year(enterprise, year):
						continue
				enterprises.append(c)
		except:
			pass
	print('\t done')
	return enterprises


def sort_enterprises(enterprises, year):
	print('sorting enterprises')
	date_string = datetime.datetime(year, 1, 1).strftime('%Y-%m-%d')
	return sorted(enterprises, key=lambda c: c['assets'][date_string])


def enterprise_alive_in_year(enterprise, year):
	date = datetime.datetime(year, 1, 1)
	return (date - datetime.datetime.strptime(enterprise['birth_date'], '%Y-%m-%d')).days >= 0 and (enterprise['death_date'] is None or (date - datetime.datetime.strptime(enterprise['death_date'])).days > 0)

	



if __name__ == '__main__':
	main()