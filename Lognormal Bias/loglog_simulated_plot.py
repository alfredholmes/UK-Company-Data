from scipy.stats import lognorm, norm

import numpy as np
import matplotlib.pyplot as plt

import calculate_parameters
import analysis

def main():
	
	bounds = [0, 5, 10, 20, 50, 100, 250, np.inf]
	titles = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']

	X = {t: [] for t in titles}
	Y = {t: [] for t in titles}
	Z = {t: [] for t in titles}

	for x in np.linspace(-1, 1, num=10):
		for y in np.linspace(0.5, 3, num=10):

			mean = x
			sd = y
			size = int(17000 + norm.rvs(0, 2000))
			sample = lognorm.rvs(sd, scale=np.exp(mean), size=size)
			binned_sample = analysis.sort_sample(sample)
			binned_sample = {titles[i]: lognorm.cdf(bounds[i+1],sd, scale=np.exp(mean)) - lognorm.cdf(bounds[i],sd, scale=np.exp(mean)) for i in range(len(bounds) - 1)}
			params_with_mean = calculate_parameters.max_likelihood(binned_sample, np.exp(mean + sd ** 2 / 2))
			params = calculate_parameters.max_likelihood(binned_sample, sample.mean())			
			if params is None or params_with_mean is None:
				continue
			r_mean, r_sd = params
			
			r_sample = lognorm.rvs(r_sd, scale=np.exp(r_mean), size=size)
			r_binned_sample = analysis.sort_sample(r_sample)
			
			r_with_mean_mean, r_with_mean_sd = params_with_mean			

			r_with_mean = lognorm.rvs(r_sd, scale=np.exp(r_mean), size=size)
			r_with_mean_binned_sample = analysis.sort_sample(r_with_mean)
			
			
			r_binned_sample = {titles[i]: lognorm.cdf(bounds[i+1],r_sd, scale=np.exp(r_mean)) - lognorm.cdf(bounds[i],r_sd, scale=np.exp(r_mean)) for i in range(len(bounds) - 1)}

			

			for t, p in binned_sample.items():
				X[t].append(p / np.sum([x for x in binned_sample.values()]))
				Y[t].append(r_binned_sample[t] / np.sum([x for x in r_binned_sample.values()]))
				Z[t].append(r_with_mean_binned_sample[t] / np.sum([x for x in r_with_mean_binned_sample.values()]))
	plt.figure(figsize=(16, 6))
	plt.subplot(121)	
	plt.loglog()
	ax = plt.gca()	
	ax.set_xlim([10**-5,10**0])
	ax.set_ylim([10**-5,10**0])
	for t in titles:
		plt.scatter(X[t], Z[t], label=t)
	plt.xlabel('Actual proportion')
	plt.ylabel('Predicted proportion')
	plt.legend()		
	plt.plot([0, 1], [0, 1])
	plt.subplot(122)	
	plt.loglog()
	ax = plt.gca()
	ax.set_xlim([10**-5,10**0])
	ax.set_ylim([10**-5,10**0])
	plt.xlabel('Actual proportion')
	plt.ylabel('Predicted proportion')
	for i in range(len(X['0-4'])):
		plt.plot([X[t][i] for t in titles], [Y[t][i] for t in titles])
				
	
	plt.plot([0, 1], [0, 1])
	plt.savefig('loglog_reconstruction.png')
	plt.show()

if __name__ == '__main__':
	main()

