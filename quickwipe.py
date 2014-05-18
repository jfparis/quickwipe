#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import os
import subprocess


chunksize = 4096


def sync():
    subprocess.call("sync")


def gen_seed():
    p1 = subprocess.Popen(["dd", "if=/dev/urandom", "bs=128", "count=1"], stdout=subprocess.PIPE, stderr=open(os.devnull, 'wb'))
    p2 = subprocess.Popen(["base64"], stdin=p1.stdout, stdout=subprocess.PIPE)
    seed = p2.communicate()[0]
    return seed


def wipe(args):
    for file in args.files:
        file_size = os.stat(file).st_size
        if file_size < 1:
            print("file {} is empty. Cannot wipe it".format(file))
            break

        for i in xrange(args.iterations):
            print("wiping {}, pass {} of {}".format(file, i+1, args.iterations))
            fd = open(file,"rb+")
            fd.seek(0, 0)
            p1 = subprocess.Popen(["cat", "/dev/zero"], stdout=subprocess.PIPE, stderr=open(os.devnull, 'wb'))
            p2 = subprocess.Popen(["head", "-c", str(file_size)], stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            p3 = subprocess.Popen(["openssl" if args.openssl is None else args.openssl, "enc", "-aes-256-ctr", "-pass", 'pass:"'+gen_seed()+'"', "-nosalt"], stdin=p2.stdout, stdout=subprocess.PIPE, bufsize=-1)
            p2.stdout.close()

            while True:
                chunk = p3.stdout.read(chunksize)
                if chunk:
                    fd.write(chunk)
                else:
                    break
            fd.close()
            sync()


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=wipe)
    parser.add_argument("files", nargs='*')
    parser.add_argument("--openssl", help="path to openssl binary")
    parser.add_argument("--iterations", help="number of iterations (default = 8)", type=int, default=8)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()