import csv, json, requests, re, time, random



#register account with companies house and add an array keys into a file called apikeys.py
# TODO: Reimplement getting current postcode through filing history as quicker than sending requests
# TODO: Think about multithreading - issues with compatability
import apikeys


def main():
    #seed the random number generator such that the shuffle of the array is the same each time the scrips runs
    random.seed(0)
    #get the company index to start
    start = 0
    try:
        with open('number_of_companies_processed.txt', 'r') as f:
            s = f.read()
            start = int(s)
    except FileNotFoundError as e:
        start = 0


    #load post code data
    print('Loading Postcode data...')
    pc = PostCodeHandler()
    print('Done')
    #load CompanyNumber array
    print('Loading Company Numbers...')
    company_numbers = get_company_numbers(start)
    print('Done')
    print('Shuffling companies')
    random.shuffle(company_numbers)
    print('Done')


    chapi = CompaniesHouseAPI(apikeys.keys)
    i = start

    #loop through the compnies, get the filing history and find location changes and staff changes, and write this to a file after n iterations
    data = []
    for company in company_numbers:
        try:
            i += 1
            print('Evaluating company ' + str(i))
            filing_history = chapi.get_company_filing_history(company)
            #get address and people changes
            moves = parse_filing_history(filing_history, company, pc, chapi)
            data += moves
            if i % 100 == 0:
                print('Writing companies: ' + str(i))
                write_data(data)
                data = []
                with open('number_of_companies_processed.txt', 'w') as f:
                    f.write(str(i))
        except Exception as e:
            logerror('Unhandeled error in main loop:' + str(e))

def logerror(err):
    with open('errors', 'a') as errorfile:
        errorfile.write(err + '\n')


def write_data(data):
    with open('company_migration_data.csv', 'a') as csvfile:
        fields = ['CompanyNumber', 'Date','OldPostcode', 'NewPostcode', 'OldLocalAuthority', 'NewLocalAuthority', 'RegisteredStaff', 'IncorperationDate','NFiles']
        writer = csv.DictWriter(csvfile, fields)
        for line in data:
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(line)

def get_company_numbers(start):
    numbers = []
    i = 0
    with open('CompanyNumbers2012-2018.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
                i += 1 # TODO : should make more efficient since still assigning data
                if start < i:
                    numbers.append(line[0])

    return numbers


def parse_filing_history(filing_history, company, pc, chapi):
    #get the current address
    current_postcode = chapi.get_company_postcode(company, filing_history)
    if current_postcode is None:
        logerror('Error getting current postcode for ' + company)
        return []

    #reverse the filing history array such that the array is in chronological order

    filing_history.reverse()
    moves = []
    # TODO: Verify that companies start with 1 staff member
    staff  = 1
    files = 0
    staff_at_date = {}
    files_at_date = {}
    for event in filing_history:
        files += 1
        if event['category'] == 'address':
            postcode = None
            if 'description' in event and event['description'] == 'legacy':
                not_important_strings = ['sit reg', 'register of members', 'debenture register', 'Sit of register', 'register of directors']
                for s in not_important_strings:
                    if s in event['description_values']['description']:
                        break
                else:
                    postcode = PostCodeHandler.postcode_from_address(event['description_values']['description'])
                    if postcode is None:
                        # TODO Implement google maps search to find address
                        print(event)

            elif 'type' in event and event['type'] == 'AD01':
                postcode = PostCodeHandler.postcode_from_address(event['description_values']['old_address'])
            if postcode is not None:
                if len(moves) > 0 and moves[-1] != postcode:
                    moves.append({'date': event['date'], 'moving_from': postcode})
                elif len(moves) == 0 and postcode != current_postcode:
                    moves.append({'date': event['date'], 'moving_from': postcode})
        if event['category'] == 'officers':
            if 'description' in event and event['description'] == 'legacy':
                parts = event['description_values']['description'].lower().split(';')
                for part in parts:
                    if 'new' in part or 'appointed' in part:
                        staff += 1
                    if 'terminated' in part or 'resigned' in part:
                        staff -= 1

        if event['category'] == 'persons-with-significant-control':
            if event['subcategory'] == 'register' or event['subcategory'] == 'notifications':
                staff += 1
            if event['subcategory'] == 'termination':
                staff -= 1
        if staff < 1:
            staff = 1

        staff_at_date[event['date']] = staff
        files_at_date[event['date']] = files

    #sort out return
    r = []
    for i in range(0, len(moves)):
        r.append({
            'CompanyNumber': company,
            'Date': moves[i]['date'],
            'RegisteredStaff': staff_at_date[moves[i]['date']],
            'OldPostcode': moves[i]['moving_from'],
            'NewPostcode': current_postcode if i == len(moves) - 1 else moves[i + 1]['moving_from'],
            'OldLocalAuthority': pc.get_local_authority_from_postcode(moves[i]['moving_from']),
            'NewLocalAuthority': pc.get_local_authority_from_postcode(current_postcode if i == len(moves) - 1 else moves[i + 1]['moving_from']),
            'IncorperationDate': filing_history[0]['date'],
            'NFiles': files_at_date[moves[i]['date']]
        })
        to_delete = []
        for i in range(0, len(r)):
            if r[i]['OldLocalAuthority'] is None:
                if i == 0:
                    to_delete.append(i)
                else:
                    r[i]['OldLocalAuthority'] = r[i - 1]['OldLocalAuthority']
                    to_delete.append(i - 1)
        for i in to_delete:
            del r[i]


    return r

class CompaniesHouseAPI:
    def __init__(self, keys):
        self.keys = keys
        self.key = 0
        self.number_of_keys = len(keys)
        self.last_api_call = 0
        self.api_delay = 0.5 / self.number_of_keys

    def prevent_call_limit(self):
        if time.time() - self.last_api_call < 0.5 / self.api_delay:
            time.sleep(0.5 / self.api_delay - (time.time() - self.last_api_call))

    def get_company_filing_history(self, company):
        index = 0
        fh = []
        while True:
            self.prevent_call_limit()
            req = requests.get('https://api.companieshouse.gov.uk/company/' + company + '/filing-history', data={'items_per_page': 100, 'start_index': index}, auth=(apikeys.keys[self.key], ''))
            self.last_request = time.time()
            self.key = (self.key + 1) % self.number_of_keys
            if req.status_code != 200:
                logerror('Error with request: ' + req.status_code + req.text)
                return None

            available_files = json.loads(req.text)['total_count']

            if available_files <= 0:
                return fh
            else:
                fh = fh + json.loads(req.text)['items']

            if len(fh) >= json.loads(req.text)['total_count']:
                return fh
            index += 100

    def get_company_postcode(self, company, filing_history = None):
        try:
            if filing_history is not None:
                for file in filing_history:
                    if 'category' in file and file['category'] == 'address':
                        if 'description_values' in file and 'new_address' in file['description_values']:
                            pc = PostCodeHandler.postcode_from_address(file['description_values']['new_address'])
                            if pc is not None:
                                return pc
                        else:
                            break

            self.prevent_call_limit()
            req = requests.get('https://api.companieshouse.gov.uk/company/' + company + '/registered-office-address', auth=(apikeys.keys[self.key], ''))
            self.last_request = time.time()
            self.key = (self.key + 1) % self.number_of_keys
            return json.loads(req.text)['postal_code']
        except Exception as e:
            if str(e) == 'postal_code':
                logerror('Postal code not returned in reg office address for company ' + company)
            return None



class PostCodeHandler:
    def __init__(self):
        with open('postcode_la.csv', 'r') as csvfile:
            self.postcode_local_authority = {}
            reader = csv.reader(csvfile)
            for line in reader:
                self.postcode_local_authority[line[0]] = line[1]

    def get_local_authority_form_address(self, address):
        s = PostCodeHandler.postcode_from_address(address[-20:])
        self.get_local_authority_from_postcode(s)

    def get_local_authority_from_postcode(self, postcode):
        if postcode is None:
            logerror('Error parsing postcode is None')
            return None

        if postcode in self.postcode_local_authority:
            return self.postcode_local_authority[postcode]
        else:
            logerror('Postcode not recognised: ' + postcode)
            return None

    def postcode_from_address(address):
        try:
            s = re.search(r'\s([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))\s?[0-9][A-Za-z]{2})', address.upper()[-25:]).group(0)
        except Exception as e:
            logerror('Error getting postcode from part of address: ' + address.upper()[-25:] + ' from the address ' + address)
            return None
        #split and remove spaces
        s = s.split(' ')
        s = [a for a in s if len(a) > 0]
        if len(s) != 2:
            if len(s) == 1:
                return s[0][:-3] + " " + s[0][-3:]
            return None
        else:
            return s[0] + " " + s[1]





if __name__ == '__main__':
    main()
