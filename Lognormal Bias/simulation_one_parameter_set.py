"""Script to test the parameter recovery of the MLE

"""

from scipy.stats import lognorm
import numpy as np, matplotlib.pyplot as plt

import calculate_parameters, analysis

from multiprocessing import Pool

def main(mean=1, sd=1.2):
	# 170 000 companies per local authority


	mean_with, sd_with, mean_without, sd_without = recovery_simulation(170000, 0.5, 1.5)
	figure = plt.figure(figsize=(16, 6))
	plt.subplot(121)
	plt.hist(mean_with, 50, density=True, alpha=0.5, label='Mean using distribution mean')
	plt.hist(mean_without, 50, density=True, alpha=0.5, label='Mean without using distribution mean')

	plt.subplot(122)
	plt.hist(sd_with, 50, density=True, alpha=0.5, label='Standard Deviation using distribution mean')
	plt.hist(sd_without, 50, density=True, alpha=0.5, label='Standard Deviation without using distribution mean')

	plt.savefig('0.51.5paramest.png')
	plt.show()


def parameter_expectation(n, mean, sd):
	print(n)
	sim = recovery_simulation(n, mean, sd)
	return [np.mean(x) for x in sim]

def recovery_simulation(n, mean, sd):
	mean_with_dist_mean = []
	mean_without_dist_mean = []
	sd_with_dist_mean = []
	sd_without_dist_mean = []
	for i in range(1000):
		sizes = lognorm.rvs(sd, scale=np.exp(mean), size=n)
		binned_sizes = analysis.sort_sample(sizes)
		parameters_without_mean = calculate_parameters.max_likelihood(binned_sizes)
		parameters_with_mean = calculate_parameters.max_likelihood(binned_sizes, sizes.mean())

		if parameters_without_mean is not None and parameters_with_mean is not None:
			mean_with_dist_mean.append(parameters_with_mean[0])
			sd_with_dist_mean.append(parameters_with_mean[1])
			mean_without_dist_mean.append(parameters_without_mean[0])
			sd_without_dist_mean.append(parameters_without_mean[1])

	return mean_with_dist_mean, sd_with_dist_mean, mean_without_dist_mean, sd_without_dist_mean
	
if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		main(float(sys.argv[1]), float(sys.argv[2]))
	else:
		main()
