![logo](./logo.png)

A Python Module for multiprocessing/threading ssh connections in order to make ssh operations
across multiple servers parallel.  It utilizes the [Paramiko](http://www.paramiko.org/) module 
for its ssh client.

In order to maintain the widest range of compatibility, [SSHreader][] is currently tested 
using [all supported versions of Python!](https://devguide.python.org/versions/)

## License

[SSHreader][] is released under [GNU Lesser General Public License v3.0][],
see the file LICENSE and LICENSE.lesser for the license text.

## Installation

The most straightforward way to get the [SSHreader][] module working for you is:

```commandline
pip install sshreader
```
or, if you'd like to use a local install from the repo:
```commandline
make install
```

This ensures that all the requirements are met.

## Documentation

The documentation for [SSHreader][] can be found at [ReadTheDocs.](https://sshreader.readthedocs.io)

## Contributing

Comments and enhancements are very welcome.

Report any issues or feature requests on the [BitBucket bug
tracker](https://bitbucket.org/isaiah1112/sshreader/issues?status=new&status=open). Please include a minimal
not-working example which reproduces the bug and, if appropriate, the
traceback information.  Please do not request features already being worked
towards.

Code contributions are encouraged: please feel free to [fork the
project](https://bitbucket.org/isaiah1112/sshreader) and submit pull requests to the develop branch.

## Extras

Included with sshreader is a script called `pydsh`.  This works very similar to [pdsh](https://computing.llnl.gov/linux/pdsh.html) 
but uses sshreader at its core to perform ssh commands in parallel and return the results.  
The output of `pydsh` can also be piped through the `dshbak` tool that comes with pdsh.

Pydsh uses [hostlist expressions](https://www.nsc.liu.se/~kent/python-hostlist/) to get its list of hosts
to process.


[GNU Lesser General Public License v3.0]: http://choosealicense.com/licenses/lgpl-3.0/ "LGPL v3"

[sshreader]: https://bitbucket.org/isaiah1112/sshreader "SSHreader Package"
