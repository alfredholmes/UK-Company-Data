import json

import matplotlib.pyplot as plt


def main():
    data = {'assets': [], 'netassets': []}
    print('Loading accounts...')
    accounts = load_accounts()
    print('done')
    h, i, j = 0, 0, 0
    for file in accounts:
        j += 1
        if 'currentassets' in file['accounts']:
            data['assets'].append(float(file['accounts']['currentassets'][0][1]))
        if 'netcurrentassetsliabilities' in file['accounts']:
            data['netassets'].append(float(file['accounts']['netcurrentassetsliabilities'][0][1]))


    plt.figure(0)
    plt.hist(data['assets'], 500, range=[0, 10**6], density=True)
    plt.show()

def load_accounts():
    with open('../../Datasets/Accounts/2011_accounts.json') as file:
        accounts = json.load(file)

    return accounts

if __name__ == '__main__':
    main()
