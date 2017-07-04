#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# * * * * * * * * * * * * * * * * * * * *
#   port_scanner: a simple port scanner
#   Requires python3
#
#   Help & Usage:
#   $ python3 port_scanner.py -h
#
# * * * * * * * * * * * * * * * * * * * *
#
#   MIT License
#
#   Copyright (c) 2017 William Normandin
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
# * * * * * * * * * * * * * * * * * * * *

from multiprocessing import Pool, TimeoutError, Lock
import time
import socket
import argparse
import sys

VERSION = '0.1a'
RELEASE = 'Development'
this = sys.modules[__name__]

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, help='Specify a hostname to scan')
    parser.add_argument('--ports', nargs='*', help='Specify ports individually or in hyphenated ranges')
    parser.add_argument('--probe', action='store_true', help='Probe for services on open ports')
    parser.add_argument('--maxprocs', type=int, default=3, help='Specify max number of worker processes')
    parser.add_argument('--nocolor', action='store_true', help='Skip color in console output')
    parser.add_argument('--verbose', action='store_true', help='Increase output verbosity')
    parser.add_argument('--timeout', type=float, help='Request timeout in s', default=0.25)
    parser.add_argument('--yes', action='store_true', help='Start scan immediately after parsing input')
    parser.add_argument('--showall', action='store_true', help='Show all port tests')
    return parser.parse_args()


def cprint(val, col=None, verbose=False):
    if not args.verbose and verbose:
        return
    if col==None:
        msg = val
    else:
        msg = color_wrap(val, col)
    print(msg)


def color_wrap(val, col):
    if args.nocolor:
        return str(val)
    return ''.join([col, str(val), Color.END])


class Color:
    BLACK_ON_GREEN = '\x1b[1;30;42m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    MSG = '\x1b[1;32;44m'
    ERR = '\x1b[1;31;44m'
    TST = '\x1b[7;34;46m'


def worker(port):

    def probe():
        s.connect((args.ip, port))
        try:
            result = s.recv(2048).decode().rstrip()
        except socket.timeout:
            try:
                s.send("GET / HTTP/1.0\r\n\r\n".encode())
                result = s.recv(2048).decode('utf-8')[:45].replace('\n', ' % ').replace('\r', '')
            except socket.timeout:
                result = 'Probe returned no data'
        s.shutdown(1)
        s.close()
        return result

    try:
        s = socket.socket()
        s.settimeout(args.timeout)
        test = s.connect_ex((args.ip, port))
        if test == 0:
            if args.probe:
                return True, port, probe()
            else:
                return True, port
        else:
            return False, port
    except KeyboardInterrupt:
        cprint(' -  Interrupt in sub ({})'.format(os.getpid()), Color.BLUE, True)
        return False, None
    

def presenter(result):
    for r in sorted(_uniq(result)):
        if r[1] is not None:
            if r[0]:
                if args.probe:
                    cprint('Port {} OPEN: {}'.format(r[1], r[2]), Color.MSG)
                else:
                    cprint('Port {} OPEN'.format(r[1]), Color.MSG)
            else:
                if args.showall:
                    cprint('Port {} CLOSED'.format(r[1]), Color.ERR)


def _uniq(iterable):
    return list(set(iterable))


def print_args():
    if args.verbose:
        for arg in vars(args):
            cprint(' -  {:<10}: {:>20}'.format(arg, str(getattr(args, arg))), Color.BLUE, True)


def user_prompt(msg):
    ch = input(msg)
    if ch.lower() == 'y':
        return True
    return False


if __name__ == '__main__':
    try:
        this.args = cli()
        args.ip = socket.gethostbyname(args.host)
        cprint('[*] PokeyScan Port Scanner v{} ({})'.format(VERSION, RELEASE), Color.MSG)
        cprint(' -  Command Line Arguments Parsed', Color.GREEN, True)
        print_args()
        if not args.yes:
            if not user_prompt('Options parsed, proceed? (Y/n) > '):
                cprint('[!] User cancelled!', Color.ERR)
                sys.exit()
        else:
            cprint('[*] User chose --yes, beginning scan', Color.GREEN)
        pool = Pool(processes=args.maxprocs)
        cprint(' -  Worker Pool Created ({} worker(s))'.format(args.maxprocs), Color.GREEN, True)
        ports = []
        [ports.append(int(v)) for v in args.ports if '-' not in v]
        for v in args.ports:
            if '-' in v:
                low, high = v.split('-')
                ports.extend(range(int(low), int(high)+1))
        cprint(' -  Checking {} ports'.format(len(ports)), Color.GREEN, True)
        result = pool.map_async(worker, _uniq(ports))
        count = 0
        while not result.ready():
            count += 1
            if count % 10 == 0:
                cprint(' -  Waiting on {} workers'.format(result._number_left), Color.BLUE, True)
            time.sleep(args.timeout)
        cprint('[*] Workers spawned', Color.GREEN, True)
        pool.close()
        pool.join()
        cprint('[*] Workers joined', Color.GREEN, True)
        cprint('--------------------------------------------')
        presenter(result.get())
    except KeyboardInterrupt:
        cprint('[!] Keyboard Interrupt Detected', Color.ERR)
