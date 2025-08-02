'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Houses utility methods and initializes cli based tools.
Common for all cli implementations of DataTransforms
'''
import logging
import sys
import argparse

if sys.version_info[0] < 3:
    raise EnvironmentError("Must be executed with python 3")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--log-level",
    help="Defualt is INFO, can be one of DEBUG|ERROR",
    choices=list(["ERROR","INFO","DEBUG"]))

def print_product_msg():
    """
    Print the product name
    """
    print ("\nOracle DataTransforms\n")

def set_log_level(level):
    """
    Update the log level for all CLI extensions 
    """
    logging.getLogger().setLevel(level)

def arg_to_bool(arg):
    """
    Utility method to convert the argument to boolean. 
    Agument with value yes, true, t,y,1,ok -> all will be evaluated to boolean value True,
    othewise the result will be false.
    """
    if isinstance(arg, bool):
        return arg
    if isinstance(arg,str):
        if arg.lower() in ('yes', 'true', 't', 'y', '1','ok'):
            return True
        else:
            return False
    else:
        raise argparse.ArgumentTypeError('Boolean or String with True or False value expected.')

def process_args(arg_parser):
    """
    Method to process the input arguments , update the log level based on input
    """
    args = arg_parser.parse_args()
    print_product_msg()
    if args.log_level:
        set_log_level(args.log_level)
        logging.debug("Arguments %s" , (str(args)))
    else:
        set_log_level("INFO")
    return args
