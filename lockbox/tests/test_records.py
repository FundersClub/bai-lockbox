import datetime

from unittest import TestCase

from lockbox.exceptions import LockboxParseError
from lockbox.records import (
    LockboxBatchTotalRecord,
    LockboxDestinationTrailerRecord,
    LockboxDetailHeader,
    LockboxDetailOverflowRecord,
    LockboxDetailRecord,
    LockboxImmediateAddressHeader,
    LockboxServiceRecord,
    LockboxServiceTotalRecord,
)

class TestRecordDefinitions(TestCase):
    def test_overlong_record(self):
        with self.assertRaises(LockboxParseError) as cm:
            LockboxImmediateAddressHeader(' ' * 161)

        self.assertIn('record longer than 160', str(cm.exception))

    def test_invalid_numeric_field(self):
        with self.assertRaises(LockboxParseError) as cm:
            LockboxImmediateAddressHeader('100ABCDEFGHIJ009AA999911605231800')

        self.assertEqual(
            str(cm.exception),
            'field originating_trn does not match expected type numeric',
        )

    def test_invalid_alphanumeric_field(self):
        with self.assertRaises(LockboxParseError) as cm:
            LockboxImmediateAddressHeader('100A~CDEFGHIJ00999999911605231800')

        self.assertEqual(
            str(cm.exception),
            'field destination_id does not match expected type alphanumeric',
        )

    def test_immediate_address_header(self):
        # test valid record
        rec = LockboxImmediateAddressHeader('100ABCDEFGHIJ00999999911605231800')

        self.assertEqual(rec._priority_code_raw, '00')
        self.assertEqual(rec._destination_id_raw, 'ABCDEFGHIJ')
        self.assertEqual(rec._originating_trn_raw, '0099999991')
        self.assertEqual(rec._processing_date_raw, '160523')
        self.assertEqual(rec._processing_time_raw, '1800')

        self.assertEqual(rec.processing_date, datetime.date(2016, 5, 23))
        self.assertEqual(rec.processing_time, datetime.time(18, 0))

    def test_valid_lockbox_service_record(self):
        rec = LockboxServiceRecord(
            '2ABCDEFGHIJ0099999991000000000040008000801'
        )

        self.assertEqual(
            rec._ultimate_dest_and_origin_raw,
            'ABCDEFGHIJ0099999991',
        )
        self.assertEqual(rec._ref_code_raw, '0000000000')
        self.assertEqual(rec._service_type_raw, '400')
        self.assertEqual(rec._record_size_raw, '080')
        self.assertEqual(rec._blocking_factor_raw, '0080')
        self.assertEqual(rec._format_code_raw, '1')

    def test_lockbox_detail_header(self):
        rec = LockboxDetailHeader('50000000022222160523ABCDEFGHIJ0099999991')

        self.assertEqual(rec._batch_number_raw, '000')
        self.assertEqual(rec._ref_code_raw, '000')
        self.assertEqual(rec._lockbox_number_raw, '0022222')
        self.assertEqual(rec._deposit_date_raw, '160523')
        self.assertEqual(
            rec._ultimate_dest_and_origin_raw,
            'ABCDEFGHIJ0099999991',
        )
        self.assertEqual(rec.deposit_date, datetime.date(2016, 5, 23))

    def test_lockbox_detail_record(self):
        rec = LockboxDetailRecord(
            '6001001000070000005500270700123455550000000180051616BOB E SMITH   '
            '                MY BUSINESS COMPANY'
        )

        self.assertEqual(rec._batch_number_raw, '001')
        self.assertEqual(rec._item_number_raw, '001')
        self.assertEqual(rec._check_amount_raw, '0000700000')
        self.assertEqual(rec._transit_routing_number_raw, '055002707')
        self.assertEqual(rec._dd_account_number_raw, '0012345555')
        self.assertEqual(rec._check_number_raw, '0000000180')
        self.assertEqual(rec._check_date_raw, '051616')
        self.assertEqual(rec._remitter_name_raw,
            'BOB E SMITH                   '
        )
        self.assertEqual(rec._payee_name_raw, 'MY BUSINESS COMPANY')

        self.assertEqual(rec.remitter_name, 'BOB E SMITH')
        self.assertEqual(rec.check_amount, 7000.00)
        self.assertEqual(rec.check_number, 180)
        self.assertEqual(rec.check_date, datetime.date(2016, 5, 16))

    def test_lockbox_detail_overflow_record(self):
        rec = LockboxDetailOverflowRecord('40010016019CE554')

        self.assertEqual(rec._batch_number_raw, '001')
        self.assertEqual(rec._item_number_raw, '001')
        self.assertEqual(rec._overflow_record_type_raw, '6')
        self.assertEqual(rec._overflow_sequence_number_raw, '01')
        self.assertEqual(rec._overflow_indicator_raw, '9')
        self.assertEqual(rec._memo_line_raw, 'CE554')

    def test_lockbox_batch_total_record(self):
        rec = LockboxBatchTotalRecord('700100000222221605230010000700000')

        self.assertEqual(rec._batch_number_raw, '001')
        self.assertEqual(rec._item_number_raw, '000')
        self.assertEqual(rec._lockbox_number_raw, '0022222')
        self.assertEqual(rec._deposit_date_raw, '160523')
        self.assertEqual(rec._total_number_remittances_raw, '001')
        self.assertEqual(rec._check_dollar_total_raw, '0000700000')
        self.assertEqual(rec.check_dollar_total, 7000.00)

    def test_lockbox_service_total_record(self):
        rec = LockboxServiceTotalRecord('8000000002222216052300010000700000')

        self.assertEqual(rec._batch_number_raw, '000')
        self.assertEqual(rec._item_number_raw, '000')
        self.assertEqual(rec._lockbox_number_raw, '0022222')
        self.assertEqual(rec._deposit_date_raw, '160523')
        self.assertEqual(rec._total_num_checks_raw, '0001')
        self.assertEqual(rec._check_dollar_total_raw, '0000700000')

    def test_lockbox_destination_trailer_record(self):
        rec = LockboxDestinationTrailerRecord('9000008')

        self.assertEqual(rec._total_num_records_raw, '000008')

    def test_memo_line_with_valid_nonalpha_char(self):
        rec = LockboxDetailOverflowRecord('40010016019(BLAH:)')

        self.assertEqual(rec._memo_line_raw, '(BLAH:)')
