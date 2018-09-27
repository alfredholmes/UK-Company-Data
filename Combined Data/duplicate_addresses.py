import ijson, csv, json, datetime

import sys

sys.path.append('../lib')

from accounts.company import Company

def main():
	enterprises = {}
	print('loading enterprises')
	with open('combined_data.json', 'r') as f:
		for i, c in enumerate(ijson.items(f, 'item')):
			if i % 10000 == 0:
				print(i)
			address = frozenset(c['address'].values())
			if address in enterprises:
				enterprises[address].append(Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts']))
			else:
				enterprises[address] = [Company(c['company_number'], c['birth_date'], c['address'], c['status'], c['sic_codes'], c['accounts'])]
	

	print('writing enterprises')
	with open('enterprises.json', 'w') as f:
		f.write('[\n')

		asset_dates = [datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1), datetime.datetime(2014, 1, 1), datetime.datetime(2015, 1, 1), datetime.datetime(2016, 1, 1)]
		i= 0

		for address, enterprise in enterprises.items():
			if i % 10000 == 0:
				print(i)

			i += 1
			
			dead = True
			birth_date = None
			death_date = None	
			
			assets = {d: 0 for d in asset_dates}

			for company in enterprise:
				if company.death_date is None:
					dead = False
				else:
					if dead and (death_date is None or (company.death_date - death_date).days > 0):
						death_date = company.death_date

				if birth_date is None or (company.birth_date - birth_date).days < 0:
					birth_date = company.birth_date
				
				for date in asset_dates:
					assets[date] += company.asset_at_date('assets', date)

			enterprise_data = {'address': [a for a in address], 'birth_date': birth_date.strftime('%Y-%m-%d'), 'assets': {d.strftime('%Y-%m-%d'): v for d, v in assets.items()}}
			if death_date is not None:
				enterprise_data['death_date'] = death_date.strftime('%Y-%m-%d')



			f.write('    ')
			f.write(json.dumps(enterprise_data))
			f.write(',\n')
		f.write(']\n')




if __name__ == '__main__':
	main()