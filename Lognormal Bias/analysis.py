""" Script to test the bias of MLE from a log normal distribution

"""

from scipy.stats import lognorm, norm
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from multiprocessing import Pool

import calculate_parameters

def main():

	fig = plt.figure(figsize=(20, 10))
	ax = fig.add_subplot(121, projection='3d')
	ax.set_title('Mean Bias')


	X, Y, Z, W, fixed_Z, fixed_W = generate_bias((-2, 2), (0.5, 3), 10)
	
	ax.plot_surface(X, Y, Z, label='Mean Bias')
	#ax.plot_surface(X, Y, W, label='Standard Deviation Bias', color='orange')
	#ax.plot_surface(X, Y, fixed_Z, label='Unbiased mean')

	#plt.legend()
	
	ax.set_xlabel('Mean')
	ax.set_ylabel('Standard Deviation')
	ax.set_zlabel('Mean Bias')

	

	
	ax = fig.add_subplot(122, projection='3d')
	ax.set_title('Standard Deviation Bias')


	ax.set_xlabel('Mean')
	ax.set_ylabel('Standard Deviation')
	ax.set_zlabel('Mean Bias')

	


	ax.plot_surface(X, Y, W, label='Mean Bias')
	plt.savefig('bias_no_dist_mean.png')
	plt.show()


def generate_bias(a, b, N):
	X = np.linspace(a[0], a[1], num=N)
	Y = np.linspace(b[0], b[1], num=N)

	params = []

	for x in X:
		for y in Y:
			params.append((170000, x, y))

	with Pool() as p:
		result = p.starmap(estimate_bias, params)



	X, Y = np.meshgrid(X, Y)
	Z = np.zeros((len(X), len(Y)))
	W = np.zeros((len(X), len(Y)))
	fixed_Z = np.zeros((len(X), len(Y)))
	fixex_W = np.zeros((len(X), len(Y)))
	for i, x in enumerate(X):
		for j, y in enumerate(Y):
			Z[i][j] = result[i + j * len(X)][0]
			W[i][j] = result[i + j * len(X)][1]	

	return X, Y, Z, W, fixed_Z, fixex_W


def estimate_bias(n, mean, sd, sample_size=100):
	print(n, mean, sd)
	mean_total = 0
	sd_total = 0
	fixed_mean_total = 0
	fixed_sd_total = 0
	for _ in range(sample_size):
		if n is not None:
			sample = lognorm.rvs(sd, scale=np.exp(mean), size=n)
			binned_sample = sort_sample(sample)
			binned_sample = {s : v / n for s, v in binned_sample.items()}


			#params = calculate_parameters.max_likelihood(binned_sample, sample.mean())
			params = calculate_parameters.max_likelihood(binned_sample)
			
		else:
			max_sizes = [0.00001, 5, 10, 20, 50, 100, 250, 10**10]
			titles = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']

			binned_sample = {titles[i]: lognorm.cdf(max_sizes[i + 1], sd, scale=np.exp(mean)) - lognorm.cdf(max_sizes[i], sd, scale=np.exp(mean)) for i in range(len(max_sizes) - 1)}

			params = calculate_parameters.max_likelihood(binned_sample, np.exp(mean + sd ** 2 / 2))
			#print(params)

		if params is None:
			continue
		recovered_mean, recovered_sd = params

		mean_total += recovered_mean - mean
		sd_total += recovered_sd - sd

		#fixed_mean, fixed_sd = calculate_parameters.remove_bias(recovered_mean, recovered_sd)
		#fixed_mean_total += fixed_mean
		#fixed_sd_total += fixed_sd

	return mean_total / sample_size, sd_total / sample_size, fixed_mean_total / sample_size, fixed_sd_total / sample_size

	

def sort_sample(sample, bins=['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']):
	""" returns dict of binned data
	"""

	bounds = []
	binned_sample = {}
	for b in bins:
		if '-' in b:
			lower = float(b.split('-')[0])
			upper = float(b.split('-')[1]) + 1
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
