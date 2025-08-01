""" Main entry point for cacts"""

from cacts.cacts import main as cacts_main
from cacts.get_mach_env import print_mach_env

def main() -> None:
    """
    Entry point for the main CACTS program
    """
    cacts_main()

def get_mach_env() -> None:
    """
    Entry point for the command-line utility for retrieving a machine env config command
    """
    print_mach_env()
