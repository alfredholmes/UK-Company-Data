""" Script to test the bias of MLE from a log normal distribution

"""

from scipy.stats import lognorm, norm
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from multiprocessing import Pool

import calculate_parameters

def main():
	sd = 1.2 # TODO: Randomize / use sample

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')


	a = 0.5
	b = 4
	N = 40


	X = np.linspace(a, b, num=N)
	Y = X

	params = []

	for x in X:
		for y in Y:
			params.append((10000, x, y))

	with Pool() as p:
		result = p.starmap(estimate_bias, params)



	X, Y = np.meshgrid(X, Y)
	Z = np.zeros((len(X), len(Y)))
	W = np.zeros((len(X), len(Y)))
	for i, x in enumerate(X):
		for j, y in enumerate(Y):
			Z[i][j] = result[i + j * len(X)][0]
			W[i][j] = result[i + j * len(X)][1]	
	
	ax.plot_wireframe(X, Y, Z, label='Mean Bias')
	ax.plot_wireframe(X, Y, W, label='Standard Deviation Bias', color='orange')
	plt.legend()
	plt.savefig('bias.png')
	plt.show()


def estimate_bias(n, mean, sd, sample_size=10):
	print(n, mean, sd)
	mean_bias_total = 0
	sd_bias_total = 0
	for _ in range(sample_size):
		sample = lognorm.rvs(sd, scale=np.exp(mean), size=n)
		binned_sample = sort_sample(sample)


		params = calculate_parameters.max_likelyhood(binned_sample)
		if params is None:
			continue
		recovered_mean, recovered_sd = params

		mean_bias_total += recovered_mean - mean
		sd_bias_total += recovered_sd - sd

	return mean_bias_total / sample_size, sd_bias_total / sample_size

	

def sort_sample(sample, bins=['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']):
	""" returns dict of binned data
	"""

	bounds = []
	binned_sample = {}
	for b in bins:
		if '-' in b:
			lower = float(b.split('-')[0])
			upper = float(b.split('-')[1])
		else:
			lower = float(b.split('+')[0])
			upper = np.inf

		n = 0

		for x in sample:
			if x >= lower and x < upper:
				n += 1
		binned_sample[b] = n

	return binned_sample


if __name__ == '__main__':
	main()
