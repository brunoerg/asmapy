# asmapy
Asmap stuff for Bitcoin Core

CLI to convert dump files to human-readable dumps, compare two files, download dumps and other stuff.

### Installing and running

```sh
$ pip install -r requirements.txt
```

```sh
$ ./asmapy-cli.py -h
```

```sh
usage: asmapy-cli.py [-h] {diff,download,convert,to-binary} ...

Tool for performing various operations on texual and binary asmap files.

options:
  -h, --help            show this help message and exit

valid subcommands:
  {diff,download,convert,to-binary}
    diff                compute the difference between two asmap files
    download            download dumps
    convert             convert dump files to human-readable dumps (getting unique originating ASN for this prefix
    to-binary           convert human-readable dump into binary asmap file
```
