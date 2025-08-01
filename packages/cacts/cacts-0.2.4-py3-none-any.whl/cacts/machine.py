"""
This module defines a Machine object, which stores properties and settings
for a testing machine to be used by CACTS
"""

import pathlib
import socket
import re

from .utils import expect, get_available_cpu_count, evaluate_py_expressions

###############################################################################
class Machine: # pylint: disable=too-many-instance-attributes
###############################################################################
    """
    An object storing configuration settings for a machine
    """

    def __init__ (self,name,project,machines_specs):
        # Check inputs
        expect (isinstance(machines_specs,dict),
                "Machine constructor expects a dict object for 'machines_specs'"
                "  - type(machines_specs): {type(machines_specs)}.\n")
        if name is None:
            hostname = socket.gethostname()
            # Loop over machines, and see if there's one whose 'node_regex' matches the hostname
            for mn,props in machines_specs.items():
                if "node_regex" in props.keys() and props["node_regex"]:
                    if re.match(props["node_regex"],hostname):
                        expect (name is None,
                                 "Multiple machines' node_regex match this hostname.\n"
                                f"  - hostname: {hostname}\n"
                                f"  - mach 1: {name}\n"
                                f"  - mach 2: {mn}\n")
                        name = mn
            expect (name is not None,
                    "Machine name was not provided, and none of the machines' node_regex "
                    f"matches hostname={hostname}\n")
        else:
            avail_machs = machines_specs.keys()
            expect (name in avail_machs,
                    f"Machine '{name}' not found in the 'machines' section of the config file.\n"
                    f" - available machines: {','.join(m for m in avail_machs if m!='default')}\n")

        self.name = name

        # Init everything to None
        self.mach_file      = None
        self.num_bld_res    = None
        self.num_run_res    = None
        self.env_setup      = None
        self.gpu_arch       = None
        self.batch          = None
        self.cxx_compiler   = None
        self.c_compiler     = None
        self.ftn_compiler   = None
        self.baselines_dir  = None
        self.valg_supp_file = None
        self.inherits       = None

        # Set parameter, first using the 'default' machine (if any), then this machine's settings
        # Note: if this machine inherits from M2, M2's settings will be parsed first
        self.update_params(machines_specs,'default')
        self.update_params(machines_specs,name)

        # If these are still None, set some defaults
        # NOTE: DON'T do this before all dicts update calls, since a value of None in one
        # of the dicts would end up overwriting the default. So do this AFTER all updates
        self.env_setup = self.env_setup or []
        self.num_bld_res = self.num_bld_res or get_available_cpu_count()
        self.num_run_res = self.num_run_res or get_available_cpu_count()

        # Expand variables and evaluate expressions
        # Perform substitution of ${..} strings
        objects = {
            'project' : project,
            'machine' : self,
        }
        evaluate_py_expressions(self,objects)

        # Check props are valid
        expect (self.mach_file is None or pathlib.Path(self.mach_file).expanduser().exists(),
                f"Invalid/non-existent machine file '{self.mach_file}'")
        expect (isinstance(self.env_setup,list),
                "machine->env_setup type error\n"
                " - expected type: list of strings\n"
               f" - actual type  : {type(self.env_setup)}.\n")

        try:
            self.num_bld_res = int(self.num_bld_res)
        except ValueError:
            print("Error! Cannot convert 'num_bld_res' entry to an integer.")
            raise
        try:
            self.num_run_res = int(self.num_run_res)
        except ValueError:
            print("Error! Cannot convert 'num_run_res' entry to an integer.\n")
            raise

    def update_params(self,machines_specs,name):
        """
        Updates the attributes of this object by reading the input dictionary
        """
        if name in machines_specs.keys():
            props = machines_specs[name]
            if 'inherits' in props.keys():
                self.update_params(machines_specs,props['inherits'])
            self.__dict__.update(props)

    def uses_gpu (self):
        """
        Whether this machine uses GPU accelerators or not
        """
        return self.gpu_arch is not None
