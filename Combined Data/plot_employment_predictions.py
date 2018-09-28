import csv

import matplotlib.pyplot as plt

def main():
	size_bands = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']

	observed = read_csv('2014_enterprise_size_by_la.csv')
	predicted = read_csv('predicted_la_size_bands.csv')


	actual_totals = {}
	predicted_totals = {}


	las = set(predicted.keys()).intersection(set(observed.keys()))

	for la in las:
		actual_total = 0
		predicted_total = 0
		for s in size_bands:
			actual_total += observed[la][s]
			predicted_total += predicted[la][s]

		actual_totals[la] = actual_total
		predicted_totals[la] = predicted_total
	

	
	observed_lists = {s: [] for s in size_bands}
	predicted_lists = {s: [] for s in size_bands}

	for la in las:

		for s in size_bands:
			observed_lists[s].append(observed[la][s] / actual_totals[la])
			predicted_lists[s].append(predicted[la][s] / predicted_totals[la]) 	
			#observed_lists[s].append(observed[la][s])
			#predicted_lists[s].append(predicted[la][s]) 	


	plt.loglog()
	ax = plt.gca()
	ax.set_xlim([10**-3.2, 10**0])
	ax.set_ylim([10**-3.2, 10**0])
	for s in size_bands:

		plt.scatter(observed_lists[s], predicted_lists[s], label=s)
	plt.plot([0] + observed_lists['0-4'], [0] + observed_lists['0-4'])
	plt.legend()
	plt.xlabel('Predicted Proportion')
	plt.ylabel('Actual Proportion')
	plt.savefig('national_distribution_employment_reconstuction.png')
	plt.show()


def read_csv(file):
	size_bands = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']
	data = {}
	with open(file, 'r') as csvfile:
		reader = csv.reader(csvfile)
		for line in reader:
			data[line[0]] = {s: float(line[i + 1]) for i, s in enumerate(size_bands)}

	return data
if __name__ == '__main__':
	main()
