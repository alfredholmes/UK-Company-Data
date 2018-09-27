import sys
import ijson, csv, json, datetime

from scipy.stats import lognorm

import numpy as np

import matplotlib.pyplot as plt

sys.path.append('../lib')

from accounts.company import Company

def main():


	enterprises = get_enterprises(2014)
	distribution_parameters = get_la_params()
	actual_size_dists = get_sic_data()

	print('sorting companies')
	enterprises_by_la = sort_enterprises(enterprises, 2014)
	print('done')

	#parameters calculated for national size dist as in lognormal parameter fitting

	for la, enterprises in enterprises_by_la.items():
		if la is None:
			continue
		print(la)
		if la not in distribution_parameters:
			print(la  + ' missing', len(enterprises))
			continue
		print(la, len(enterprises))
		
		mean = distribution_parameters[la]['mean']
		sd = distribution_parameters[la]['sd']
		
		sizes = sorted(lognorm.rvs(sd, scale=np.exp(mean), size=len(enterprises)))
		for i, s in enumerate(sizes):
			enterprises[i]['size'] = int(round(float(s)))

		print('done')
	top_bands = [5, 10, 20, 50, 100, 250, 500, np.inf]
	bands = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250499', '500+']
	reconstructed = {} 		

	sic_codes = set()

	for la, enterprises in enterprises_by_la.items():
		for enterprise in enterprises:
			for sic_code in enterprise['sic_codes']:
				try:
					if int(str(sic_code)[:2]) != '99' and int(str(sic_codes)[:2]) in actual_size_dists:
						sic = int(sic_code[:2])
						break	
				except:
					continue

			else:
				continue

			if sic not in reconstructed:
				reconstructed[sic] = {s: 0 for s in bands}

			
			for i, upper in enumerate.top_bands():
				if enterprise['size'] < upper:
					band = bands[i]
					break

			sic_codes.add(sic)

			reconstructed[sic][band] += 1

		
	sic_codes_to_plot = sic_codes.intersection(set(actual_size_dists.keys()))

			

	for b in bands:
		x = []
		y = []
		for sic in sic_codes_to_plot:
			x.append(actual_size_dists[sic][b] / np.sum([x for x in actual_size_dists[sic].values()]))
			y.append(reconstructed[sic][b] / np.sum([x for x in reconstructed[sic].values()]))

		plt.scatter(x, y, label=b)

	plt.savefig('2014_sic_reconstruction.png')
	plt.show()









def get_enterprises(year=None):
	print('loading enterprises')
	enterprises = []
	i = 0
	with open('enterprises.json', 'r') as file:
		
		for c in ijson.items(file, 'item'):
			if i % 10000 == 0:
				print('\t', i)
			i += 1
			if year is not None:
				if not enterprise_alive_in_year(c, year):
					continue
			enterprises.append(c)
	print('\t done')
	return enterprises

def get_la_params():
	with open('2014_local_authority_log_normal_parameters.csv', 'r') as csvfile:
		data = {}
		reader = csv.reader(csvfile)
		for line in reader:
			data[line[0]] = {'mean': float(line[1]), 'sd': float(line[2])}

	return data

def sort_enterprises(enterprises, year):
	enterprises_by_la = {la: [] for la in get_la_params()}
	print('splitting_by_la.csv')
	for enterprise in enterprises:
		la = Company(None, '2012-01-01', enterprise['address'], {}, {}).la(2014)
		if la in enterprises_by_la:
			enterprises_by_la[la].append(enterprise)
		else:
			enterprises_by_la[la] = [enterprise]

	print('sorting enterprises')

	date_string = datetime.datetime(year, 1, 1).strftime('%Y-%m-%d')
		
	return {la: sorted(enterprises, key=lambda c: c['assets'][date_string]) for la, enterprises in enterprises_by_la.items()}


def enterprise_alive_in_year(enterprise, year):
	date = datetime.datetime(year, 1, 1)
	return (date - datetime.datetime.strptime(enterprise['birth_date'], '%Y-%m-%d')).days >= 0 and ('death_date' not in enterprise or (date - datetime.datetime.strptime(enterprise['death_date'])).days > 0)

	
def get_sic_data():
	size_bands = {}
	with open('2014_enterprise_size_by_sic.csv', 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for line in reader:
			size_bands[int(line['SIC'])] = {s: float(v) for s, v in line.items() if '-' in s or '+' in s }


	return size_bands


if __name__ == '__main__':
	main()