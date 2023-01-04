# Asmapy - Asmap | Bitcoin Core

CLI to download dumps, convert dump files to human-readable ones, compare two files, and other stuff. Some codes presented here were originally written in [sipa/asmap](https://github.com/sipa/asmap/tree/nextgen).

### Installing and running

```sh
$ pip install -r requirements.txt
```

```sh
$ ./asmapy.py -h
```

```sh
usage: asmapy.py [-h] {diff,download,to-human-readable,to-binary,to-mapping} ...

Tool for performing various operations on texual and binary asmap files.

options:
  -h, --help            show this help message and exit

valid subcommands:
  {diff,download,to-human-readable,to-binary,to-mapping}
    diff                compute the difference between two asmap files
    download            download dumps
    to-human-readable   convert dump files to human-readable dumps (getting unique originating ASN for this prefix)
    to-binary           convert human-readable dump into binary asmap file
    to-mapping          convert (sets of) human-readable dumps into a text file with iprange->asn mappings
```


#### 1. Downloading dumps

You can get dumps from a specific date (YYYYMMDD).

```sh
$ ./asmapy.py download 20220202
```

#### 2. Converting dump files to human-readable

After downloading the dumps, they will be available in a folder (e.g. `data-20220202`), and you can use that directory in the following command to convert them to a human-readable format:

```sh
$ ./asmapy.py to-human-readable -p data-20220202
```

You can also pass more than one folder, this can be useful to combine data from different dates, e.g:
```sh
$ ./asmapy.py to-human-readable -p data-20220202 data-20221212
```

Use `--allasn` to fetch all ASN for every prefix instead of unique originating one.

Use `--singleoutput` to combine all dumps into one file.

####  3. Converting human-readable dumps into a text file with iprange->asn mappings

After converting the dumps using `to-human-readable --singleoutput`, you're gonna have one file with all dumps, it means we can have duplicated stuff. 
For this reason, you can use the following command to convert them into a text file with iprange->asn mappings.

```sh
$ ./asmapy.py to-mapping path/to/file
```

#### 4. Converting a file to binary

```sh
$ ./asmapy.py to-binary path/to/file
```

#### Comparing two files

```sh
$ ./asmapy.py diff path/to/file1 path/to/file2
```

Optional flags:
- `--ignore-unassigned` to ignore unassigned ranges in the first input (useful when second input is filled).
- `--unified` to get output diff in `unified` format.
