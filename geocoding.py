from string import ascii_uppercase
import worksheet
from collections import OrderedDict
from typing import Union
from openpyxl.worksheet.worksheet import Worksheet
from geopy.geocoders.yandex import Yandex
from geopy.geocoders.google import GoogleV3
from pprint import pprint


def find_address_components(dictionary: dict, keys: list) -> list:
    info = dictionary
    for i in keys:
        if i is not None:
            info = info.get(i)
        else:
            raise ValueError(f'There is wrong structure of keys: {keys}\nNesting in the {info} stops on {i} key')
    return info


def parsing(geocoder: dict[str, Union[Yandex, GoogleV3, dict, str]], place: str) -> OrderedDict:
    geocoded = geocoder['engine'].geocode(place)
    keys = geocoder['keys']
    country = region = city = street = house_number = postal_code = None
    if geocoded is not None:
        for info in find_address_components(geocoded.raw, keys['nested_dict']):
            item = info[keys['item']]
            value = info[keys['value']]
            if keys['country'] in item:
                country = value
            if keys['city'] in item:
                city = value
            if keys['region'] in item:
                region = value
            if keys['house_number'] in item:
                house_number = value
            if keys['street'] in item:
                street = value
            postal_code = find_address_components(geocoded.raw, keys.get('postal_code'))
            if geocoder['type'] == 'google' and postal_code is not None:
                postal_code = postal_code[-6:]

    parsed_info = OrderedDict([
        ('country', country),
        ('region', region),
        ('city', city),
        ('street', street),
        ('house_number', house_number),
        ('postal_code', postal_code),
    ])
    pprint(parsed_info)
    return parsed_info


def geocode(sheet: Worksheet, geocoders: list[dict]) -> None:
    source_column = sheet[ascii_uppercase[0]]

    for i, cell in enumerate(source_column[1:], start=1):
        place = cell.value
        for geocoder in geocoders:
            parsed_info = parsing(geocoder, place)
            if all(parsed_info.values()):
                worksheet.write_in_a_row(sheet, i, parsed_info)
                break
