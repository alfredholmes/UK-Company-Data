import sys, csv
from scipy.optimize import minimize, Bounds
from scipy.stats import norm, lognorm
import numpy as np

import matplotlib.pyplot as plt

import calculate_parameters

def main(files):
    files = [files[i:i+2] for i in range(int(len(files) / 2))] # TODO: need to make this neater, the script takes two inputs
    with open('2014_output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for file in files:
            dist_data = calculate_parameters.read_file(file[0])
            employment = get_employment(file[1])
            ratios = {}
            for key, size_dist in dist_data.items():
                #print(size_dist)
                total = np.sum([n for n in size_dist.values()])
                if key not in employment:
                    print(key + ' missing', total)
                    continue
                params = calculate_parameters.max_likelihood(size_dist, employment[key] / total)
                #params = calculate_parameters.max_likelihood(size_dist)
                if params is None:
                    continue
                mean, sd = params
                expected = expected_bands(mean, sd, [bands for bands in size_dist])
                
                writer.writerow([key, mean, sd])
                for size_band, n in size_dist.items():
                    if size_band in ratios:
                        ratios[size_band]['x'].append(n / total)
                        ratios[size_band]['y'].append(expected[size_band])

                    else:
                        ratios[size_band] = {'x': [n / total], 'y': [expected[size_band]]}
            
            

            plt.figure(0)
            plt.loglog()
            ax = plt.gca()
            ax.set_xlim([10**-4, 10**0])
            ax.set_ylim([10**-4, 10**0])
            for band, data in ratios.items():
                plt.scatter(data['x'], data['y'], label=band)
            plt.legend()

            plt.plot([0, 1], [0, 1])
            plt.xlabel('Actual proportion')
            plt.ylabel('Predicted proportion')
            plt.savefig('graphs/' + file[0][:-4] + '.png')
            plt.show()




def expected_bands(mean, sd, size_bands):
    sizes = {}
    for size_band in size_bands:
        if '-' in size_band:
            upper = int(size_band.split('-')[1]) + 1
            lower = int(size_band.split('-')[0])
        else:
            upper = np.inf
            lower = int(size_band[:-1])

        sizes[size_band] = lognorm.cdf(upper,s=sd,scale=np.exp(mean)) - lognorm.cdf(lower, s=sd, scale=np.exp(mean))

    return sizes

def get_employment(file):
    with open(file, 'r') as f:
        employment = {}
        reader = csv.reader(f)
        for line in reader:
            if line[0] != '':
                employment[line[0]] = float(line[1]) * 1000

        return employment



if __name__ == '__main__':
    files = sys.argv[1:]
    main(files)
