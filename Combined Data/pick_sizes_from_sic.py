import sys
import ijson, csv, json, datetime

from scipy.stats import lognorm

import numpy as np

import matplotlib.pyplot as plt

sys.path.append('../lib')

from accounts.company import Company

def main():


	enterprises = get_enterprises(2014)
	distribution_parameters = get_sic_params()
	actual_size_dists = get_la_data()

	print('sorting companies')
	enterprises_by_sic = sort_enterprises(enterprises, 2014)
	print('done')

	#parameters calculated for national size dist as in lognormal parameter fitting

	for sic, enterprises in enterprises_by_sic.items():
		if sic is None:
			continue
		if sic not in distribution_parameters:
			print(sic  + ' missing', len(enterprises))
			continue
		
		
		mean = distribution_parameters[sic]['mean']
		sd = distribution_parameters[sic]['sd']
		
		sizes = sorted(lognorm.rvs(sd, scale=np.exp(mean), size=len(enterprises)))
		for i, s in enumerate(sizes):
			enterprises[i]['size'] = int(round(float(s)))
	print('writing to file')
	
	with open('enterprises_with_size_from_sic.json', 'w') as f:
		json.dump(enterprises_by_sic, f, indent=4)

	top_bands = [5, 10, 20, 50, 100, 250, np.inf]
	bands = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']
	reconstructed = {} 		

	las = set()

	for sic, enterprises in enterprises_by_sic.items():
		for enterprise in enterprises:
			la = Company(None, '2012-01-01', enterprise['address'], {}, {}).la(2014)

			las.add(la)

			if la not in reconstructed:
				reconstructed[la] = {b: 0 for b in bands}
			
			
			for i, upper in enumerate(top_bands):
				if enterprise['size'] < upper:
					band = bands[i]
					break

			reconstructed[la][band] += 1

		
	la_to_plot = las.intersection(set(actual_size_dists.keys()))



	for b in bands:
		x = []
		y = []
		for la in la_to_plot:
			x.append(actual_size_dists[la][b] / np.sum([z for z in actual_size_dists[la].values()]))
			y.append(reconstructed[la][b] / np.sum([z for z in reconstructed[la].values()]))

		plt.scatter(x, y, label=b)
	plt.loglog()
	plt.xlim([10**-4, 10**0])
	plt.ylim([10**-4, 10**0])
	plt.legend()
	plt.plot([0, 1], [0, 1])
	plt.xlabel('Actual proportion')
	plt.ylabel('Predicted Proportion')
	plt.savefig('2014_la_reconstruction.png')
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
			for key, value in c['assets'].items():
				c['assets'][key] = float(value)
			enterprises.append(c)
	print('\t done')
	return enterprises

def get_sic_params():
	with open('2014_SIC_params.csv', 'r') as csvfile:
		data = {}
		reader = csv.reader(csvfile)
		for line in reader:
			data[int(line[0])] = {'mean': float(line[1]), 'sd': float(line[2])}

	return data

def sort_enterprises(enterprises, year):
	enterprises_by_sic = {sic: [] for sic in get_sic_params()}
	print('splitting_by_la.csv')
	for enterprise in enterprises:
		sic = None
		for s in enterprise['sic_codes']:
			if int(str(s)[:2]) in enterprises_by_sic:
				sic = int(str(s)[:2])
				break
		if sic is None:
			continue
		
		enterprises_by_sic[sic].append(enterprise)
		
	print('sorting enterprises')

	date_string = datetime.datetime(year, 1, 1).strftime('%Y-%m-%d')
		
	return {sic: sorted(enterprises, key=lambda c: c['assets'][date_string]) for sic, enterprises in enterprises_by_sic.items()}


def enterprise_alive_in_year(enterprise, year):
	date = datetime.datetime(year, 1, 1)
	return (date - datetime.datetime.strptime(enterprise['birth_date'], '%Y-%m-%d')).days >= 0 and ('death_date' not in enterprise or (date - datetime.datetime.strptime(enterprise['death_date'])).days > 0)

	
def get_la_data():
	size_bands = {}
	with open('2014_enterprise_size_by_la.csv', 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for line in reader:
			size_bands[line['la']] = {s: float(v) for s, v in line.items() if '-' in s or '+' in s }


	return size_bands


if __name__ == '__main__':
	main()
