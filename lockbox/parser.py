# This file is part of bai-lockbox.

# bai-lockbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# bai-lockbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with bai-lockbox.  If not, see
# <http://www.gnu.org/licenses/>.

import six
import sys

from .exceptions import (
    LockboxConsistencyError,
    LockboxError,
    LockboxParseError,
)

from .records import (
    LockboxBatchTotalRecord,
    LockboxDestinationTrailerRecord,
    LockboxDetailHeader,
    LockboxDetailOverflowRecord,
    LockboxDetailRecord,
    LockboxImmediateAddressHeader,
    LockboxServiceRecord,
    LockboxServiceTotalRecord,
)

class Check(object):
    def __init__(self, detail):
        self.sender = detail.remitter_name
        self.recipient = detail.payee_name
        self.date = detail.check_date
        self.number = detail.check_number
        self.amount = detail.check_amount
        self.memo = detail.memo
        self.sender_routing_number=detail.transit_routing_number
        self.sender_account_number=detail.dd_account_number


class LockboxDetail(object):
    def __init__(self):
        self.record = None
        self.overflow_records = []

    @property
    def memo(self):
        return ''.join(o.memo_line for o in self.overflow_records)

    def add_record(self, record):
        if isinstance(record, LockboxDetailRecord):
            self.record = record
        elif isinstance(record, LockboxDetailOverflowRecord):
            self.overflow_records.append(record)
        else:
            raise LockboxParseError(
                'expected lockbox detail overflow record'
            )

    def __getattr__(self, attr):
        if attr in dir(self.record):
            return getattr(self.record, attr)
        else:
            return super(LockboxDetail, self).__getattr__(attr)


class LockboxBatch(object):
    def __init__(self):
        self.details = []
        self.cur_detail = None
        self.summary = None

    @property
    def checks(self):
        return [Check(d) for d in self.details]

    def validate(self):
        if self.summary is None:
            raise LockboxParseError(
                'batch summary record expected'
            )

        checks_sum = sum(d.check_amount for d in self.details)
        if checks_sum != self.summary.check_dollar_total:
            raise LockboxConsistencyError(
                'batch expected dollar total ({}) does not match actual total'
                ' ({})'.format(
                    checks_sum,
                    self.summary.check_dollar_total,
                )
            )

        if len(self.details) != self.summary.total_number_remittances:
            raise LockboxConsistencyError(
                'batch expected number of remittances ({}) does not match'
                ' actual number of remittances ({})'.format(
                    len(self.details),
                    self.summary.total_number_remittances,
                )
            )

    def add_record(self, record):
        if isinstance(record, LockboxDetailRecord):
            if self.cur_detail is not None:
                self.details.append(self.cur_detail)

            self.cur_detail = LockboxDetail()
            self.cur_detail.record = record
        elif isinstance(record, LockboxBatchTotalRecord):
            if self.summary is not None:
                raise LockboxParseError(
                    'unexpected additional lockbox batch total record found'
                )

            self.summary = record

            if self.cur_detail is not None:
                self.details.append(self.cur_detail)

            self.cur_detail = LockboxDetail()
        else:
            self.cur_detail.add_record(record)


class Lockbox(object):
    def __init__(self):
        self.header_record = None
        self.total_record = None

        self.batches = []
        self.cur_batch = LockboxBatch()

    @property
    def checks(self):
        checks = []

        for batch in self.batches:
            checks.extend(batch.checks)

        return checks

    def validate(self):
        if self.total_record is None:
            raise LockboxConsistencyError('missing service total record')

        if self.header_record is None:
            raise LockboxConsistencyError('missing lockbox detail header')

        for batch in self.batches:
            batch.validate()

        num_remittances = sum(
            batch.summary.total_number_remittances
            for batch
            in self.batches
        )
        dollar_total = sum(
            batch.summary.check_dollar_total
            for batch
            in self.batches
        )

        if self.total_record.total_num_checks != num_remittances:
            raise LockboxConsistencyError(
                'expected number of checks for lockbox {} does not match actual'
                ' number'.format(self.total_record.lockbox_number)
            )

        if self.total_record.check_dollar_total != dollar_total:
            raise LockboxConsistencyError(
                'expected dollar total for lockbox {} does not match actual'
                ' total'.format(self.total_record.lockbox_number)
            )

    def add_record(self, record):
        if isinstance(record, LockboxBatchTotalRecord):
            self.cur_batch.add_record(record)
            self.cur_batch.validate()
            self.batches.append(self.cur_batch)
            self.cur_batch = LockboxBatch()
        else:
            self.cur_batch.add_record(record)


class LockboxFile(object):
    def __init__(self):
        self.lockboxes = []
        self.header_record = None
        self.service_record = None
        self.destination_trailer_record = None

        self.cur_lockbox = None

    @property
    def checks(self):
        checks = []

        for lockbox in self.lockboxes:
            checks.extend(lockbox.checks)

        return checks

    def validate(self):
        for lockbox in self.lockboxes:
            lockbox.validate()

    def add_record(self, record):
        if isinstance(record, LockboxImmediateAddressHeader):
            if self.header_record is not None:
                raise LockboxParseError(
                    'only one immediate address header per file'
                )

            self.header_record = record
        elif isinstance(record, LockboxServiceRecord):
            if self.header_record is None:
                raise LockboxParseError('expected immediate address header')

            if self.service_record is not None:
                raise LockboxParseError('only one service record per file')

            self.service_record = record
        elif isinstance(record, LockboxDetailHeader):
            if self.service_record is None:
                raise LockboxParseError('expected service record')

            if self.cur_lockbox is not None:
                raise LockboxParseError(
                    'cannot have lockbox detail header before closing the '
                    'current one'
                )

            self.cur_lockbox = Lockbox()
            self.cur_lockbox.header_record = record
        elif isinstance(record, LockboxServiceTotalRecord):
            if self.cur_lockbox is None:
                raise LockboxParseError('expected lockbox detail header')

            self.cur_lockbox.total_record = record
            self.lockboxes.append(self.cur_lockbox)
            self.cur_lockbox = None

        elif isinstance(record, LockboxDestinationTrailerRecord):
            if self.cur_lockbox is not None:
                raise LockboxParseError('expected batch total record')

            if self.destination_trailer_record is not None:
                raise LockboxParseError('unexpected destination trailer')

            self.destination_trailer_record = record
        else:
            self.cur_lockbox.add_record(record)

    @classmethod
    def from_lines(cls, lines):
        lines = [l.strip() for l in lines]
        lockbox_file = cls()

        for line_num, line in enumerate(lines, start=1):
            try:
                rec_type = int(line[0])
                record_type_to_constructor = {
                    LockboxBatchTotalRecord.RECORD_TYPE_NUM: LockboxBatchTotalRecord,
                    LockboxDestinationTrailerRecord.RECORD_TYPE_NUM: LockboxDestinationTrailerRecord,
                    LockboxDetailHeader.RECORD_TYPE_NUM: LockboxDetailHeader,
                    LockboxDetailOverflowRecord.RECORD_TYPE_NUM: LockboxDetailOverflowRecord,
                    LockboxDetailRecord.RECORD_TYPE_NUM: LockboxDetailRecord,
                    LockboxImmediateAddressHeader.RECORD_TYPE_NUM: LockboxImmediateAddressHeader,
                    LockboxServiceRecord.RECORD_TYPE_NUM: LockboxServiceRecord,
                    LockboxServiceTotalRecord.RECORD_TYPE_NUM: LockboxServiceTotalRecord,
                }

                if rec_type not in record_type_to_constructor:
                    raise LockboxParseError(
                        'unknown record type {}'.format(rec_type)
                    )

                rec = record_type_to_constructor[rec_type](line)
                lockbox_file.add_record(rec)
            except Exception as e:
                if not isinstance(e, LockboxError):
                    raise

                # if this is some lockbox-related exception,create a new
                # exception of the same kind we caught, bet prepend the
                # current line number to it so we know where to look while
                # troubleshooting
                six.reraise(
                    type(e),
                    'Line {}: {} ("{}")'.format(line_num, str(e), line),
                    sys.exc_info()[2]
                )

        lockbox_file.validate()
        return lockbox_file

    @classmethod
    def from_file(cls, inf):
        return LockboxFile.from_lines(inf.readlines())
