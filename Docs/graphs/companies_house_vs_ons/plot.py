import matplotlib.pyplot as plt


def main():
	years = [2012, 2013, 2014, 2016, 2017]
	#companies_house_companies = [2995776, 3224648, 3419079, 3782463, 3983372]
	companies_house_no_repeated_address = [1631977, 1774548, 1919786, 2011493, 2299449]
	ons_companies = [2081695, 2167580, 2249415, 2554510, 2598095]

	plt.plot(years, companies_house_no_repeated_address, label='Companies House address sets')
	plt.plot(years, ons_companies, label='ONS Companies')
	plt.legend()
	plt.ylabel('Number of Companies / Enterprises')
	plt.savefig('companies_house_vs_ons_no_repeats.png')
	plt.show()

if __name__ == '__main__':
	main()
