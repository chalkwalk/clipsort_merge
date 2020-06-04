#!/usr/bin/python3
"""A tool to merge several ninjam session archives."""

import argparse
import os

parser = argparse.ArgumentParser(description='Merge a set of ninjam session archives.')

parser.add_argument('--clipsort', '-c', metavar='FILE', type=str, required=True, help='The original clipsort.log.')

args = parser.parse_args()


def PathCanonicalize(filename):
  # Given a path, if it's absolute, return it, if it's relative, assume it's
  # relative to the directory containing the executable.
  if os.path.isabs(filename):
    return filename
  else:
    return os.path.join(os.path.dirname(__file__), filename)


def main():
    clipsort = PathCanonicalize(args.clipsort)
    lines = []
    with open(clipsort, 'r') as f:
        lines.append('interval 0 0 0')
        interval_number = 0
        for line in f:
            if line.startswith('interval'):
                interval_number += 1
                elements = line.strip().split(' ')
                lines.append('interval %s %s %s' % (interval_number, elements[1], elements[2]))
            else:
                lines.append(line.strip())
    with open('%s.new' % clipsort, 'w') as f:
        print('\n'.join(lines), file=f)
    os.rename(clipsort, '%s.old' % clipsort)
    os.rename('%s.new' % clipsort, clipsort)


if __name__ == '__main__':
  main()
