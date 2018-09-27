"""Script that calculates the parameters for a log normal distribution given the input
To use: python calculate_parameters file1.csv file2.csv ... fileN.csv [optional output_dir=output]

The details of the calculations in this script are in the appendix of the docs.
"""

import sys, csv
from scipy.optimize import minimize, Bounds, NonlinearConstraint
from scipy.stats import norm, lognorm
import numpy as np

a_1, b_1, c_1, a_2, b_2, c_2, M = None, None, None, None, None, None, None

def main(files, output_dir):
    to_ignore = 0
    for file in files:
        company_sizes = read_file(file)
        parameters = {}
        options = []
        for key, size_dist in company_sizes.items():
            option_1 = max_likelihood(size_dist)
            option_2 = match_expectation(size_dist)
            options.append((option_1, option_2))

            if option_1 is not None:
                var = lognorm.var(option_1[1],scale=np.exp(option_1[0]))
            elif option_2 is not None:
                option_1 = option_2
                var = lognorm.var(option_2[1],scale=np.exp(option_2[0]))
            else:
                continue
            if option_1[0] == 0 and option_2[1] == 1:
                for n in size_dist.values():
                    to_ignore += n

                print('ignoring ' + key)
            else:
                parameters[key] = option_1
            #max_likelyhood(size_dist)

        with open(output_dir + file[:-4] + '_out.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            for key, params in parameters.items():
                writer.writerow([key, params[0], params[1]])

    print(to_ignore)

def remove_bias(mle_mean, mle_sd):
    global a_1, b_1, c_1, a_2, b_2, c_2, M
    if a_1 is None:
        with open('plane_params.csv') as csvfile:
            reader = csv.reader(csvfile)
            mean_params = [float(x) for x in next(reader)]
            sd_params = [float(x) for x in next(reader)]

            #set params to be as in documentation

            a_1, b_1, _, c_1 = (np.array(mean_params) / mean_params[2])
            a_2, b_2, _, c_2 = (np.array(sd_params) / sd_params[2])
            M = np.linalg.inv(([a_1 - 1, b_1], [a_2, b_2 - 1]))
            
           
    mean, sd = np.matmul(M, np.array((c_1 - mle_mean, c_2 - mle_sd)))

    return mean, sd




""" size_dist parameter is a dictionary with form {'lower-upper': n, ... 'lower+': n}
    like the ONS size distributions

    return mean and standard deviation (not variance)

"""

def match_expectation(size_dist):
    result = minimize(lambda x: expectation_difference(x, size_dist), (0, 1), bounds=Bounds([-np.inf, 0], [np.inf, np.inf]))
    if result.success:
        return result.x
    else:
        return None


def max_likelihood(size_dist, distribution_mean=None):
    """ Returns the estimated mean, sd from size dist

        Arguments
        ------------
        size_dist: dict of the form {str: float or int} where the string is 'a_i-a_i+1' or 'a_n+' and the float or int is the proportion or number of companies in that bin.
        (optional) distribution_mean: if the mean of the distribution is known then this is a constraint that can be used to improve the estimation.
    """
    if distribution_mean is None:
        result = minimize(lambda x: -likelihood(x, size_dist), (0.5, 1.5), jac=lambda x: -likelihood_jacobian(x, size_dist), bounds=Bounds([-np.inf, 0], [np.inf, np.inf]))
    else:
        result = minimize(lambda x: -likelihood(x, size_dist), (0.5, 1.5), jac=lambda x: -likelihood_jacobian(x, size_dist), bounds=Bounds([-np.inf, 0], [np.inf, np.inf]), constraints={'type': 'eq', 'fun': lambda x: np.exp(x[0] + x[1] ** 2 / 2) - distribution_mean})
    #print(result)

    if result.success:
        return result.x
    else:
        return None


def likelihood(params, size_dist):
    mean, sd = params
    total = 0
    for size_band, n in size_dist.items():
        if '-' in size_band:
            lower = int(size_band.split('-')[0])
            upper = int(size_band.split('-')[1]) + 1
        else:
            lower = int(size_band.split('+')[0])
            upper = np.inf

        if upper == np.inf:
            x = 1 - norm.cdf((np.log(lower) - mean) / sd)
        elif lower == 0:
            x = norm.cdf((np.log(upper) - mean) / sd)
        else:
            x = norm.cdf((np.log(upper) - mean) / sd) - norm.cdf((np.log(lower) - mean) / sd)

        #print(x)

        total += n * np.log(x)

    return total


def likelihood_jacobian(params, size_dist):
    jacobian = np.zeros(2)
    mean, sd = params
    for size_band, n in size_dist.items():
        if '-' in size_band:
            lower = int(size_band.split('-')[0])
            upper = int(size_band.split('-')[1]) + 1
        else:
            lower = int(size_band.split('+')[0])
            upper = np.inf

        if upper == np.inf:
            d_l = n / (1 - norm.cdf((np.log(lower) - mean) / sd))
            jacobian[0] += -d_l * (- norm.pdf((np.log(lower) - mean) / sd)) / sd
            jacobian[1] += -d_l * (- norm.pdf((np.log(lower) - mean) / sd) * (np.log(lower) - mean)) / sd ** 2
        elif lower == 0:
            d_l = n / (norm.cdf((np.log(upper) - mean) / sd))
            jacobian[0] += -d_l * (norm.pdf((np.log(upper) - mean) / sd)) / sd
            jacobian[1] += -d_l * (norm.pdf((np.log(upper) - mean) / sd) * (np.log(upper) - mean)) / sd ** 2
        else:
            d_l = n / (norm.cdf((np.log(upper) - mean) / sd) - norm.cdf((np.log(lower) - mean) / sd))
            jacobian[0] += -d_l * (norm.pdf((np.log(upper) - mean) / sd) - norm.pdf((np.log(lower) - mean) / sd)) / sd
            jacobian[1] += -d_l * (norm.pdf((np.log(upper) - mean) / sd) * (np.log(upper) - mean) - norm.pdf((np.log(lower) - mean) / sd) * (np.log(lower) - mean)) / sd ** 2

    return jacobian


def expectation_difference(params, size_dist):
    mean, sd = params

    expectation = []
    actual = []
    total = 0

    for size_band, n in size_dist.items():
        total += n
        if '-' in size_band:
            lower = int(size_band.split('-')[0])
            upper = int(size_band.split('-')[1]) + 1
        else:
            lower = int(size_band.split('+')[0])
            upper = np.inf

        expectation.append(lognorm.cdf(upper, sd, scale=np.exp(mean)) - lognorm.cdf(lower, sd, scale=np.exp(mean)))

        actual.append(n)



    return ((total * np.array(expectation) - np.array(actual)) ** 2).mean()




def read_file(file):
    base_sizes = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249']

    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        first_line = next(reader)
        csvfile.seek(0)
        read_as_dict = '0-4' in first_line
        if read_as_dict:
            reader = csv.DictReader(csvfile)
            id_key = first_line[0]

        if len(first_line) == 8 or len(first_line) == 9:
            sizes = base_sizes + ['250+']
        elif len(first_line) == 10 or len(first_line) == 11:
            sizes = base_sizes + ['250-499', '499-999', '1000+']
        else:
            raise ValueError('Line length for' + file + ' does not match size distribution table')

        file_data = {}

        for line in reader:
            if read_as_dict:
                file_data[line[id_key]] = {size: float(line[size]) for size in sizes}
            else:
                file_data[line[0]] = {size: float(line[i]) for i, size in sizes}

    return file_data


if __name__ == '__main__':
    options = [s for s in sys.argv[1:] if '=' in s]
    for option in options:
        if option.split('=')[0] != 'output_dir':
            print('Unrecognised option: ' + option.split('=')[0])
            exit()
        else:
            output_dir = str.join(option.split('=')[1:])
    else:
        output_dir = './'
    files = sys.argv[1:]
    main(files, output_dir)
