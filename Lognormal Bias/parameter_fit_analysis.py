import sys, csv
from scipy.optimize import minimize, Bounds
from scipy.stats import norm, lognorm
import numpy as np

import matplotlib.pyplot as plt

import calculate_parameters

def main(files):
    for file in files:
        dist_data = calculate_parameters.read_file(file)
        ratios = {}
        for key, size_dist in dist_data.items():
            params = calculate_parameters.max_likelihood(size_dist)
            if params is None:
                continue
            mean, sd = params
            total = np.sum([n for n in size_dist.values()])

            expected_biased = expected_bands(mean, sd, [bands for bands in size_dist])
            print(mean, sd)
            mean, sd = calculate_parameters.remove_bias(mean, sd)
            
            expected_unbiased = expected_bands(mean, sd, [bands for bands in size_dist])

            for size_band, n in size_dist.items():
                if size_band in ratios:
                    ratios[size_band]['x'].append(n / total)
                    ratios[size_band]['y'].append(expected_biased[size_band])
                    ratios[size_band]['z'].append(expected_unbiased[size_band])
                else:
                    ratios[size_band] = {'x': [n / total], 'y': [expected_biased[size_band]], 'z': [expected_unbiased[size_band]]}
        plt.figure(0)
        plt.loglog()
        for band, data in ratios.items():
            plt.scatter(data['x'], data['y'], label=band)
        plt.legend()

        plt.plot([0, 1], [0, 1])
        plt.savefig('graphs/' + file[:-4] + 'biased' + '.png')
        
        plt.figure(1)
        plt.loglog()
        for band, data in ratios.items():
            plt.scatter(data['x'], data['z'], label=band)
        plt.legend()

        plt.plot([0, 1], [0, 1])
        plt.savefig('graphs/' + file[:-4] + 'unbiased' + '.png')

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




if __name__ == '__main__':
    files = sys.argv[1:]
    main(files)
