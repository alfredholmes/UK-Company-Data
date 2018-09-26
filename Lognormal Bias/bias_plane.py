import analysis, numpy as np, csv
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def main():
	X, Y, Z, W = analysis.generate_bias((-1, 1), (1, 2), 100)

	mean_params = fit_plane(X, Y, Z)
	sd_params = fit_plane(X, Y, W)

	with open('plane_params.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(mean_params)
		writer.writerow(sd_params)


	#fig = plt.figure()
	#ax = fig.add_subplot(111, projection='3d')

	#ax.plot_surface(X, Y, Z, alpha=0.5)
	#ax.plot_surface(X, Y, plane(X, Y, mean_params), alpha=0.5)

	#plt.show()

def plane(X, Y, params):
	a, b, c, d = params
	return -(a * X + b * Y - d) / c


def fit_plane(X, Y, Z):
	return minimize(error, (1, 1, 1, 1), args=(X, Y, Z)).x


def error(params, X, Y, Z):
	a, b, c, d = params
	
	return (((a * X + b * Y - d) / c + Z) ** 2).sum()


if __name__ == '__main__':
	main()