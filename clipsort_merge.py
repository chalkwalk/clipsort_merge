#!/usr/bin/python3
"""A tool to merge several ninjam session archives."""

import argparse
import os
import shutil
import sys

parser = argparse.ArgumentParser(description='Merge a set of ninjam session archives.')

parser.add_argument('directories', metavar='DIR', type=str, nargs='+', help='The directories to consider.')
parser.add_argument('--output_directory', '-o', metavar='DIR', type=str, help='The directory in which to output the resulting merged session.')
parser.add_argument('--force', '-f', action='store_true', default=False, help='If set, delete the target merged directory if it already exists.')

args = parser.parse_args()

current_interval = {}


def PathCanonicalize(filename):
  # Given a path, if it's absolute, return it, if it's relative, assume it's
  # relative to the directory containing the executable.
  if os.path.isabs(filename):
    return filename
  else:
    return os.path.join(os.path.dirname(__file__), filename)


def LogPathToFilePath(log_path, file_hash):
    return os.path.join(os.path.dirname(log_path), file_hash[0], '%s.OGG' % file_hash)

def ParseClipsortLog(log_path):
    global current_interval
    interval_collection = []
    with open(log_path, 'r') as my_file:
      while True:
          line = my_file.readline().strip()
          if not line:
              break
          if line.startswith('interval'):
              if current_interval:
                  interval_collection.append(current_interval.copy())
              interval_split = line.split(' ')
              current_interval['interval_number'] = int(interval_split[1])
              current_interval['bpm'] = int(interval_split[2])
              current_interval['bpi'] = int(interval_split[3])
              current_interval['users'] = []
          elif line.startswith('user'):
              quote_split=line.split('"')
              file_hash=quote_split[0].split(' ')[1]
              filename=LogPathToFilePath(log_path, file_hash)
              if not os.path.isfile(filename):
                  continue
              username=quote_split[1].split('@')[0]
              channel_num=int(quote_split[2])
              channel_name=quote_split[3]
              current_interval['users'].append({
                  'hash': file_hash,
                  'file': filename,
                  'user': username,
                  'channel_number': channel_num,
                  'channel_name': channel_name,
                  })
    if not interval_collection[0]['users']:
        del interval_collection[0]
    return sorted(interval_collection, key=lambda a: a['interval_number'])


def LoadAllClipsortLogs(directories):
    clipsort_logs = []
    for directory in directories:
        log_path = os.path.join(directory, 'clipsort.log')
        if os.path.exists(log_path):
            clipsort_logs += ParseClipsortLog(log_path)
        else:
            print('No cliplog found in', log_path, file=sys.stderr)
    return clipsort_logs


def CreateMergedSessionArchive(output_dir, clipsort_logs):
    parent_path = os.path.dirname(output_dir)
    if not os.path.isdir(parent_path):
        print('The parent directory of the output output_dir must exist.')
        return False
    if os.path.exists(output_dir):
        if os.path.isdir(output_dir):
            if args.force:
                shutil.rmtree(output_dir)
            else:
                print('The output output_dir exists, use --force to overwrite')
                return False
        else:
            print('The output output_dir isn\'t a directory, choose another output_dir')
            return False
    os.mkdir(output_dir)
    for hash_prefix in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
        os.mkdir(os.path.join(output_dir, hash_prefix))
    output_clipsort_log_path = os.path.join(output_dir, 'clipsort.log')
    with open(output_clipsort_log_path, 'w') as my_file:
        interval_number = 1
        for interval in clipsort_logs:
            if 'bpm' in interval and 'bpi' in interval:
                print('interval', interval_number, interval['bpm'], interval['bpi'], file=my_file)
                interval_number += 1
            for user in interval['users']:
                print('user', user['hash'], '"%s"' % user['user'], user['channel_number'], '"%s"' % user['channel_name'], file=my_file)
                audio_file_destination = os.path.join(output_dir, user['hash'][0], os.path.basename(user['file']))
                os.symlink(user['file'], audio_file_destination)
    return True


def main():
    ordered_directories=sorted([PathCanonicalize(x) for x in args.directories], key=lambda a: os.path.dirname(a))
    clipsort_logs=LoadAllClipsortLogs(ordered_directories)
    output_directory = args.output_directory
    if not output_directory:
        output_directory = os.path.join(os.path.dirname(PathCanonicalize(ordered_directories[0])), 'merged.ninjam')
    if CreateMergedSessionArchive(output_directory, clipsort_logs):
        print('Merged session output at', output_directory)


if __name__ == '__main__':
  main()
