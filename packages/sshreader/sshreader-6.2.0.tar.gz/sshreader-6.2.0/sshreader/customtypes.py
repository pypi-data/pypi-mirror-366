""" Typing module for sshreader
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
from typing import NamedTuple, Optional, Union


class Command(NamedTuple):
    cmd: str
    stdout: Optional[Union[str, bytes]]
    stderr: Optional[Union[str, bytes]]
    return_code: int


class EnvVars(NamedTuple):
    username: Optional[str]
    agent_keys: Optional[list]
    dsa_key: Optional[str]
    ecdsa_key: Optional[str]
    rsa_key: Optional[str]


Timeout = Union[int, float]
TimeoutTuple = tuple[Timeout, Timeout]
