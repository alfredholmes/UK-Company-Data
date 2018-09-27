from scipy.stats import lognorm

import numpy as np
import matplotlib.pyplot as plt

import calculate_parameters
import analysis

def main():
	bounds = [0, 5, 10, 20, 50, 100, 250, np.inf]
	titles = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']

	X = {t: [] for t in titles}
	Y = {t: [] for t in titles}

	for x in np.linspace(0, 1, num=10):
		for y in np.linspace(1, 2, num=10):

			mean = x
			sd = y

			sample = lognorm.rvs(sd, scale=np.exp(mean), size=100000)
			binned_sample = analysis.sort_sample(sample)
			#proportions = {titles[i]: lognorm.cdf(bounds[i+1],sd, scale=np.exp(mean)) - lognorm.cdf(bounds[i],sd, scale=np.exp(mean)) for i in range(len(bounds) - 1)}
			params = calculate_parameters.max_likelihood(binned_sample, sample.mean())
			if params is None:
				continue
			r_mean, r_sd = params
			r_proportions = {titles[i]: lognorm.cdf(bounds[i+1],r_sd, scale=np.exp(r_mean)) - lognorm.cdf(bounds[i],r_sd, scale=np.exp(r_mean)) for i in range(len(bounds) - 1)}

			print(mean, r_mean)

			for t, p in binned_sample.items():
				X[t].append(p / np.sum([x for x in binned_sample.values()]))
				Y[t].append(r_proportions[t])
	plt.loglog()
	for t in titles:
		print(X[t], Y[t])
		plt.scatter(X[t], Y[t], label=t)
	plt.xlabel('Actual proportion')
	plt.ylabel('Predicted proportion')
	plt.show()

if __name__ == '__main__':
	main()

