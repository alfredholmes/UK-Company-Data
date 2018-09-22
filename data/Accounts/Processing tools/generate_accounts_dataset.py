""" This script reads xbrl and ixbrl files used in companies house accounts data product
	and produces a json file for each year, typically about 5GB in size for recent years
	(2015, 16, 17)

	To run, run this script from a directory with the unzipped data product files in
	folders for each year so, for example the folder '2008/' contains the 100 000 or so
	files from the 2008 accounts.
"""

import os, re, json, sys
import parse_xml
import xml.etree.ElementTree as ET

non_decimal = re.compile(r'[^\d.]+')
numbers = re.compile(r'[^\d]+')

def main(year=None):
	if year is None:
		years = [str(y) for y in range(2008, 2015)]
	else:
		years = [year]
	for year in years:
		print(year)
		accounts = []
		files = [year + '/' + f for f in os.listdir(year)]
		#print(len(files))
		for i, f in enumerate(files):
			if i % 10000 == 0:
				print(i / len(files))
			file = parse_xml.readfile(f)
			try:
				et = ET.fromstring(file)
			except ET.ParseError:
				#print(file)
				continue
			file_data = {}
			if f[-3:] == 'xml':
				company_number, start_date, end_date = get_date_company_id(et, 'xml')
				read_element_tree(et, file_data, 'xml')
			else:
				company_number, start_date, end_date = get_date_company_id(et, 'html')
				read_element_tree(et, file_data, 'html')

			data = assign_instances(file_data, start_date, end_date)

			if company_number is not None:
				accounts.append({'company_number': company_number, 'start_date': start_date, 'end_date': end_date, 'accounts': data})

		with open(year + '_accounts.json', 'w') as out_file:
			json.dump(accounts, out_file, indent=4)

def read_element_tree(et, data, file_type='html'):
	looking_for = ['asset', 'share', 'turnover', 'profit', 'gross']
	for child in et:
		read_element_tree(child, data)
		tag = get_tag(child, file_type)
		if tag is None:
			continue

		for s in looking_for:
			if s in tag and 'contextRef' in child.attrib:
				n = get_number_from_string(str(child.text))
				if n is None:
					continue
				if tag in data:
					data[tag].append((str(child.attrib['contextRef']), n))
				else:
					data[tag] = [(str(child.attrib['contextRef']), n)]
				break



def get_date_company_id(et, file_type='html', company_number=None, start_date=None, end_date=None):
	for child in et:
		if company_number is not None and start_date is not None and end_date is not None:
			break
		if file_type == 'xml':
			if start_date is None and'balancesheetdate' in child.tag.lower():
				end_date = child.text
				start_date = str(int(child.text[:4]) - 1) + child.text[4:]
			if company_number is None and 'companieshouseregisterednumber' in child.tag.lower():
				company_number = child.text
		else:
			if start_date is None and 'startdate' in child.tag.lower():
				start_date = child.text
			if end_date is None and 'enddate' in child.tag.lower():
				end_date = child.text
			if company_number is None and 'identifier' in child.tag.lower():
				if 'http' not in child.text:
					company_number = child.text
		company_number, start_date, end_date = get_date_company_id(child, file_type, company_number, start_date, end_date)


	return company_number, start_date, end_date

def assign_instances(data, start_date, end_date):
	new_data = {}
	for tag, instanced_data in data.items():
		instanced_data = set(instanced_data)
		instanced_data = [i for i in instanced_data]

		if len(instanced_data) == 1:
			new_data[tag] = [(start_date, instanced_data[0][1])]
		elif len(instanced_data) == 2:
			#check carried forward and brought forward
			if 'bf' in instanced_data[0][0] and 'cf' in instanced_data[1][0]:
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'cf' in instanced_data[0][0] and 'bf' in instanced_data[1][0]:
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue


			#sometimes the header has the date at the end, see if that is the case
			if len(numbers.sub("", instanced_data[0][0])) > 0 and len(numbers.sub("", instanced_data[1][0])) > 0:
				try:
					if int(numbers.sub("", instanced_data[0][0])) < int(numbers.sub('', instanced_data[1][0])):
						new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
						continue
					elif int(numbers.sub("", instanced_data[0][0])) > int(numbers.sub('', instanced_data[1][0])):
						new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
						continue
				except ValueError as e:
					print(instanced_data[0][0])
					raise(e)
			#if unable to use the date, look for current and previous
			if 'p' in instanced_data[0][0].lower() and 'c' in instanced_data[1][0].lower():
				#print(instanced_data)
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'c' in instanced_data[0][0].lower() and 'p' in instanced_data[1][0].lower():
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue

			if 'start' in instanced_data[0][0].lower() and 'end' in instanced_data[1][0].lower():
				#print(instanced_data)
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'end' in instanced_data[0][0].lower() and 'start' in instanced_data[1][0].lower():
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue

			if 'b' in instanced_data[0][0].lower() and 'e' in instanced_data[1][0].lower():
				#print(instanced_data)
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'e' in instanced_data[0][0].lower() and 'b' in instanced_data[1][0].lower():
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue

			if 'last' in instanced_data[0][0].lower() and 'this' in instanced_data[1][0].lower():
				#print(instanced_data)
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'this' in instanced_data[0][0].lower() and 'last' in instanced_data[1][0].lower():
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue

			if 'a' in instanced_data[0][0].lower() and 'b' in instanced_data[1][0].lower():
				#print(instanced_data)
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'b' in instanced_data[0][0].lower() and 'a' in instanced_data[1][0].lower():
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue

			if 's' in instanced_data[0][0].lower() and 'e' in instanced_data[1][0].lower():
				#print(instanced_data)
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'e' in instanced_data[0][0].lower() and 's' in instanced_data[1][0].lower():
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue

			if 'ly' in instanced_data[0][0].lower() and 'ty' in instanced_data[1][0].lower():
				#print(instanced_data)
				new_data[tag] = [(start_date, instanced_data[0][1]), (end_date, instanced_data[1][1])]
				continue
			elif 'th' in instanced_data[0][0].lower() and 'ly' in instanced_data[1][0].lower():
				new_data[tag] = [(start_date, instanced_data[1][1]), (end_date, instanced_data[0][1])]
				continue


			#print(instanced_data)

		else:
			pass
			# TODO: Handle this case
	return new_data
def get_tag(child, file_type):
	tag = None
	if file_type=='html':
		if 'name' in child.attrib:
			tag = child.attrib['name'].split(':')[-1].lower()
	else:
		tag = str(child.tag).split('}')[-1].lower()
	return tag

def get_number_from_string(s):
	n = non_decimal.sub('', s)
	try:
		return float(n)
	except ValueError:
		return None

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv[1])
	else:
		main()
