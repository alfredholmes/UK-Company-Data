import ijson, json

from accounts.company import Company

def main():
    print('Loading companies')
    companies = get_companies()
    print('Done')
    print('Loading Accounts:')
    accounts = get_accounts(companies)
    print('Done')

    with open('combined_data.json', 'w') as file:
        file.write('[\n')
        for i, company in enumerate(companies):
            file.write('    ')
            file.write(company.json())
            if i != len(companies) - 1:
                file.write(',\n')

        file.write('\n]')

def get_companies():
    companies = []
    i = 0

    with open('../Dataset/dataset.json', 'r') as file:
        json_objs = ijson.items(file, 'item')
        for company in json_objs:
            i += 1
            if i % 100000 == 0:
                print(i)
            
            if company['IncorporationDate'] == '':
                continue
            if company['LastActiveDate'] != '2017-02-03' and company['LastActiveDate'] != '':
                companies.append(Company(company['CompanyNumber'], company['IncorporationDate'], company['Address'], company['Status'], company['SICCodes'], company['LastActiveDate']))
            else:
                companies.append(Company(company['CompanyNumber'], company['IncorporationDate'], company['Address'], company['Status'], company['SICCodes']))
    return companies

def get_accounts(companies):
    print('Generating company dict')
    company_indices = {company.company_number: i for i, company in enumerate(companies)}
    print('Done')
    accounts = {}
    for i in range(2008, 2018):
        if i == 2013:
            continue
        print('\t' + str(i))
        with open('../../Datasets/Accounts/'+ str(i) + '_accounts.json') as accounts_json:
            objects = ijson.items(accounts_json, 'item')
            for o in objects:
                if o['company_number'] not in company_indices:
                    continue
                if 'currentassets' not in o['accounts']:
                    continue
                companies[company_indices[o['company_number']]].add_accounts({'assets': o['accounts']['currentassets']})



if __name__ == '__main__':
    main()
