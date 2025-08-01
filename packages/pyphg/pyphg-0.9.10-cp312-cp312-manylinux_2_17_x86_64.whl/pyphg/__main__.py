import argparse
import os,sys,re
import pyphg as phg

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
    help_parser = subparsers.add_parser('help', help='show help')
    info_parser = subparsers.add_parser('info', help='show info of the package')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    examples_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'examples'))
    if args.subcommand == 'help':
        print(f'''
  use 
    cp -r {examples_path} .
  to copy out a example, and use 
    python simplest.py
  to run the example
    ''')

    if args.subcommand == 'info':
        print("Solvers:")
        for it in phg.getSolvers():
          print(f"    {it}")
        print("FEFunctions:")
        for it in phg.getDofs():
          print(f"    {it}")

main()

