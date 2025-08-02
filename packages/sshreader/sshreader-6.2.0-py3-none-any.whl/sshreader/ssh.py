"""A wrapper for Paramiko that attempts to make ssh sessions easier to work with.
"""
# Copyright (C) 2015-2025 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
import os
import socket
from getpass import getuser
from typing import Any, Optional

import paramiko

from .customtypes import Command, EnvVars, Timeout

log = logging.getLogger('sshreader')


def envvars() -> EnvVars:
    """ Attempt to determine the current username and location of any ssh private keys.
    If any value is unable to be determined it is returned as 'None'.

    This method also checks for any private keys loaded into the SSH Agent.

    :return: NamedTuple of (username, agent_keys, rsa_key, dsa_key, ecdsa_key)
    :rtype: :class:`typing.NamedTuple`
    """
    global log
    env = {'username': None, 'rsa_key': None, 'dsa_key': None, 'ecdsa_key': None, 'agent_keys': None}
    user_home = os.getenv('HOME', '~')
    if user_home == '~':
        user_home = os.path.expanduser('~')
    try:
        env['username'] = getuser()
    except OSError:  # Running in a container or inside an IDE, let's take our best guess based on your $HOME
        env['username'] = user_home.split('/').pop()
    if os.path.exists(user_home + "/.ssh"):
        keyfiles = os.listdir(user_home + "/.ssh")
        if "id_rsa" in keyfiles:
            env['rsa_key'] = user_home + "/.ssh/id_rsa"
        if "id_dsa" in keyfiles:
            env['dsa_key'] = user_home + "/.ssh/id_dsa"
        if 'id_ecdsa' in keyfiles:
            env['ecdsa_key'] = user_home + '/.ssh/id_ecdsa'
    env['agent_keys'] = paramiko.Agent().get_keys()
    return EnvVars(**env)


class SSH:
    """SSH Session class which can be used to send commands to a remote server.  It also supports basic SFTP commands
    and can be used to push/pull files from a remote system.

    :param fqdn: Fully qualified domain name or IP address
    :type fqdn: str, required
    :param username: SSH username
    :type username: str, required
    :param password: SSH password
    :type password: str, optional
    :param keyfile: Path to SSH Private Key File
    :type keyfile: str, optional
    :param keypass: SSH private key password
    :type keypass: str, optional
    :param port: SSH port (Default: 22)
    :type port: int, optional
    :param connect: Initiate ssh connection on object initialization (Default: True)
    :type connect: bool, optional
    :param rsa_sha2: Enable/Disable RSA w/SHA2 hashes (Default: True)
    :type rsa_sha2: bool, optional
    :raises: :class:`paramiko.SSHException`
    """
    def __init__(self, fqdn: str, username: str, password: Optional[str] = None, keyfile: Optional[str] = None,
                 keypass: Optional[str] = None, port: int = 22, connect: bool = True, rsa_sha2: bool = True) -> None:
        if not keyfile and len(paramiko.Agent().get_keys()) == 0 and not all((username, password)):
            paramiko.SSHException('username and password or keyfile not provided')
        self.host = fqdn
        self.username = username
        self.password = password
        if keyfile:
            if not isinstance(keyfile, str):
                raise TypeError(f'expected {str(str)} for keyfile, got {str(type(keyfile))}')
            self.keyfile = os.path.abspath(os.path.expanduser(keyfile))
        else:
            self.keyfile = keyfile
        self.rsa_sha2 = rsa_sha2
        self.keypass = keypass
        self.port = port
        self._connection = paramiko.SSHClient()
        self._connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if connect:
            self.__connect()

    def __str__(self) -> str:
        return str(self.__dict__)

    def __enter__(self):
        if self.__alive() is False:
            self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__close()

    def sftp_put(self, srcfile: str, dstfile: str) -> Any:
        """ Use the SFTP subsystem of OpenSSH to copy a local file to a remote host

        :param srcfile: Path to the local file
        :type srcfile: str, required
        :param dstfile: Path to the remote file
        :type dstfile: str, required
        :return: Result of :meth:`paramiko.SFTPClient.put()`
        """
        if not self.__alive():
            raise paramiko.SSHException(f"connection to {self.host} not established")
        sftp = paramiko.SFTPClient.from_transport(self._connection.get_transport())
        try:
            result = sftp.put(os.path.expanduser(srcfile), os.path.expanduser(dstfile))
        finally:
            sftp.close()
        return result

    def sftp_get(self, srcfile: str, dstfile: str) -> None:
        """ Use the SFTP subsystem of OpenSSH to copy a remote file to the localhost

        :param srcfile: Path to the remote file
        :type srcfile: str, required
        :param dstfile: Path to the local file
        :type dstfile: str, required
        :return: None
        """
        if not self.__alive():
            raise paramiko.SSHException(f"connection to {self.host} not established")
        sftp = paramiko.SFTPClient.from_transport(self._connection.get_transport())
        try:
            sftp.get(os.path.expanduser(srcfile), os.path.expanduser(dstfile))
        finally:
            sftp.close()

    def ssh_command(self, command: str, timeout: Timeout = 30, combine: bool = False,
                    decodebytes: bool = True) -> Command:
        """Run a command over an ssh connection

        :param command: The command to run
        :type command: str, required
        :param timeout: Timeout for blocking commands in seconds (Default: 30)
        :type timeout: int or float, optional
        :param combine: Combine stderr and stdout using a pseudo TTY (Default: False)
        :type combine: bool, optional
        :param decodebytes: Decode bytes objects to unicode strings in Python3 (Default: True)
        :type decodebytes: bool, optional
        :return: Namedtuple of (cmd, stdout, stderr, return_code) or (cmd, stdout, return_code)
        :rtype: Command
        :raises: :class:`paramiko.SSHException`
        """
        if self.__alive() is False:
            raise paramiko.SSHException(f"connection to {self.host} not established")
        if combine:
            try:
                stdin, stdout, stderr = self._connection.exec_command(command, timeout=timeout, get_pty=True)
                if decodebytes:
                    result = Command(cmd=command, stdout=stdout.read().decode().strip(), stderr=None,
                                     return_code=stdout.channel.recv_exit_status())
                else:
                    result = Command(cmd=command, stdout=stdout.read().strip(), stderr=None,
                                     return_code=stdout.channel.recv_exit_status())
            except (paramiko.buffered_pipe.PipeTimeout, socket.timeout):
                result = Command(cmd=command, stdout='command timed out', stderr=None, return_code=124)
        else:
            try:
                stdin, stdout, stderr = self._connection.exec_command(command, timeout=timeout)
                if decodebytes:
                    result = Command(cmd=command, stdout=stdout.read().decode().strip(),
                                     stderr=stderr.read().decode().strip(), return_code=stdout.channel.recv_exit_status())
                else:
                    result = Command(cmd=command, stdout=stdout.read().strip(), stderr=stderr.read().strip(),
                                     return_code=stdout.channel.recv_exit_status())
            except (paramiko.buffered_pipe.PipeTimeout, socket.timeout):
                result = Command(cmd=command, stdout='', stderr='command timed out', return_code=124)
        return result

    def close(self):
        """Closes an established ssh connection

        :return: None
        """
        return self._connection.close()

    def alive(self):
        """Is an SSH connection alive

        :return: True or False
        :rtype: bool
        :raises: :class:`paramiko.SSHException`
        """
        if self._connection.get_transport() is None:
            return False
        else:
            if self._connection.get_transport().is_alive():
                return True
            else:
                raise paramiko.SSHException("unable to determine state of ssh connection")

    def reconnect(self):
        """Alias to connect
        """
        return self.__connect()

    def connect(self, timeout: Timeout = 0.5) -> bool:
        """Opens an SSH Connection

        :param timeout: TCP Timeout in seconds (Default: 0.5)
        :type timeout: int or float, optional
        :return: True
        :rtype: bool
        :raises: :class:`paramiko.SSHException`
        """
        if self.__alive():
            raise paramiko.SSHException(f"connection to {self.host} already established")
        paramiko.util.logging.getLogger().setLevel(logging.CRITICAL)  # Keeping paramiko from logging errors to stdout
        if not self.keyfile and len(paramiko.Agent().get_keys()) == 0 and not all((self.username, self.password)):
            paramiko.SSHException('username and password or keyfile not provided')
        if self.keyfile:
            if self.rsa_sha2:
                self._connection.connect(self.host, port=self.port, username=self.username, password=self.keypass,
                                         key_filename=self.keyfile, timeout=timeout, look_for_keys=False)
            else:
                # While this is more insecure, it is required for pre-OpenSSH 8.8 servers
                # For more info, visit: https://www.paramiko.org/changelog.html#2.9.0
                self._connection.connect(self.host, port=self.port, username=self.username, password=self.keypass,
                                         key_filename=self.keyfile, timeout=timeout, look_for_keys=False,
                                         disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
        else:
            self._connection.connect(self.host, port=self.port, username=self.username, password=self.password,
                                     timeout=timeout, look_for_keys=False)
        return True

    # Privatizing some functions so SSH can be subclassed
    __alive = alive
    __connect = connect
    __close = close
