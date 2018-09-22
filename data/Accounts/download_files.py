""" Simple python script to download accounts data from companies house

    WARNING: The total size after the download will be about 300GB

"""

import wget, os



months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

files = {
            '2008': ['http://download.companieshouse.gov.uk/archive/Accounts_Monthly_Data-JanuaryToDecember2008.zip'],
            '2009': ['http://download.companieshouse.gov.uk/archive/Accounts_Monthly_Data-JanuaryToDecember2009.zip']
        }
for year in range(2010, 2016):
    files[str(year)] = ['http://download.companieshouse.gov.uk/archive/Accounts_Monthly_Data-' + month + str(year) + '.zip' for month in months]

files['2017'] = ['http://download.companieshouse.gov.uk/Accounts_Monthly_Data-' + month + '2017' + '.zip' for month in months]

for year, addresses in files.items():
    for address in addresses:
        if address.split('/')[-1] not in os.listdir(year):
            print('Downloading ' + address)
            wget.download(address, out=year + '/')
        else:
            print('Not downloading ' + address + ' since file exists')
