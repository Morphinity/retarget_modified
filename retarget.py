#!/usr/bin/env python

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.realpath(os.path.dirname(__file__)), "radiotool")) # add subrepo root to front of import search path, so that local "radiotool" will be found.

from path import Path
from radiotool.composer import Song
from radiotool.algorithms import retarget

defaultlength = 60

def cachedir():
    root = None
    for candidate in [ Path("/var/cache"), Path(os.environ['HOME']).joinpath("Library", "Caches") ]:
        if candidate.isdir(): root = candidate
    return None if root is None else root.joinpath("retarget")

parser = argparse.ArgumentParser(
        description='Retargets music to desired length, with optional change point constraints.',
        usage='retarget [options] INFILE'
        )
parser.add_argument('-l', '--length', metavar='LENGTH', type=int, help='New length in seconds [default: {0}]'.format(defaultlength), default=defaultlength)
parser.add_argument('-o', '--output', metavar='OUTFILE', type=str, help='Output WAV file.  [default: INFILE-LENGTH.wav]')
parser.add_argument('-c', '--change', metavar='POINT', type=int, action='append', help='Change point time in seconds. Can be provided multiple times. If change points are specified, that implies --no-start and --no-end')
parser.add_argument('--start', dest='start', action='store_true', help='Require result to start at song start. [default]')
parser.add_argument('--no-start', dest='start', action='store_false', help='Do not require result to start at song start')
parser.add_argument('--end', dest='end', action='store_true', help='Require result to end at song end. [default]')
parser.add_argument('--no-end', dest='end', action='store_false', help='Do not require result to end at song end')
parser.add_argument('--cache', metavar='DIR', type=Path, help='Cache directory [{0}]'.format(cachedir()), default=cachedir())
parser.add_argument('--no-cache', dest='cache', action='store_const', const=None, help='Do not use cache')
parser.add_argument('-q', '--quiet', action='store_true', help="Quiet; do not print processing info.")
#parser.add_argument('input1', metavar='INFILE', type=str, help='Audio file to retarget (WAV format)')
#parser.add_argument('input2', metavar='INFILE', type=str, help='Audio file to retarget (WAV format)')
parser.add_argument('--s', '--single', dest='singlesong', action='store_true')
parser.add_argument('--old', dest='old', action='store_true')
parser.set_defaults(start=True, end=True, singlesong=False, old=False)
args = parser.parse_args()

constraint_params = {
    'timbre': 1.0,
    'chroma': 1.0,
    'energy': 1.0,
    'minbeats': 10,
    'changesong': 1.0,
    'minbeatcount': 3
}
for root, dirs, files in os.walk("../../input"):
    if 'config' in files:
        config = open(root + "/config", "r")
        song_paths = []
        length = 60
        start = True
        end = True
        old = False
        for line in config:
            params = line.split("=")
            if params[0] == "input":
                song_paths.append(root + "/" + params[1].split()[0])
            elif params[0] == "timbre":
                constraint_params[params[0]] = float(params[1].split()[0])
            elif params[0] == "chroma":
                constraint_params[params[0]] = float(params[1].split()[0])
            elif params[0] == "energy":
                constraint_params[params[0]] = float(params[1].split()[0])
            elif params[0] == "minbeats":
                constraint_params[params[0]] = int(params[1].split()[0])
            elif params[0] == "changesong":
                constraint_params[params[0]] = float(params[1].split()[0])
            elif params[0] == "length":
                length = float(params[1].split()[0])
            elif params[0] == "nostart\n":
                start = False
            elif params[0] == "noend\n":
                end = False
            elif params[0] == "minbeatcount":
                constraint_params[params[0]] = int(params[1].split()[0])

        config.close()

        outpath = Path(root + "/result.wav")

        if not args.quiet:
            for filepath in song_paths:
                print("input", filepath)
            print "output:\t" + outpath
            print "length:\t" + str(length)
            print "start:\t" + str(start)
            print "end:\t" + str(end)
            print "cache:\t" + str(args.cache)
            print "timbre:\t" + str(constraint_params["timbre"])
            print "chroma:\t" + str(constraint_params["chroma"])
            print "energy:\t" + str(constraint_params["energy"])
            print "minbeats:\t" + str(constraint_params["minbeats"])
            print "changesong:\t" + str(constraint_params["changesong"])
            print "minbeatcount:\t" + str(constraint_params["minbeatcount"])

        songs = []
        for path in song_paths:
            songs.append(Song(path, cache_dir=str(args.cache)))

        composition = retarget.retarget_multi_songs_to_length(songs, length, constraint_params, start=start, end=end,
                                                                  old=old)

        composition.export(filename=outpath.stripext())

        if not args.quiet: print "Wrote {0}".format(outpath)

"""
input_paths = open("../../input_paths", "r")

song_paths = []
for line in input_paths:
    song_paths.append(line.split()[0])
input_paths.close()

length = args.length
change_points = sorted(args.change or [])
if change_points: args.start = args.end = False

if args.output:
    outpath = Path(args.output)
else:
    tag = "result-mod"

if args.output:
    outpath = Path(args.output)
else :
    print("output file not defined")

if not args.quiet:
    for filepath in song_paths:
        print("input", filepath)
    print "output:\t"+outpath
    print "length:\t"+str(length)
    print "change_points:\t"+" ".join(map(str, change_points))
    print "start:\t"+str(args.start)
    print "end:\t"+str(args.end)
    print "cache:\t"+str(args.cache)

if not args.quiet: print "Retargeting..."

if args.cache is not None: args.cache.makedirs_p()

song1 = Song(inpath1, cache_dir = str(args.cache))
if not args.singlesong:
    song2 = Song(inpath2, cache_dir = str(args.cache))

songs = []
for path in song_paths:
    songs.append(Song(path, cache_dir = str(args.cache)))

if change_points:
    composition, change_points = retarget.retarget_with_change_points(songs[0], change_points, length)
elif not args.singlesong:
    composition = retarget.retarget_multi_songs_to_length(songs, length, start=args.start, end=args.end, old=args.old)
else :
    composition = retarget.retarget_to_length(songs[0], length, start=args.start, end=args.end)

composition.export(filename=outpath.stripext())
if not args.quiet: print "Wrote {0}".format(outpath)
"""
