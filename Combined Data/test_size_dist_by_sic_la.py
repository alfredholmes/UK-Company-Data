import csv, ijson, numpy as np, json, datetime

import employment_prediction

import sys

sys.path.append('../lib')

from accounts.company import Company

def main():
	
	sizes = get_company_sizes()

	size_bands = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']
	size_upper = [5, 10, 20, 50, 100, 250, np.inf]

	size_by_la  = {}
	#size_by_sic = {}

	


	for enterprise, size in sizes.items():
		size = int(round(float(size)))
		la = Company(None, '2012-01-01', json.loads(enterprise), {}, {}).la(2014)
		#sic = company.sic_codes
		if la not in size_by_la:
			size_by_la[la] = {s: 0 for s in size_bands}

		for i, s in enumerate(size_upper):
			if size < s:
				size_band = size_bands[i]
				break
		else:
			size_band = size_bands[0] 

		size_by_la[la][size_band] += 1


	with open('predicted_la_size_bands.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, ['la'] + size_bands)
		for la, size_dist in size_by_la.items():
			size_dist['la'] = la
			writer.writerow(size_dist)




def get_company_sizes():
	sizes = {}
	with open('2014_enterprise_sizes.csv', 'r') as csvfile:
		reader = csv.reader(csvfile)
		for line in reader:
			sizes[line[0]] = int(round(float(line[1])))
	return sizes



if __name__ == '__main__':
	main()