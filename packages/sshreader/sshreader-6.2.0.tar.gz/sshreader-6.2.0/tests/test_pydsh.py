#!/usr/bin/env python
# coding=utf-8
""" Integration and Unit tests for pydsh script
"""
import os
import sys
import unittest
import warnings
from click.testing import CliRunner

__author__ = 'Jesse Almanrode (jesse@almanrode.com)'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import sshreader.scripts.pydsh as pydsh

global ssh_data
# Defaults for testing with Docker!
ssh_data = {"host_fqdn": "127.0.0.1", "host_port": os.getenv('SSH_PORT', 22),
            "ssh_user": "sshreader", "ssh_password": "sunshine",
            "ssh_key_path": project_root + "/tests/keys/id_rsa"}


class TestPydsh(unittest.TestCase):
    """ Test cases for the pydsh cli
    """

    def setUp(self) -> None:
        self.cli = CliRunner()

    def test_help(self):
        self.assertEqual(self.cli.invoke(pydsh.cli, ['--help']).exit_code, 0)
        pass

    def test_password_auth(self):
        global ssh_data
        cli_result = self.cli.invoke(pydsh.cli, ['-w', ssh_data['host_fqdn'], '--port', ssh_data['host_port'],
                                                 '-u', ssh_data['ssh_user'], '-P', ssh_data['ssh_password'],
                                                 'uname'])
        self.assertIn('Linux', cli_result.stdout)
        self.assertEqual(cli_result.exit_code, 0)
        pass

    def test_keyfile_auth(self):
        global ssh_data
        cli_result = self.cli.invoke(pydsh.cli, ['-w', ssh_data['host_fqdn'], '--port', ssh_data['host_port'],
                                                 '-u', ssh_data['ssh_user'], '-k', ssh_data['ssh_key_path'],
                                                 'uname'])
        self.assertIn('Linux', cli_result.stdout)
        self.assertEqual(cli_result.exit_code, 0)
        pass

    def test_hostlist_port(self):
        global ssh_data
        host_port = ssh_data['host_fqdn'] + ':' + str(ssh_data['host_port'])
        cli_result = self.cli.invoke(pydsh.cli, ['-w', host_port,
                                                 '-u', ssh_data['ssh_user'], '-k', ssh_data['ssh_key_path'],
                                                 'uname'])
        self.assertIn('Linux', cli_result.stdout)
        self.assertEqual(cli_result.exit_code, 0)
        pass

    def test_dshbak_output(self):
        global ssh_data
        cli_result = self.cli.invoke(pydsh.cli, ['-w', ssh_data['host_fqdn'], '--port', ssh_data['host_port'],
                                                 '-u', ssh_data['ssh_user'], '-k', ssh_data['ssh_key_path'],
                                                 '-D', 'uname'])
        self.assertIn('Linux', cli_result.stdout)
        self.assertEqual(cli_result.exit_code, 0)
        pass

    def test_coalesce_output(self):
        global ssh_data
        cli_result = self.cli.invoke(pydsh.cli, ['-w', ssh_data['host_fqdn'], '--port', ssh_data['host_port'],
                                                 '-u', ssh_data['ssh_user'], '-k', ssh_data['ssh_key_path'],
                                                 '-C', 'uname'])
        self.assertIn('Linux', cli_result.stdout)
        self.assertEqual(cli_result.exit_code, 0)
        pass


if __name__ == '__main__':
    with warnings.catch_warnings(record=True):
        unittest.main()
