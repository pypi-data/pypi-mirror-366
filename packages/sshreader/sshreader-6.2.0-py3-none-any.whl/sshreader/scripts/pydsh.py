""" A Pythonic implementation of pdsh powered by sshreader
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
import sys
from collections import defaultdict
from hashlib import md5

import click
from hostlist import collect_hostlist, expand_hostlist

import sshreader

# GLOBALS
__author__ = 'Jesse Almanrode'
__version__ = '3.2.0'
__examples__ = """\b
Examples:
    pydsh -w host1,host2,host3 "uname -r"
    pydsh -u root -k /root/.ssh/id_rsa -w host[1,3] "uname -r"
    pydsh -u root -P Password123 -w host[1-3] "uname -r"
    pydsh -F -w host[01-10] myscript.sh
"""

log = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter('%(levelname)s:%(funcName)s:%(message)s'))
log.addHandler(log_handler)
log.setLevel(logging.WARNING)
log.propagate = False  # Keeps our messages out of the root logger.


def copy_script(scriptfile, job):
    """ Copy script to remote host using SFTP connection

    :param scriptfile: Path to script file
    :param job: <ServerJob> object
    :return: True on file copy
    """
    script_name = os.path.split(scriptfile)[1]
    try:
        job._conn.sftp_put(scriptfile, '/tmp/' + script_name)
    except Exception as err:
        return err


def output(thisjob):
    """ Print output from jobs as they complete in a format that could be piped to dshbak

    :param thisjob: <ServerJob> object
    :return: None
    """
    result = thisjob.results[0] if thisjob.status == 255 else thisjob.results[0].stdout
    if len(result) != 0:
        for line in result.split('\n'):
            sshreader.echo(str(thisjob.name) + ': ' + str(line))
    return None


def dshbak(jobresults):
    """ Output the results of the jobs grouped by hosts

    Similar to piping output to `dshbak`

    :param jobresults: List of <ServerJob> objects
    :return: None
    """
    for thisjob in jobresults:
        if thisjob.status == 255:
            result = thisjob.results[0]
        else:
            result = thisjob.results[0].stdout
        if len(result) != 0:
            click.echo(str('-' * 16) + '\n' + str(thisjob.name) + '\n' + str('-' * 16))
            click.echo(result)
    return None


def coalesce(jobresults):
    """ Output the results of jobs coalescing identical output from hosts

    Similar to piping output to `dshbak -c`

    :param jobresults: List of <ServerJob> objects
    :return: None
    """
    job_hashes = defaultdict(list)
    output_hashes = dict()
    for job in jobresults:
        result = job.results[0] if job.status == 255 else job.results[0].stdout
        md5sum = md5(result.encode()).hexdigest()
        job_hashes[md5sum].append(job.name)
        if md5sum not in output_hashes:
            output_hashes[md5sum] = result

    for md5sum, stdout in output_hashes.items():
        if len(stdout) != 0:
            click.echo(str('-' * 16) + '\n' + collect_hostlist(job_hashes[md5sum]) + '\n' + str('-' * 16))
            click.echo(stdout)
    return None


def validate_hostlist(ctx, param, value):
    """ Callback for click to expand hostlist expressions or error

    :param ctx: Click context
    :param param: Parameter Name
    :param value: Hostlist expression to expand
    :return: List of expanded hosts
    """
    try:
        return expand_hostlist(value)
    except Exception:
        raise click.BadOptionUsage(param, 'Invalid hostlist expression') from None


@click.command(epilog=__examples__)
@click.version_option(version=__version__)
@click.option('--hostlist', '-w', metavar='EXPR', required=True, callback=validate_hostlist,
              help='Hostlist expression')
@click.option('--username', '-u', help='Override ssh username')
@click.option('--keyfile', '-k', type=click.Path(exists=True, dir_okay=False), help='Private key file')
@click.option('--keypass', '-K', is_flag=True, help='Prompt for private key password')
@click.option('--prompt', '-p', is_flag=True, help='Prompt for ssh password')
@click.option('--password', '-P', help='Supply ssh password')
@click.option('--dshbak', '-D', is_flag=True, help='Group output by host')
@click.option('--coalesce', '-C', is_flag=True, help='Coalesce similar output from hosts')
@click.option('--file', '-F', is_flag=True, help='Treat CMD as a script file')
@click.option('--debug', '-d', is_flag=True, help='Enable debug output')
@click.option('--verbose', '-v', count=True, help='Increase debug verbosity')
@click.option('--redline', is_flag=True, help='Run pydsh faster')
@click.option('--port', default=22, help='SSH Port')
@click.option('--sha2', is_flag=True, default=True, help='Use SHA2 Hash Algorithm for Keys')
@click.argument('cmd', nargs=1)
def cli(**kwargs):
    """  Run ssh commands in parallel across hosts
    """
    if kwargs['debug']:
        log.setLevel(logging.INFO)
        if kwargs['verbose']:
            logging.getLogger('sshreader').setLevel(logging.INFO)
        if kwargs['verbose'] > 1:
            log.setLevel(logging.DEBUG)
        if kwargs['verbose'] > 2:
            logging.getLogger('sshreader').setLevel(logging.DEBUG)
    log.debug(kwargs)
    if kwargs['file']:
        mkpath = click.Path(exists=True, dir_okay=False)
        script_path = mkpath(kwargs['cmd'])
        script_name = os.path.split(script_path)[1]
        log.info('Creating copy_script prehook for: ' + script_name)
        prehook = sshreader.Hook(copy_script, args=[script_path], ssh_established=True)
        with open(script_path) as s:
            script = s.readline()
        if script.startswith('#!') is False:
            raise click.UsageError('Script must start with #!')
        kwargs['cmd'] = [script.split('#!').pop().strip() + ' /tmp/' + script_name, 'rm /tmp/' + script_name]
    sshenv = sshreader.envvars()
    log.debug(sshenv)

    if kwargs['port'] <= 0 or not isinstance(kwargs['port'], int):
        raise click.BadOptionUsage('port', 'Please enter a positive integer')

    if kwargs['username'] is None:
        if sshenv.username is None:
            raise click.ClickException('Unable to determine ssh username. Please provide one using --username')
        else:
            kwargs['username'] = sshenv.username

    # By default, we prefer ssh keys
    if not kwargs['keyfile']:
        log.info('SSH keyfile not specified, searching for one anyways')
        if any((sshenv.rsa_key, sshenv.dsa_key, sshenv.ecdsa_key)):
            if sshenv.ecdsa_key:
                kwargs['keyfile'] = sshenv.ecdsa_key
                log.info('Using ECDSA private key file')
            elif sshenv.rsa_key:
                kwargs['keyfile'] = sshenv.rsa_key
                log.info('Using RSA private key file')
            else:
                kwargs['keyfile'] = sshenv.dsa_key
                log.info('Using DSA private key file')
        else:
            if len(sshenv.agent_keys) == 0:
                if not all((kwargs['username'], kwargs['password'])):
                    raise click.ClickException('Unable to find ssh key to use and password not supplied.')
            else:
                log.info('Falling back to SSH Agent')
            if kwargs['keypass']:
                kwargs['keypass'] = click.prompt('Private Key Password', hide_input=True)
    else:
        log.info('SSH keyfile provided disabling password authentication')
        # If you specify an SSH key then we ignore any password or prompt flags you might have entered
        kwargs['password'] = None
        kwargs['prompt'] = False
        if kwargs['keypass']:
            kwargs['keypass'] = click.prompt('Private Key Password', hide_input=True)

    # If you specify a password or prompt for one it overrides the ssh key
    if not kwargs['password']:
        if not kwargs['prompt']:
            if not kwargs['keyfile'] and len(sshenv.agent_keys) == 0:
                raise click.ClickException('Unable to find ssh key to use and password not supplied or prompt enabled.')
        else:
            log.info('Prompting for password and disabling discovered SSH keyfiles')
            kwargs['keyfile'] = None
            while kwargs['password'] is None:
                kwargs['password'] = click.prompt(kwargs['username'] + "'s Password", hide_input=True)
    else:
        log.info('Using password authentication and disabling discovered SSH keyfiles')
        # You provided a password, ignore the SSH key
        kwargs['keyfile'] = None

    log.debug(kwargs)
    posthook = sshreader.Hook(target=output)
    jobs = list()
    for host in kwargs['hostlist']:
        if ':' in host:
            log.info('SSH Port declared in host: ' + host)
            host, port = host.split(':')
            log.debug((host, port))
        else:
            port = kwargs['port']
        if kwargs['keyfile']:
            job = sshreader.ServerJob(host, kwargs['cmd'], username=kwargs['username'], keyfile=kwargs['keyfile'],
                                      key_pass=kwargs['keypass'], combine_output=True, rsa_sha2=kwargs['sha2'])
        else:
            job = sshreader.ServerJob(host, kwargs['cmd'], username=kwargs['username'], password=kwargs['password'],
                                      combine_output=True, rsa_sha2=kwargs['sha2'])
        job.ssh_port = port
        if kwargs['dshbak'] is False and kwargs['coalesce'] is False:
            log.info('Adding posthook to ServerJob for: ' + host)
            job.post_hook = posthook
        if kwargs['file']:
            log.info('Adding prehook to ServerJob for: ' + host)
            job.pre_hook = prehook
        jobs.append(job)

    log.info(f'Sending {len(jobs)} ServerJobs to sshreader module')
    if kwargs['dshbak'] is False and kwargs['coalesce'] is False:
        if kwargs['redline']:
            sshreader.sshread(jobs, pcount=0, tcount=0, print_lock=True)
        else:
            sshreader.sshread(jobs, tcount=0, print_lock=True)
    else:
        if kwargs['redline']:
            jobs_finished = sshreader.sshread(jobs, pcount=0, tcount=0, progress_bar=True)
        else:
            jobs_finished = sshreader.sshread(jobs, tcount=0, progress_bar=True)
        if kwargs['coalesce']:
            coalesce(jobs_finished)
        else:
            dshbak(jobs_finished)
    sys.exit(0)


if __name__ == "__main__":
    print('Please install pydsh by running: pip install sshreader')
    sys.exit(1)
