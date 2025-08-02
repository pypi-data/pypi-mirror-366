
import argparse
from .dlkParse import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("--out", help = "Output file (json format)")
    parser.add_argument("--noprint", action = 'store_true', help = "Don't print output to console")
    args = parser.parse_args()

    if(args.infile):
        dlk = dlkIO(args.infile)
        if(not args.noprint):
            dlk.dlkPrint()
        if(args.out):
            dlk.dlkDumpJSON(args.out) 

