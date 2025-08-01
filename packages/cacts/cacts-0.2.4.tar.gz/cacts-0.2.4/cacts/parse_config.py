"""
Utilities to parse different sections of a CACTS configure file
"""

import pathlib
import yaml

from .project    import Project
from .machine    import Machine
from .build_type import BuildType
from .utils      import expect, check_minimum_python_version

check_minimum_python_version(3, 4)

###############################################################################
def parse_project(config_file,root_dir):
###############################################################################
    """
    Parse the 'project' section of cacts config file
    Returns a Project object
    """
    with open(config_file,"r",encoding='utf-8') as fd:
        content = yaml.load(fd,Loader=yaml.SafeLoader)

    expect ('project' in content.keys(),
            "Missing 'project' section in configuration file\n"
            f" - config file: {config_file}\n"
            f" - sections found: {','.join(content.keys())}\n")

    # Build Project
    return Project(content['project'],root_dir)

###############################################################################
def parse_machine(config_file,project,machine_name):
###############################################################################
    """
    Parse the 'machine' section of cacts config file
    Returns a Machine object
    """
    with open(config_file,"r",encoding='utf-8') as fd:
        content = yaml.load(fd,Loader=yaml.SafeLoader)

    expect ('machines' in content.keys(),
            "Missing 'machines' section in configuration file\n"
            f" - config file: {config_file}\n"
            f" - sections found: {','.join(content.keys())}\n")

    # Special handling of 'local' machine
    machs = content['machines']
    if machine_name=="local":
        local_yaml = pathlib.Path("~/.cime/cacts.yaml").expanduser()
        with open(local_yaml,'r',encoding='utf-8') as fd:
            local_content = yaml.load(fd,Loader=yaml.SafeLoader)
        machs.update(local_content['machines'])
        machine_name = 'local'

    # Build Machine
    return Machine(machine_name,project,machs)

###############################################################################
def parse_builds(config_file,project,machine,generate,build_types=None):
###############################################################################
    """
    Parse the 'configuration' section of cacts config file
    Returns a list of BuildType objects
    """
    with open(config_file,"r",encoding='utf-8') as fd:
        content = yaml.load(fd,Loader=yaml.SafeLoader)

    expect ('configurations' in content.keys(),
            "Missing 'configurations' section in configuration file\n"
            f" - config file: {config_file}\n"
            f" - sections found: {','.join(content.keys())}\n")

    # Get builds
    builds = []
    if build_types:
        for name in build_types:
            build = BuildType(name,project,machine,content['configurations'])
            # Skip non-baselines builds when generating baselines
            if not generate or build.uses_baselines:
                builds.append(build)
    else:
        configs = content['configurations']
        # Add all build types that are on by default
        for name in configs.keys():
            if name=='default':
                continue
            build = BuildType(name,project,machine,configs)

            # Skip non-baselines builds when generating baselines
            if (not generate or build.uses_baselines) and build.on_by_default:
                builds.append(build)

    return builds
