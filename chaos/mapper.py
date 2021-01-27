# Copyright (c) since 2001, Kisio Digital and/or its affiliates. All rights reserved.

from collections import Mapping, Sequence
from aniso8601 import parse_datetime, parse_time, parse_date


class Datetime(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, item, field, value):
        if value:
            setattr(
                item,
                self.attribute,
                parse_datetime(value).replace(tzinfo=None)
            )
        else:
            setattr(item, self.attribute, None)


class Time(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, item, field, value):
        if value:
            setattr(
                item,
                self.attribute,
                parse_time(value).replace(tzinfo=None)
            )
        else:
            setattr(item, self.attribute, None)


class Date(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, item, field, value):
        if value:
            setattr(item, self.attribute, parse_date(value))
        else:
            setattr(item, self.attribute, None)


class AliasText(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, item, field, value):
        setattr(item, self.attribute, value)


class OptionalField(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, item, field, json):
        if field in json and json[field] is not None:
            setattr(item, self.attribute, json[field])


def fill_from_json(item, json, fields):
    for field, formater in fields.iteritems():
        if isinstance(formater, OptionalField):
            formater(item, field, json)
        else:
            if field not in json:
                setattr(item, field, None)
                continue
            if isinstance(formater, Mapping):
                fill_from_json(item, json[field], fields=formater)
            elif isinstance(formater, Sequence):
                for fr in formater:
                    for key in fr.keys():
                        for one_json in json[field]:
                            fr[key](item, key, one_json[key])
            elif not formater:
                setattr(item, field, json[field])
            elif formater:
                formater(item, field, json[field])


disruption_mapping = {
    'reference': None,
    'note': None,
    'status': OptionalField(attribute='status'),
    'publication_period': {
        'begin': Datetime(attribute='start_publication_date'),
        'end': Datetime(attribute='end_publication_date')
    },
    'cause': {'id': AliasText(attribute='cause_id')},
    'author': None
}

severity_mapping = {
    'color': None,
    'priority': None,
    'effect': None,
}

cause_mapping = {
    'category': {'id': AliasText(attribute='category_id')},
}

tag_mapping = {
    'name': None
}

property_mapping = {
    'key': None,
    'type': None
}

category_mapping = {
    'name': None
}

object_mapping = {
    "id": AliasText(attribute='uri'),
    "type": None
}

message_mapping = {
    "text": None,
    'channel': {'id': AliasText(attribute='channel_id')}
}

meta_mapping = {
    'key': None,
    'value': None
}

application_period_mapping = {
    'begin': Datetime(attribute='start_date'),
    'end': Datetime(attribute='end_date')
}

channel_mapping = {
    'name': None,
    'max_size': None,
    'content_type': None,
    'required': OptionalField(attribute='required')
}

line_section_mapping = {
    'line': None,
    'start_point': None,
    'end_point': None
}

line_section_mapping = {
    'line': None,
    'start_point': None,
    'end_point': None,
    'blocked_stop_areas': None,
    'route_patterns': None,
}

pattern_mapping = {
    'start_date': Date(attribute='start_date'),
    'end_date': Date(attribute='end_date'),
    'weekly_pattern': None,
    'time_zone': None
}

time_slot_mapping = {
    'begin': Time(attribute='begin'),
    'end': Time(attribute='end')
}

export_mapping = {
    'start_date': Datetime(attribute='start_date'),
    'end_date': Datetime(attribute='end_date'),
    'time_zone': None
}

contributor_mapping = {
    'code': AliasText(attribute='contributor_code')
}
