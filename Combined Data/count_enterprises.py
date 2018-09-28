import json

import pick_sizes_from_la

import matplotlib.pyplot as plt

def main():

	years = [2012, 2013, 2014, 2016, 2017]

	ons_enterprises = [2081695, 2167580, 2249415, 2554510, 2598095]

	ch_enterprises = []

	for year in years:
		print(year)
		n_enterprises = len(pick_sizes_from_la.get_enterprises(year))
		ch_enterprises.append(n_enterprises)


	plt.plot(years, ch_enterprises)
	plt.plot(years, ons_enterprises)
	
	plt.ylabel('Number of Enterprises')
	plt.savefig('ch_enterprises_one_enterprises_comparison.png')
	plt.show()

if __name__ == '__main__':
	main()