"""
This module provides a utility to print the commands needed
to correctly setup a machine environment to replicate the
same environment used by CACTS
"""
import os
import sys
import pathlib
import argparse

from .parse_config  import parse_project, parse_machine
from .utils         import check_minimum_python_version, GoodFormatter

check_minimum_python_version(3, 4)

###############################################################################
def print_mach_env():
###############################################################################
    """
    Print the env setup command
    """

    args = vars(parse_command_line(sys.argv, __doc__))

    project = parse_project(args['config_file'],args['root_dir'])
    machine = parse_machine(args['config_file'],project,args['machine_name'])

    print(" && ".join(machine.env_setup))

    sys.exit(0)

###############################################################################
def parse_command_line(args, description):
###############################################################################
    """
    Parse the command line arguments
    """
    cmd = pathlib.Path(args[0]).name
    # pylint: disable=R0801
    parser = argparse.ArgumentParser(
        usage=f"""
{cmd} <ARGS> [--verbose]
OR
{cmd} --help

\033[1mEXAMPLES:\033[0m
    \033[1;32m# Get the env setup command for machine 'foo' using config file my_config.yaml \033[0m
    > ./{cmd} foo -f my_config.yaml
""",
        description=description,
        formatter_class=GoodFormatter
    )

    parser.add_argument("-f","--config-file", default=f"{os.getcwd()}/cacts.yaml",
        help="YAML file containing valid project/machine settings")

    parser.add_argument("-r", "--root-dir", default=f"{os.getcwd()}",
        help="The root directory of the project, where the main CMakeLists.txt file is located")

    parser.add_argument("machine_name", help="The machine name for which you want the scream env")

    return parser.parse_args(args[1:])
