#!/usr/bin/env python
# coding=utf-8
""" Integration and Unit tests for sshreader Python Package
"""
import os
import sys
import unittest
import warnings

__author__ = 'Jesse Almanrode (jesse@almanrode.com)'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import sshreader

global ssh_data
# Defaults for testing with Docker!
ssh_data = {"host_fqdn": "127.0.0.1", "host_port": os.getenv('SSH_PORT', 22),
            "ssh_user": "sshreader", "ssh_password": "sunshine",
            "ssh_key_path": project_root + "/tests/keys/id_rsa"}


class TestMisc(unittest.TestCase):
    """ Test Cases for miscellaneous functions of SSH module
    """

    def test_env_variables(self):
        """ Test envvars method"""
        ssh_env = sshreader.envvars()
        self.assertIsNotNone(ssh_env.username)
        pass

    def test_shell_command(self):
        """ Test shell_command method
        """
        result = sshreader.shell_command('echo "foo"')
        self.assertEqual(result.return_code, 0)
        self.assertIn('foo', result.stdout)
        self.assertEqual(len(result.stderr), 0)
        pass

    def test_shell_command_combined(self):
        """ Test combining stdout and stderr of shell_command method
        """
        result = sshreader.shell_command('echo "foo"; echo "bar" 1>&2', combine=True)
        self.assertEqual(result.return_code, 0)
        self.assertIn('foo', result.stdout)
        self.assertIn('bar', result.stdout)
        self.assertEqual(result.stderr, None)
        pass

    def test_shell_command_stderr(self):
        """ Test stderr of shell_command method
        """
        result = sshreader.shell_command('echo "bar" 1>&2')
        self.assertEqual(result.return_code, 0)
        self.assertEqual(len(result.stdout), 0)
        self.assertIn('bar', result.stderr)
        pass

    def test_decode_bytes(self):
        """ Test to ensure that result is a unicode string type
        """
        result = sshreader.shell_command('uname -a')
        self.assertEqual(result.return_code, 0)
        self.assertIsInstance(result.stdout, str)
        pass

    def test_bytes(self):
        """ Test to ensure that result is a bytes string type
        """
        result = sshreader.shell_command('uname -a', decode_bytes=False)
        self.assertEqual(result.return_code, 0)
        self.assertIsInstance(result.stdout, bytes)
        result = sshreader.shell_command('uname -a', combine=True, decode_bytes=False)
        self.assertEqual(result.return_code, 0)
        self.assertIsInstance(result.stdout, bytes)
        pass


class TestSSH(unittest.TestCase):
    """ Test cases for the SSH class
    """

    def test_password(self):
        """ Test an SSH connection using a password
        """
        global ssh_data
        with sshreader.SSH(ssh_data['host_fqdn'], port=ssh_data['host_port'], username=ssh_data['ssh_user'],
                           password=ssh_data['ssh_password']) as conn:
            self.assertTrue(conn.alive())
            self.assertEqual(conn.ssh_command('uname').stdout, 'Linux')
        pass

    def test_keyfile(self):
        """ Test an SSH connection using an ssh key
        """
        global ssh_data
        with sshreader.SSH(ssh_data['host_fqdn'], port=ssh_data['host_port'], username=ssh_data['ssh_user'],
                           keyfile=ssh_data['ssh_key_path']) as conn:
            self.assertTrue(conn.alive())
            self.assertEqual(conn.ssh_command('uname').stdout, 'Linux')
        pass

    def test_reconnect(self):
        """ Test re-opening an SSH connection
        """
        global ssh_data
        conn = sshreader.SSH(ssh_data['host_fqdn'], port=ssh_data['host_port'], username=ssh_data['ssh_user'],
                             password=ssh_data['ssh_password'], connect=False)
        self.assertFalse(conn.alive())
        conn.reconnect()
        self.assertTrue(conn.alive())
        conn.close()
        pass

    def test_command(self):
        """ Test commands over ssh
        """
        with sshreader.SSH(ssh_data['host_fqdn'], port=ssh_data['host_port'], username=ssh_data['ssh_user'],
                           password=ssh_data['ssh_password']) as conn:
            cmd = conn.ssh_command('uname')
            self.assertEqual(cmd.stdout, 'Linux')
            self.assertEqual(cmd.stderr, '')
            cmd = conn.ssh_command('uname 1>&2')
            self.assertEqual(cmd.stderr, 'Linux')
            self.assertEqual(cmd.stdout, '')
            cmd = conn.ssh_command('echo foo; echo bar 1>&2;', combine=True)
            self.assertIn('foo', cmd.stdout)
            self.assertIn('bar', cmd.stdout)
            self.assertIsNone(cmd.stderr)
            cmd = conn.ssh_command('sleep 5', timeout=2)
            self.assertEqual(cmd.return_code, 124)
            self.assertIn('command timed out', cmd.stderr)
        pass


def my_hook(*args):
    """ Function for testing hook
    :param args: Args should be ('pre|post', sshreader.ServerJob)
    :return:
    """
    args = list(args)
    if len(args) == 1:
        if args[0] in ('pre', 'post') and isinstance(args.pop(), sshreader.ServerJob):
            return True
        else:
            return False
    else:
        if args[0] in ('pre', 'post'):
            return True
        else:
            return False


class TestSshreader(unittest.TestCase):
    """ Test cases for the sshreader module
    """

    @staticmethod
    def configure_serverjob_list(size):
        """ Configure a list of serverjob objects to sshread (including pre and post hooks) and local commands
        :return: List
        """
        global ssh_data
        pre = sshreader.Hook(my_hook, args=['pre'])
        post = sshreader.Hook(my_hook, args=['post'])
        jobs = list()
        for x in range(size):
            x = sshreader.ServerJob(ssh_data['host_fqdn'], ['sleep 1', 'echo done'], pre_hook=pre, post_hook=post,
                                    username=ssh_data['ssh_user'], password=ssh_data['ssh_password'],
                                    ssh_port=ssh_data['host_port'])
            jobs.append(x)
        for x in range(size):
            jobs.append(sshreader.ServerJob('local-' + str(x), ['sleep 1', 'echo done'], run_local=True))
        return jobs

    def test_Hook_creation(self):
        """ Test valid hook creation
        """
        myhook = sshreader.Hook(my_hook, args=['pre'])
        self.assertIsInstance(myhook, sshreader.Hook)
        pass

    def test_ServerJob(self):
        """ Test valid ServerJob creation
        """
        global ssh_data
        job = sshreader.ServerJob(ssh_data['host_fqdn'], 'echo foo', ssh_port=ssh_data['host_port'],
                                  username=ssh_data['ssh_user'], password=ssh_data['ssh_password'])
        self.assertIsInstance(job, sshreader.ServerJob)
        pass

    def test_ServerJob_with_hooks(self):
        """ Test ServerJob with hooks
        """
        global ssh_data
        pre = sshreader.Hook(my_hook, args=['pre'])
        post = sshreader.Hook(my_hook, args=['post'])
        job = sshreader.ServerJob(ssh_data['host_fqdn'], 'echo foo', pre_hook=pre, post_hook=post,
                                  username=ssh_data['ssh_user'], password=ssh_data['ssh_password'],
                                  ssh_port=ssh_data['host_port'])
        self.assertIsInstance(job, sshreader.ServerJob)
        pass

    def test_sshread_threads(self):
        """ Test sshread method using threads
        """
        jobs = self.configure_serverjob_list(1)
        result = sshreader.sshread(jobs, tcount=0)
        for x in result:
            self.assertEqual(x.status, 0, msg=x.results)
        pass

    def test_sshread_processes(self):
        """ Test sshread method using processes
        """
        jobs = self.configure_serverjob_list(1)
        result = sshreader.sshread(jobs, pcount=0)
        for x in result:
            self.assertEqual(x.status, 0, msg=x.results)
        pass

    def test_sshread(self):
        """ Test sshread method using threads and processes
        """
        jobs = self.configure_serverjob_list(1)
        result = sshreader.sshread(jobs, pcount=0, tcount=0)
        for x in result:
            self.assertEqual(x.status, 0, msg=x.results)
        pass

    def test_cpu_limit(self):
        """ Ensure the cpu_limit methods
        """
        self.assertIsInstance(sshreader.utils.cpu_limit(), int)
        self.assertIsInstance(sshreader.utils.cpu_limit(2), int)
        pass


if __name__ == '__main__':
    with warnings.catch_warnings(record=True):
        unittest.main()
