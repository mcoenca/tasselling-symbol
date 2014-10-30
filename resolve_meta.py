import json


def read_json(filename):
	with open(filename) as f:
		json_data = json.load(f)
		printf(f)

read_json('meta/meta_0')