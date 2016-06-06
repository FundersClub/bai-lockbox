import datetime
import os

from unittest import TestCase

from lockbox.parser import LockboxFile


class TestLockboxParser(TestCase):
    def setUp(self):
        valid_lockbox_path = os.path.join(
            os.getcwd(),
            'lockbox',
            'tests',
            'test_lockbox.bai',
        )

        empty_lockbox_path = os.path.join(
            os.getcwd(),
            'lockbox',
            'tests',
            'test_empty_lockbox.bai',
        )

        self.valid_lockbox_lines = [l.strip() for l in open(valid_lockbox_path, 'r').readlines()]
        self.empty_lockbox_lines = [l.strip() for l in open(empty_lockbox_path, 'r').readlines()]

    def test_parsing_valid_file(self):
        lockbox_file = LockboxFile.from_lines(self.valid_lockbox_lines)

        self.assertEqual(len(lockbox_file.checks), 1)

        check = lockbox_file.checks[0]
        self.assertEqual(check.sender, 'BOB E SMITH')
        self.assertEqual(check.recipient, 'MY BUSINESS COMPANY')
        self.assertEqual(check.date, datetime.date(2016, 5, 16))
        self.assertEqual(check.number, 180)
        self.assertEqual(check.amount, 7000.0)
        self.assertEqual(check.memo, 'CE554')

    def test_parsing_file_with_no_checks(self):
        lockbox_file = LockboxFile.from_lines(self.empty_lockbox_lines)

        self.assertEqual(len(lockbox_file.checks), 0)
