import csv, ijson, numpy as np

import employment_prediction

def main():
	las = get_postcode_data()
	companies = employment_prediction.get_companies()
	sizes = get_company_sizes()

	size_bands = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']
	size_upper = [5, 10, 20, 50, 100, 250, np.inf]

	size_by_la  = {}
	#size_by_sic = {}


	for company in companies:
		if company.company_number not in sizes:
			continue

		la = las[company.postcode(2014)]
		#sic = company.sic_codes
		if la not in size_by_la:
			size_by_la[la] = {s: 0 for s in size_band}

		for i, s in enumerate(size_upper):
			if sizes[company.company_number] < s:
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








def get_postcode_data():
	las = {}
	with open('../data/postcode_la.csv', 'r') as csvfile:
		reader = csv.reader(csvfile)
		for line in reader:
			las[line[0]] = line[1]

	return las

def get_company_sizes():
	sizes = {}
	with open('2014_sizes.csv', 'r') as csvfile:
		reader = csv.reader(csvfile)
		for line in reader:
			sizes[line[0]] = line[1]
	return sizes

if __name__ == '__main__':
	main()