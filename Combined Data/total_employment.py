import csv

def main():
	total = 0
	with open('2014_sizes.csv', 'r') as csvfile:
		reader = csv.reader(csvfile)
		for line in reader:
			total += round(float(line[1]))

	print(total)

if __name__ == '__main__':
	main()	