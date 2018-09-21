import calculate_parameters


def main():
	data = [1713790,285060,142305,75755,24015,13640,9080]
	bands = ['0-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250+']
	data = {bands[i]: data[i] for i in range(len(data))}

	print(calculate_parameters.max_likelihood(data))

if __name__ == '__main__':
	main()