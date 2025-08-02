# # Merge mp3 files from the current directory or from subfolders (each into one mp3 file)
# Group files into subfolders. Create groups of a certain size.
# Ungroup files from subfolders.
# Carsten Engelke 2023

import os
import subprocess
import sys
import time

from _thread import start_new_thread
from pynput.keyboard import Controller, Key # type: ignore
import math as m
from shutil import copyfile

__all__ = ["main", "mergemp3", "packsubdirs", "unpackdirs"]

VERSIONSTR = "1.0.8 (C)opyright Carsten Engelke 2022"
argmax = len(sys.argv) - 1
foobarpath = "C:/Program Files (x86)/foobar2000/foobar2000.exe"
mp3tagpath = "C:/Program Files (x86)/Mp3tag/Mp3tag.exe"
decisionset = False
mergesub = True
workingdir = os.getcwd()
autowaittime = 5
groupsize = 15
filefilter = ".mp3"
subdirfilter = "subdir-"
copymode = False
removesubdirmode = True
yes = ['yes', 'y', 'ja', 'j', '', 'Yes', 'Y', 'YES', '1']
no = ['no', 'n', 'nein', 'N', 'NO', 'No', '0']
move = ['move', 'Move', 'MOVE', no]

def mergesubdirs(dir, foobarpath, autowaittime):
    filelist = []
    with os.scandir(dir) as it:
        for subdir in it:
            if (not subdir.name.startswith(".") and subdir.is_dir()):
                aimfile = mergedir(subdir, True)
                if (aimfile != None):
                    filelist.append(aimfile)
    callfoobar(foobarpath, dir, filelist, autowaittime)
    print("Merging subdirectories of " + dir + " done.")


def mergedir(dir, copytoparent):
    if (copytoparent):
        filestr = os.path.dirname(dir.path) + os.sep + dir.name + ".mp3"
    else:
        filestr = os.path.dirname(dir) + os.sep + \
            os.path.basename(dir) + ".mp3"
    mp3number = " ".join(os.listdir(dir)).count(".mp3")
    mp3now = 0
    if (mp3number > 0):
        print("mp3 file found. Merging to: " +
              filestr + "...0%\r", end=" ", flush=True)
        if (os.path.exists(filestr)):
            os.remove(filestr)
        with open(filestr, "ab") as aimfile:
            with os.scandir(dir) as it:
                for f in it:
                    if (f.name.endswith(".mp3") and f.is_file()):
                        mp3now += 1
                        srcfile = open(f, "rb")
                        aimfile.write(srcfile.read())
            return aimfile
    else:
        print("No mp3 in '" + dir.path + "' found.")
        return None


def callfoobar(foobarpath, workdir, filelist, autowaittime):
    # if not in windows skip foobar2000 execution
    if os.name == "nt":
        filenamelist = []
        for f in filelist:
            filenamelist.append(f.name)
        rebuildcmdlist = [foobarpath]
        rebuildcmdlist.append("/runcmd-files=Util/Rebuild")
        rebuildcmdlist.extend(filenamelist)
        fixcmdlist = [foobarpath]
        fixcmdlist.append("/runcmd-files=Util/Fix")
        fixcmdlist.extend(filenamelist)
        minimizecmdlist = [foobarpath]
        minimizecmdlist.append(
            "/runcmd-files=Utilities/Optimize file layout + minimize file size")
        minimizecmdlist.extend(filenamelist)
        os.chdir(workdir)
        if (autowaittime >= 0):
            print("Calling foobar2000 for rebuilding the mp3 stream. Automatically ending in:" +
                str(autowaittime*len(filenamelist)), end="...", flush=True)
            start_new_thread(
                closefoobar, (foobarpath, autowaittime, len(filelist), True))
        else:
            print("Calling foobar2000 for rebuilding the mp3 stream. Please close the foobar window to continue", end="...", flush=True)
        subprocess.call(rebuildcmdlist)
        print("done")
        if (autowaittime >= 0):
            print("Calling foobar2000 for fixing the mp3 metadata length. Automatically ending in:" +
                str(autowaittime*len(filenamelist)/2), end="...", flush=True)
            start_new_thread(
                closefoobar, (foobarpath, autowaittime/2, len(filelist), True))
        else:
            print("Calling foobar2000 for fixing the mp3 metadata length. Please close the foobar window to continue", end="...", flush=True)
        subprocess.call(fixcmdlist)
        print("done")
        if (autowaittime >= 0):
            print("Calling foobar2000 for minimizing file. Automatically ending in " +
                str(autowaittime*len(filenamelist)/3), end="...", flush=True)
            start_new_thread(
                closefoobar, (foobarpath, autowaittime/3, len(filelist), False))
        else:
            print("Calling foobar2000 for minimizing file. Please close the foobar window to continue",
                end="...", flush=True)
        subprocess.call(minimizecmdlist)
        print("done")
        return True
    else:
        print("foobar2000 onyl available in windows - skipping. Use mp3diags manually in linux e.g.")
        return False


def closefoobar(foobarpath, sleeptime, filenumber, press):
    closecmdlist = [foobarpath, "/exit"]
    k = Controller()
    if (press):
        time.sleep(sleeptime)
        k.press(Key.enter)
        k.release(Key.enter)
    time.sleep(sleeptime * filenumber)
    subprocess.call(closecmdlist)


def mergemp3cli(args):

    global decisionset
    global argmax
    global workingdir
    global mergesub
    global foobarpath
    global autowaittime

    print("mp3-tools merge-mp3 {0}".format(VERSIONSTR))
    print(
        "Usage: mp3tools merge-mp3 [dir] [subdir-mode] [foobarpath] [autowaittime]")
    print("    [dir] determines the directory in which to perform the script. Use '.' to select the current directory")
    print("    [subdir-mode] determines wheter all mp3 files in subfolders should be merged into one file each. ('True' to do so)")
    print("    [foobarpath] determines the path to your foobar2000 installation. Please provide in case it differs from 'C:/Program Files (x86)/foobar2000/foobar2000.exe'. Use '.' to remain unchanged.")
    print("    [autowaittime] determines whether to automatically clos foobar2000 after some seconds. Use -1 to disable and any number to set the waiting time.")

    if (argmax > 1 and args[1] != "."):
        if (os.path.isdir(args[1])):
            workingdir = args[1]
        else:
            choice = ""
            while (choice != "y" and choice != "n" and choice != "Y" and choice != "N"):
                choice = input("Specified directory not found: " +
                               args[1] + " ... will use current directory instead: " + workingdir + "...OK? (Y)es or (N)o?")
                if choice in no:
                    sys.exit(0)

    if (argmax > 2):
        decisionset = True
        if (args[2] == "true" or args[2] == "True"):
            mergesub = True
        else:
            mergesub = False

    if (argmax > 3 and args[3] != "."):
        foobarpath = args[3]

    if (argmax > 4):
        autowaittime = int(args[4])

    while (not decisionset):
        print("merge-mp3 [dir={0}] [subdir-mode={1}] [foobarpath={2}] [autowaittime={3}]".format(workingdir, mergesub, foobarpath, autowaittime))
        choice = input(" > Merge (S)ubfolders or this (D)irectory or (A)bort?")
        if (choice == "S" or choice == "s"):
            mergesub = True
            decisionset = True
        if (choice == "D" or choice == "d"):
            mergesub = False
            decisionset = True
        if (choice == "A" or choice == "a"):
            sys.exit(0)
    mergemp3(workingdir, mergesub, foobarpath, autowaittime)


def mergemp3(dir, mergesub, foobarpath, autowaittime):

    print("calling mergemp3 [mergesub=" + str(mergesub) + "] [dir=" + dir +
          "] [foobarpath=" + foobarpath + "]  [autowaittime=" + str(autowaittime) + "]")

    if (mergesub):
        mergesubdirs(dir, foobarpath, autowaittime)
    else:
        aimfile = mergedir(dir, False)
        if (aimfile != None):
            callfoobar(foobarpath, dir, [aimfile], autowaittime)
        print("Merging mp3s in " + dir + " done.")


def packsubdirscli(args):

    global decisionset
    global groupsize
    global workingdir
    global filefilter
    global copymode

    print("pack-subdirs {0}".format(VERSIONSTR))
    print("Use: mp3tools pack-subdirs [group-size] [dir] [file-filter] [copy-mode]")
    print("    [group-size] determines the number of files to put into each directory")
    print("    [dir] determines the directory in which to perform the script. Use '.' to select the current directory")
    print("    [file-filter] Filter the file list according to this.")
    print("    [copy-mode] If 'True', the files are copied into the created subfolders. If 'False' they are moved (Use with caution).")

    if (argmax > 1):
        groupsize = int(args[1])
        decisionset = True
    if (argmax > 2):
        if args[2] != ".":
            workingdir = args[2]
    if (argmax > 3):
        filefilter = args[3]
    if (argmax > 4):
        c = args[4]
        if c == "0" or c == "move" or c == "Move" or c == "MOVE" or c == "false" or c == "FALSE" or c == "False":
            copymode = False
    print("calling pack-subdirs: [group-size=" + str(groupsize) + "] [dir=" +
          workingdir + "] [filter=" + filefilter + "] [copy-mode=" + str(copymode) + "]")

    if (not decisionset):
        print(
            "Pack files according to above settings into subdirectories [y/n]?")
        choice = input().lower()
        if not choice in yes:
            sys.exit()
    packsubdirs(groupsize, workingdir, filefilter, copymode)


def packsubdirs(groupsize, dir, filter, copy):

    l = []
    with os.scandir(dir) as it:
        for entry in it:
            if (entry.name.find(filter) >= 0 and os.path.isfile(entry)):
                l.append(entry)
    dirnum = m.ceil(len(l) / groupsize)
    anz = 0
    dirnumactual = 1
    dirname = dir + "/subdir-" + str(dirnumactual)
    try:
        os.makedirs(dirname)
    except:
        print("directory already exists")
    for entry in l:
        if anz >= groupsize:
            anz = 0
            dirnumactual += 1
            dirname = dir + "/subdir-" + str(dirnumactual)
            print("create: " + dirname)
            try:
                os.mkdir(dirname)
            except:
                print("directory already exists")
        if copy:
            copyfile(dir + "/" + entry.name, dirname + "/" + entry.name)
            print("FILE_COPIED: " + entry.name)
        else:
            os.rename(dir + "/" + entry.name, dirname + "/" + entry.name)
            print("FILE_MOVED: " + entry.name)
        anz += 1

def unpackdirscli(args):

    global decisionset
    global workingdir
    global filefilter
    global subdirfilter
    global copymode
    global removesubdirmode

    print("unpack-subdirs {0}".format(VERSIONSTR))
    print("Use: mp3tools unpack-subdirs [dir] [subdir-filter] [file-filter] [copy-mode] [removesubdir-mode]")
    print("    [dir] determines the directory in which to perform the script. Use '.' to select the current directory")
    print("    [subdir-filter] Filter the subdir list according to this. Use '*' to select any subdirectory")
    print("    [file-filter] Filter the file list according to this.")
    print("    [copy-mode] If 'True', the files are copied into the parent folder. If 'False' they are moved (Use with caution).")
    print("    [removesubdir-mode] If 'True', the subdirectories are deleted. If 'False' they are left as they are.")

    if argmax > 1:
        if args[1] == "-h" or args[1] == "-help" or args[1] == "-H" or args[1] == "-HELP" or args[1] == "-Help":
            sys.exit(0)
        if args[1] != ".":
            workingdir = args[1]
        decisionset = True
    if argmax > 2:
        subdirfilter = args[2]
    if argmax > 3:
        filefilter = args[3]
    if argmax > 4:
        c = args[4]
        if c == "0" or c == "move" or c == "Move" or c == "MOVE" or c == "false" or c == "FALSE" or c == "False":
            copymode = False
    if argmax > 5:
        c = args[5]
        if c == "0" or c == "false" or c == "False" or c == "FALSE":
            removesubdirmode = False
    print("calling unpack-subdirs [dir=" + str(workingdir) + "] [subdir-filter=" + subdirfilter +
          "] [file-filter=" + filefilter + "] [copy-mode=" + str(copymode) + "] [removesubdir-mode=" + str(removesubdirmode) + "]")
    if (not decisionset):
        print(
            "Unpack files according to above settings into subdirectories [y/n]?")
        choice = input().lower()
        if not choice in yes:
            sys.exit()
    unpackdirs(workingdir, subdirfilter, filefilter, copymode, removesubdirmode)

def unpackdirs(workdir, subdirfilter, filefilter, copy, remove):
    l = []
    with os.scandir(workingdir) as it:
        for entry in it:
            if (subdirfilter == "*" and os.path.isdir(entry)):
                l.append(entry)
            else:
                if (entry.name.find(subdirfilter) >= 0 and os.path.isdir(entry)):
                    l.append(entry)

    for subdir in l:
        with os.scandir(subdir) as it:
            for entry in it:
                if (entry.name.find(filefilter) >= 0 and os.path.isfile(entry)):
                    if copy:
                        copyfile(workingdir + "/" + subdir.name + "/" +
                                 entry.name, workingdir + "/" + entry.name)
                        print("FILE_COPIED: " + entry.name)
                    else:
                        os.rename(workingdir + "/" + subdir.name + "/" +
                                  entry.name, workingdir + "/" + entry.name)
                        print("FILE_MOVED: " + entry.name)
        if (remove):
            os.removedirs(subdir)
            print("DIR_REMOVED: " + subdir.name)

def selectsubprogram():
    waitforchoice = True
    while (waitforchoice):
        choice = input("(M)erge mp3 files, (P)ack subfolders, (U)npack subfolders or (A)bort?")
        if (choice == "M" or choice == "m"):
            mergemp3cli([])
            waitforchoice = False
        if (choice == "P" or choice == "p"):
            packsubdirscli([])
            waitforchoice = False
        if (choice == "U" or choice == "u"):
            unpackdirscli([])
            waitforchoice = False
        if (choice == "A" or choice == "a"):
            sys.exit(0)

def main():
    """
    The main function executes on commands:
    `python -m mp3tools` and `$ mp3tools `.

    This is your program's entry point.
    """
    global autowaittime

    print ("Usage: mp3tools merge-mp3 [dir] [subdir-mode] [foobarpath] [autowaittime]")
    print ("Usage: mp3tools pack-subdirs [group-size] [dir] [file-filter] [copy-mode]")
    print ("Usage: mp3tools unpack-subdirs [dir] [subdir-filter] [file-filter] [copy-mode] [removesubdir-mode]")
    print ("Usage: mp3tools wait=seconds")
    print ("Note: This script depends on a foobar2000 installation! (Get it from: https://www.foobar2000.org/)")
    args = sys.argv[1:]
    if (len(args) > 0):
        if args[0] == "merge-mp3":
            mergemp3cli(args)
        if args[0] == "pack-subdirs":
            packsubdirscli(args)
        if args[0] == "unpack-subdirs":
            unpackdirscli(args)
        if args[0].startswith("wait"):
            autowaittime = int(args[0][5:])
            selectsubprogram()
    else:
        selectsubprogram()

if __name__ == "__main__":
    main()