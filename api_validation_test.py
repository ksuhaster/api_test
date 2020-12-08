#!/usr/bin/env python3
import pytest
import requests
import json
from jsonschema import Draft7Validator


def create_path(path_arr, json_data):
    obj_idx = path_arr.pop(1)
    current_obj = json_data['results'][obj_idx]

    if (current_obj.get('id')):
        obj_ID = json_data['results'][obj_idx]['id']
        symbol = 'ID-'
    else:
        obj_ID = obj_idx
        symbol = 'Object_count='

    path_arr.insert(1, symbol + str(obj_ID))
    return '/'.join(path_arr)


def main_teardown(v, data):
    for error_idx, error in enumerate(v.iter_errors(data), start=1):
        error_path = list(error.path)
        error_key_name = error_path[0] if error_path else 'root'

        if len(error_path) >= 2:
            str_path = create_path(error_path, data)
            print(f'Error {error_idx} at "{str_path}": {error.message}\n')
        else:
            print(f'Error {error_idx} at "{error_key_name}": {error.message}\n')


@pytest.fixture()
def main_schema(data):
    with open('schemas/full_schema.json') as api_schema:
        main_schema = json.load(api_schema)

    v = Draft7Validator(main_schema)
    yield v
    main_teardown(v, data)


@pytest.fixture()
def data():
    response = requests.get('https://djinni.co/api/jobs')
    json_data = response.json()

    return json_data


@pytest.fixture()
def data_objects(data):
    return data['results']


def test_schema(main_schema, data):
    assert main_schema.is_valid(data)


def test_if_10(data_objects):
    assert len(data_objects) == 10, f'\n--- EXPECTED --- \n10 objects in "results"\n--- GOT ---\n{len(data_objects)} objects in "results"\n'
