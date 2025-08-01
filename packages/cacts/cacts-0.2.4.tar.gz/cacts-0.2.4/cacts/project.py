"""
A Project class to hold some properties of a cmake project
that CACTS will use at runtime
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from .utils import expect

###############################################################################
@dataclass
class Project:
###############################################################################
    """
    An object storing config data for a cmake
    """
    root_dir: str
    name: str = field(init=False)
    baselines_gen_label: Optional[str] = None
    baselines_cmp_label: Optional[str] = None
    baselines_summary_file: Optional[str] = None
    cdash: Dict[str, any] = field(default_factory=dict)

    # To check inside init
    valid_keys = {
            'name',
            'baseline_gen_label',
            'baseline_cmp_label',
            'baseline_summary_file',
            'cmake_settings',
            'cdash'
    }

    def __init__ (self,project_specs,root_dir):
        expect (isinstance(project_specs,dict),
                f"Project constructor expects a dict object (got {type(project_specs)} instead).\n")

        # Check for unrecognized keys (may be typos)
        unrecognized_keys = set(project_specs.keys()) - self.valid_keys
        expect (not unrecognized_keys,
                f"Unrecognized keys in project_specs: {', '.join(unrecognized_keys)}")

        expect ('name' in project_specs.keys(),
                "Missing required field 'name' in 'project' section.\n")

        self.root_dir = root_dir

        self.name = project_specs['name']

        # If left to None, ALL tests are run during baselines generation
        self.baselines_gen_label = project_specs.get('baseline_gen_label',None)

        # If set, when -b <dir> is NOT used (signaling NO baselines tests),
        # tests with this label are NOT run. Defaults to baselines_gen_label
        self.baselines_cmp_label = project_specs.get('baseline_cmp_label',self.baselines_gen_label)

        # Projects can dump in this file (relative to cmake build dir) the list of
        # baselines files that need to be copied to the baseline dir. This allows
        # CACTS to ensure that ALL baselines tests complete sucessfully before copying
        # any file to the baselines directory
        self.baselines_summary_file = project_specs.get('baseline_summary_file',None)

        # Allow to use a project cmake var that can turn on/off baseline-related code/tests.
        # Can help to limit build time
        # NOTE: projects may have an option to ENABLE such code or an optio to DISABLE it.
        # Hence, we ooffer both alternatives
        self.cmake_settings = project_specs.get('cmake_settings',{})

        # Set empty sub-dicts if not present
        self.cmake_settings.setdefault('baselines_on',{})
        self.cmake_settings.setdefault('baselines_off',{})
        self.cmake_settings.setdefault('baselines_only',{})

        self.cdash = project_specs.get('cdash',{})
