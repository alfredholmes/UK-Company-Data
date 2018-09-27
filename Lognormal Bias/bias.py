import matplotlib.pyplot as plt, numpy as np

import simulation_one_parameter_set, analysis
from scipy.stats import lognorm

from multiprocessing import Pool

def main(mean = 0.5, sd = 1.2):
	for x in np.linspace(1, 100000, num=16):
			max_sizes = [0.00001, 5, 10, 20, 50, 100, 250, 10**10]
			titles = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']

			binned_sample_exp = {titles[i]: lognorm.cdf(max_sizes[i + 1], sd, scale=np.exp(mean)) - lognorm.cdf(max_sizes[i], sd, scale=np.exp(mean)) for i in range(len(max_sizes) - 1)}
			binned_sample_gen = analysis.sort_sample(lognorm.rvs(sd, scale=np.exp(mean), size=int(x)))
			binned_sample_gen = {s: v / int(x) for s, v in binned_sample_gen.items()}
			print(binned_sample_gen, binned_sample_exp)
	with Pool() as p:
		data = p.starmap(simulation_one_parameter_set.parameter_expectation, [(int(x), mean, sd) for x in np.linspace(0, 100000, num=16)])

	mean_with = []
	sd_with = []
	mean_without = []
	sd_without = []

	for d in data:
		mean_with.append(d[0] - mean)
		sd_with.append(d[1] - sd)
		mean_without.append(d[2])
		sd_without.append(d[3])

	plt.plot(np.linspace(0, 100000, num=16), mean_with)
	plt.plot(np.linspace(0, 100000, num=16), sd_with)

	plt.show()

if __name__ == '__main__':
	main()