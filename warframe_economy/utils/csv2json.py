import csv
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('model', help='Name of the model the JSON will be produced for', choices=('sets', 'items'))
parser.add_argument('file', help='Location of the CSV file')
args = parser.parse_args()

APP = 'dashboard'
MODELS = {
    'sets' : 'PrimeSet',
}

results = []

with open(args.file, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    pk = 1
    for row in csv_reader:
        if args.model == 'sets':
            object = {}
            object['model'] = f'{APP}.{MODELS["sets"]}'
            object['pk'] = pk
            object['fields'] = {
                        "name" : row[0],
                        "url_name": row[1],
                        "ducats": 0
                    }
            results.append(object)
            pk += 1

print(json.dumps(results))
