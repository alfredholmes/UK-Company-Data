import json, matplotlib.pyplot as plt, sys, csv, numpy as np

sys.path.append('../lib')

from accounts.company import Company

def main():
	with open('enterprises_with_size_from_sic.json', 'r') as f:
		enterprises_by_sic = json.load(f)

	employment_by_la = {}

	print('calcuating employment')

	for enterprises in enterprises_by_sic.values():
		for enterprise in enterprises:
			la = Company(None, '2012-01-01', enterprise['address'], {}, {}).la(2014)
			if la in employment_by_la:
				employment_by_la[la] += enterprise['size']
			else:
				employment_by_la[la]  = enterprise['size']

	print('done')


	X = []
	Y = []


	largest_la = None
	largest_la_size = 0
	with open('2014_total_employment.csv', 'r') as csvfile:
		reader = csv.reader(csvfile)
		processed = set()
		for line in reader:
			
			if line[0] in processed:
				continue
			processed.add(line[0])
			if line[0] not in employment_by_la:
				print(line[0] + ' missing')
				continue

			if largest_la is None or employment_by_la[line[0]] > largest_la_size:
				largest_la = line[0]
				largest_la_size = employment_by_la[line[0]]

			X.append(float(line[2]) * 1000)
			Y.append(employment_by_la[line[0]])

	print(largest_la)

	X = np.array(X) / np.sum(X)
	Y = np.array(Y) / np.sum(Y)
	
	plt.scatter(X, Y)
	plt.xlabel('Actual employment proportion')
	plt.ylabel('Predicted employment proportion')
	plt.show()


if __name__ == '__main__':
	main()
