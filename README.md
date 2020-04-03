# Clipsort merge

## Introduction
[Ninjam](https://www.cockos.com/ninjam/) is a service that allows multiple people to jam together over the internet, even with long network delays. It provides a mechanism on both the client and server side to save the audio. In particular for servers there is a mechanism to save all intervals played by all users in individual audio files, recorded in a set of directories by hash and indexed by a text file known as `clipsort.log`. Such log files and directories can be used alongside tools such as [autosong](https://github.com/justinfrankel/ninjam/tree/master/ninjam/autosong) and [Reaper](http://reaper.fm) one can create a consolidated project or merged audio files from the sessions. The default server behaviour is to create one such session archive and log for every interval of time (defaulting to 10 minutes). This tool allows several such directories to be merged into one by creating a new clipsort log and symlinking the necessary audio files.

## Usage
At a basic level the command is used as follows:
```
usage: clipsort_merge.py [-h] [--output_directory DIR] [--force] DIR [DIR ...]
  DIR                   The directories to consider.
```
In particular one provides a list of directories (possibly by way of a glob) to merge and an optional output directory that will be created and filled with the new session archive. In the absence of a specified output directory a peer of the first specified output directory called 'merged.ninjam' will be created. An example invocation might be as follows:
```
$ ./clipsort_merge.py -o combined_log.ninjam my_server/path/2020_*.ninjam
```
in this case all directories matching the glob and containing a clipsort.log file will be merged into a new session archine in the current directory called `combined_log.ninjam`.
