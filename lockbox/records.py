# -*- coding: utf-8 -*-

'''
lockbox.records
---------------

This module contains the definitions of the different types of BAI
lockbox records.

'''

import datetime
import re
import six

from .exceptions import LockboxDefinitionError, LockboxParseError


class LockboxFieldType(object):
    '''The three possible field types available are ``Numeric``, which is
    means the field contains only numeric characters, ``Alphanumeric``
    which actually means all alphanumeric characters as well as
    ``;:,./()-``.

    .. note:: This class isn't meant to be instantiated, but rather like
              an enum.
    '''
    Numeric = 'numeric'
    Alphanumeric = 'alphanumeric'
    Blank = 'blank'


class LockboxBaseRecord(object):
    # Valid types are listed inside the LockboxFieldType class.

    # Note: The record type which is determined by first character of
    # a line is defined by setting MAX_RECORD_LENGTH in a derrived
    # class rather than by adding it to the 'fields' field.

    # Officially this should be 104 but we've already gotten lines
    # longer than that
    MAX_RECORD_LENGTH = 160

    RECORD_TYPE_NUM = None

    raw_record_text = ''
    children = []

    def __init__(self, raw_record_text):
        if len(raw_record_text) > self.MAX_RECORD_LENGTH:
            raise LockboxParseError(
                'record longer than {}'.format(self.MAX_RECORD_LENGTH)
            )

        self.raw_record_text = raw_record_text

        if hasattr(self, 'fields'):
            # we can only parse if there are actually fields defined
            self.fields['record_type'] = {
                'location': (0,1),
                'type':  LockboxFieldType.Numeric,
            }
            self._parse()

            if hasattr(self, 'validate'):
                self.validate()

            # all of the basic type checking (alphanumeric vs numeric)
            # has already been performed by the regexps in _parse(),
            # so at this point we just create any missing fields by
            # doing self.my_field = self._my_field_raw
            for field_name, field_def in six.iteritems(self.fields):
                if hasattr(self, field_name):
                    continue

                raw_field_name = '_{}_raw'.format(field_name)

                raw_field_val = (
                    None
                    if field_def['type'] ==  LockboxFieldType.Blank
                    else getattr(self, raw_field_name, None)
                )

                setattr(self, field_name, raw_field_val)

    def _parse(self):
        for field_name, field_def in six.iteritems(self.fields):
            raw_field_name = '_{}_raw'.format(field_name)
            if hasattr(self, field_name):
                raise AttributeError(
                    'LockboxRecord already has field "{}"'.format(
                        field_name,
                    )
                )

            start_col, end_col = field_def['location']
            raw_field = self.raw_record_text[start_col:end_col]

            if field_def['type'] ==  LockboxFieldType.Alphanumeric:
                patt = re.compile(r'^[ A-Z0-9;:,./()-]+$')
            elif field_def['type'] ==  LockboxFieldType.Numeric:
                patt = re.compile(r'^[0-9]+$')
            elif field_def['type'] ==  LockboxFieldType.Blank:
                patt = re.compile(r'^\s*$')
            else:
                raise LockboxDefinitionError(
                    'invalid field type found: "{}"'.format(field_def['type'])
                )

            if not patt.match(raw_field):
                raise LockboxParseError(
                    'field {} does not match expected type {}'.format(
                        field_name,
                        field_def['type'],
                    )
                )

            setattr(self, raw_field_name, raw_field)

    def _parse_as_date(self, field_name, mmddyy=False):
        raw_field_name = '_{}_raw'.format(field_name)

        if not hasattr(self, raw_field_name):
            raise AttributeError("'{}' has no field '{}'".format(
                self.__class__.__name__,
                field_name
            ))

        try:
            field_val = getattr(self, raw_field_name)
            if len(field_val) != 6:
                raise ValueError()

            if not mmddyy:
                parsed_date = datetime.date(
                    # format of the (raw) field is YYMMDD
                    int(field_val[0:2]) + 2000,
                    int(field_val[2:4]),
                    int(field_val[4:6]),
                )
            else:
                parsed_date = datetime.date(
                    # format of the (raw) field is MMDDYY
                    int(field_val[4:6]) + 2000,
                    int(field_val[0:2]),
                    int(field_val[2:4]),
                )
        except ValueError:
            raise LockboxDefinitionError(
                '{} is not a valid YYMMDD-formatted date'.format(
                    field_val,
                )
            )

        return parsed_date

    def _parse_as_time(self, field_name):
        raw_field_name = '_{}_raw'.format(field_name)

        if not hasattr(self, raw_field_name):
            raise AttributeError("'{}' has no field '{}'".format(
                self.__class__.__name__,
                field_name
            ))

        try:
            field_val = getattr(self, raw_field_name)
            if len(field_val) != 4:
                raise ValueError()

            parsed_time = datetime.time(
                # format of the (raw) field is HHMM
                int(field_val[0:2]),
                int(field_val[2:4]),
            )
        except ValueError:
            raise LockboxDefinitionError(
                '{} is not a valid HHMM formatted date'.format(
                    field_val,
                )
            )

        return parsed_time


class LockboxImmediateAddressHeader(LockboxBaseRecord):
    RECORD_TYPE_NUM = 1

    fields = {
        'priority_code': { 'location': (1, 3), 'type':  LockboxFieldType.Numeric },
        'destination_id': { 'location': (3, 13), 'type':  LockboxFieldType.Alphanumeric },
        'originating_trn': { 'location': (13, 23), 'type':  LockboxFieldType.Numeric },
        'processing_date': { 'location': (23, 29), 'type':  LockboxFieldType.Numeric },
        'processing_time': { 'location': (29, 33), 'type':  LockboxFieldType.Numeric },
        'filler': {'location': (33, 104), 'type':  LockboxFieldType.Blank },
    }

    def validate(self):
        self.processing_date = self._parse_as_date('processing_date')
        self.processing_time = self._parse_as_time('processing_time')


class LockboxServiceRecord(LockboxBaseRecord):
    RECORD_TYPE_NUM = 2

    fields = {
        'ultimate_dest_and_origin': {
            'location': (1, 21),
            'type':  LockboxFieldType.Alphanumeric,
        },
        'ref_code':  {'location': (21, 31), 'type':  LockboxFieldType.Numeric},
        'service_type': {'location': (31, 34), 'type':  LockboxFieldType.Numeric},
        'record_size': {'location': (34, 37), 'type':  LockboxFieldType.Numeric},
        'blocking_factor': {'location': (37, 41), 'type':  LockboxFieldType.Numeric},
        'format_code': {'location': (41,42), 'type':  LockboxFieldType.Numeric},
        'filler': {'location': (42, 104), 'type':  LockboxFieldType.Blank},
    }


class LockboxDetailHeader(LockboxBaseRecord):
    RECORD_TYPE_NUM = 5

    fields = {
        'batch_number':  { 'location': (1, 4), 'type':  LockboxFieldType.Numeric },
        'ref_code':  { 'location': (4, 7, ), 'type':  LockboxFieldType.Numeric },
        'lockbox_number':  { 'location': (7, 14), 'type':  LockboxFieldType.Numeric },
        'deposit_date':  { 'location': (14, 20), 'type':  LockboxFieldType.Numeric },
        'ultimate_dest_and_origin':  {
            'location': (20, 40),
            'type':  LockboxFieldType.Alphanumeric,
        },
        'filler': {'location': (40, 104), 'type':  LockboxFieldType.Blank },
    }

    def validate(self):
        self.batch_number = int(self._batch_number_raw)
        self.deposit_date = self._parse_as_date('deposit_date')

class LockboxDetailRecord(LockboxBaseRecord):
    RECORD_TYPE_NUM = 6

    fields = {
        'batch_number': { 'location': (1, 4), 'type':  LockboxFieldType.Numeric },
        'item_number': { 'location': (4, 7), 'type':  LockboxFieldType.Numeric },
        'check_amount': { 'location': (7, 17), 'type':  LockboxFieldType.Numeric },
        'transit_routing_number': { 'location': (17, 26), 'type':  LockboxFieldType.Numeric },
        'dd_account_number': { 'location': (26, 36), 'type':  LockboxFieldType.Numeric },
        'check_number': { 'location': (36, 46), 'type':  LockboxFieldType.Numeric },
        'check_date': { 'location': (46, 52), 'type':  LockboxFieldType.Numeric },
        'remitter_name': { 'location': (52, 82), 'type':  LockboxFieldType.Alphanumeric },
        'payee_name': { 'location': (82, 160), 'type':  LockboxFieldType.Alphanumeric },
    }

    def validate(self):
        self.batch_number = int(self._batch_number_raw)
        self.item_number = int(self._item_number_raw)

        self.check_amount = int(self._check_amount_raw) / 100.00
        self.check_number = int(self._check_number_raw)
        # for some reason check_date is stored in MMDDYY format instead of the
        # otherwise standard YYMMDD
        self.check_date = self._parse_as_date('check_date', mmddyy=True)

        self.remitter_name = self._remitter_name_raw.strip()
        self.payee_name = self._payee_name_raw.strip()


class LockboxDetailOverflowRecord(LockboxBaseRecord):
    RECORD_TYPE_NUM = 4

    fields = {
        'batch_number': { 'location': (1, 4), 'type':  LockboxFieldType.Numeric },
        'item_number': { 'location': (4, 7), 'type':  LockboxFieldType.Numeric },
        'overflow_record_type': { 'location': (7, 8), 'type':  LockboxFieldType.Numeric },
        'overflow_sequence_number': { 'location': (8, 10), 'type':  LockboxFieldType.Numeric },
        'overflow_indicator': { 'location': (10, 11), 'type':  LockboxFieldType.Numeric },
        'memo_line': { 'location': (11, 41), 'type':  LockboxFieldType.Alphanumeric },
        'filler': {'location': (41, 104), 'type':  LockboxFieldType.Blank },
    }

    def validate(self):
        self.batch_number = int(self._batch_number_raw)
        self.item_number = int(self._item_number_raw)
        self.overflow_record_type = int(self._overflow_record_type_raw)
        self.overflow_sequence_number = int(self._overflow_sequence_number_raw)


class LockboxBatchTotalRecord(LockboxBaseRecord):
    RECORD_TYPE_NUM = 7

    fields = {
        'batch_number': { 'location': (1, 4), 'type':  LockboxFieldType.Numeric },
        'item_number': { 'location': (4, 7), 'type':  LockboxFieldType.Numeric },
        'lockbox_number': { 'location': (7, 14), 'type':  LockboxFieldType.Numeric },
        'deposit_date': { 'location': (14, 20), 'type':  LockboxFieldType.Numeric },
        'total_number_remittances': {
            'location': (20, 23),
            'type':  LockboxFieldType.Numeric
        },
        'check_dollar_total': { 'location': (23, 33), 'type':  LockboxFieldType.Numeric },
        'filler': {'location': (33, 104), 'type':  LockboxFieldType.Blank },
    }

    def validate(self):
        self.batch_number = int(self._batch_number_raw)
        self.item_number = int(self._item_number_raw)
        self.deposit_date = self._parse_as_date('deposit_date')
        self.total_number_remittances = int(self._total_number_remittances_raw)
        self.check_dollar_total = int(self._check_dollar_total_raw) / 100.0


class LockboxServiceTotalRecord(LockboxBaseRecord):
    RECORD_TYPE_NUM = 8

    fields = {
        'batch_number': { 'location': (1, 4), 'type':  LockboxFieldType.Numeric },
        'item_number': { 'location': (4, 7), 'type':  LockboxFieldType.Numeric },
        'lockbox_number': { 'location': (7, 14), 'type':  LockboxFieldType.Numeric },
        'deposit_date': { 'location': (14, 20), 'type':  LockboxFieldType.Numeric },
        'total_num_checks': { 'location': (20, 24), 'type':  LockboxFieldType.Numeric },
        'check_dollar_total': { 'location': (24, 34), 'type':  LockboxFieldType.Numeric },
        'filler': {'location': (34, 104), 'type':  LockboxFieldType.Blank },
    }

    def validate(self):
        self.batch_number = int(self._batch_number_raw)
        self.item_number = int(self._item_number_raw)
        self.deposit_date = self._parse_as_date('deposit_date')
        self.total_num_checks = int(self._total_num_checks_raw)
        self.check_dollar_total = int(self._check_dollar_total_raw) / 100.0

class LockboxDestinationTrailerRecord(LockboxBaseRecord):
    RECORD_TYPE_NUM = 9

    fields = {
        'total_num_records': { 'location': (1, 7), 'type':  LockboxFieldType.Numeric },
        'filler': {'location': (7, 104), 'type':  LockboxFieldType.Blank },
    }

    def validate(self):
        self.total_num_records = int(self._total_num_records_raw)
