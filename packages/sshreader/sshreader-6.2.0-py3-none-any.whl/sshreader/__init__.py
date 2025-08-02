"""A Python Package for parallelizing ssh connections via threading and multiprocessing.
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

# For backwards compatibility
import logging

from .customtypes import Command, EnvVars, Timeout, TimeoutTuple
from .ssh import SSH, envvars
from .utils import Hook, ServerJob, cpu_limit, echo, shell_command, sshread

__author__ = 'Jesse Almanrode (jesse@almanrode.com)'
__all__ = ['ssh', 'customtypes', 'utils']

log = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s.%(module)s.%(funcName)s:%(message)s'))
log.addHandler(log_handler)
log.setLevel(logging.WARNING)
log.propagate = False  # Keeps our messages out of the root logger.
