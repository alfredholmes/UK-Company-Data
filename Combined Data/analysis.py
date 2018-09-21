import json


def main():

	print('loading companies')
	companies = load_companies()
	print('done')

	print('Counting companies')
	years = range(2012, 2018)
	for year in years:
		total_companies = 0
		total_accounts = 0
		print(year)
		for company in companies:
			if int(company['birth_date'][:4]) <= year:
				total_companies += 1
				if 'assets' in company['accounts']:
					for key in  company['accounts']['assets']:
						if int(key[:4]) == year:
							total_accounts += 1

		print('\t', total_accounts, total_companies)

def load_companies():
	with open('combined_data.json', 'r') as file:
		companies = json.load(file)

	return companies

if __name__ == '__main__':
	main()
