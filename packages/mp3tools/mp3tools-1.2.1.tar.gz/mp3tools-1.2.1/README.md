# mp3tools
Merge mp3 files and set correct audio length using foobar2000 with an automated python script. These scripts can merge all files in one directory or create one file for each subdirectory.


![merge mp3 files from subdirectories](https://github.com/carsten-engelke/mp3tools/blob/main/mergemp3subdirs.jpg)
 - mp3tools merge-mp3: merging script, works with foobar2000
 - mp3tools pack-subdirs: pack files into grouped subdirectories (good for large audiobooks)
 - mp3tools unpack-subdirs.py: unpack files from grouped subdirectories (undo mp3tools pack-subdirs)

## Version
1.2.2 Fixed 

1.2.0 Added PI/CI Support thanks to https://github.com/rochacbruno/python-project-template

1.0.0 release version. Ported to vscode.

0.2.0 bug corrected foobar needs to be called from working directory as the command line plugin cannot handle empty spaces in file names or paths given by command line

0.1.0 initial release. Port from windows script to python, introducing automation

## Requirements
- Python (script was created using python 3.7.0) (https://www.python.org/)
- foobar2000 (https://www.foobar2000.org/)

## Installation
pip install mp3tools

## Usage
Command-line-use:
```
mp3tools -> start tools using standard wizard, just follow instructions.

mp3tools merge-mp3 [dir] [subdir-mode] [foobarpath] [autowaittime]
    [dir] determines the directory in which to perform. Use '.' to select the current directory
    [subdir-mode] determines wheter all mp3 files in subfolders should be merged into one file each. ('True' to do so)")
    [foobarpath] determines the path to your foobar2000 installation. Please provide in case it differs from 'C:/Program Files (x86)/foobar2000/foobar2000.exe'
    [autowaittime] determines whether to automatically close foobar2000 after some seconds. Use -1 to disable and any number to set the waiting time.

mp3tools pack-subdirs [group-size] [dir] [file-filter] [copy-mode]
    [group-size] determines the number of files to put into each directory
    [dir] determines the directory in which to perform the script. Use '.' to select the current directory
    [file-filter] Filter the file list according to this
    [copy-mode] If 'True', the files are copied into the created subfolders. If 'False' they are moved (Use with caution).

mp3tools unpack-subdirs [dir] [subdir-filter] [filter] [copy-mode] [remove-dir]")
    [dir] determines the directory in which to perform the script. Use '.' to select the current directory
    [subdir-filter] Filter the subdir list according to this. Use '*' to select any subdirectory
    [filter] Filter the file list according to this
    [copy-mode] If 'True', the files are copied into the parent folder. If 'False' they are moved (Use with caution).
    [remove-dir] If 'True', the subdirectories are deleted. If 'False' they are left as they are.
```