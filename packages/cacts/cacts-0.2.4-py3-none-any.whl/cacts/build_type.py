"""
This module defines a BuildType object, which stores properties and settings
for a particular project configuration to be tested by CACTS
"""

from .utils import expect, evaluate_py_expressions, str_to_bool

###############################################################################
class BuildType: # pylint: disable=R0902, R0903
###############################################################################
    """
    Class of predefined build types for the project.
    The script 'test-proj-build' will query this object for runtime info on the build
    """

    def __init__(self, name, project, machine, builds_specs):
        # Check inputs
        expect (isinstance(builds_specs,dict),
                "Error! Invalid type for build_specs arg to BuildType constructor.\n"
                " - expected type: dict\n"
               f" - actual type  : {type(builds_specs)}")
        keys = builds_specs.keys()
        expect (name in keys,
                f"BuildType '{name}' not found in the 'build_types' section of the config file.\n"
                f" - available build types: {','.join(b for b in keys if b!='default')}\n")

        self.name = name

        # Init everything to None
        self.longname       = None
        self.description    = None
        self.uses_baselines = None
        self.on_by_default  = None
        self.cmake_args     = None
        self.inherits       = None

        # Set parameter, first using the 'default' build (if any), then this build's settings
        # Note: if this build inherits from B2, B2's settings will be parsed first
        self.update_params(builds_specs,'default')
        self.update_params(builds_specs,name)

        # Get props for this build type and for a default build
        props   = builds_specs[name]
        default = builds_specs.get('default',{})
        self.name   = name
        self.longname    = props.get('longname',name)
        self.description = props.get('description',None)
        self.uses_baselines = props.get('uses_baselines',None)
        self.on_by_default  = props.get('on_by_default',None)
        self.coverage = props.get('coverage',False)
        if  self.uses_baselines is None:
            self.uses_baselines = default.get('uses_baselines',True)
        if  self.on_by_default is None:
            self.on_by_default  = default.get('on_by_default',True)

        expect (isinstance(props.get('cmake_args',{}),dict),
                f"Invalid value for cmake_args for build type '{name}'.\n"
                f"  - input value: {props.get('cmake_args',{})}\n"
                f"  - input type: {type(props.get('cmake_args',{}))}\n"
                 "  - expected type: dict\n")
        expect (isinstance(default.get('cmake_args',{}),dict),
                f"Invalid value for cmake_args for build type 'default'.\n"
                f"  - input value: {default.get('cmake_args',{})}\n"
                f"  - input type: {type(default.get('cmake_args',{}))}\n"
                 "  - expected type: dict\n")
        self.cmake_args = default.get('cmake_args',{})
        self.cmake_args.update(props.get('cmake_args',{}))

        # Perform substitution of ${..} strings
        objects = {
            'project' : project,
            'machine' : machine,
            'build'   : self
        }
        evaluate_py_expressions(self,objects)

        # After vars expansion, these two must be convertible to bool
        if isinstance(self.uses_baselines,str):
            self.uses_baselines = str_to_bool(self.uses_baselines,f"{name}.uses_baselines")
        if isinstance(self.on_by_default,str):
            self.on_by_default  = str_to_bool(self.on_by_default,f"{name}.on_by_default")

        # Properties set at runtime by the TestProjBuild
        self.compile_res_count = None
        self.testing_res_count = None
        self.baselines_missing = False

    def update_params(self,builds_specs,name):
        """
        Updates the attributes of this object by reading the input dictionary
        """
        if name in builds_specs.keys():
            props = builds_specs[name]
            if 'inherits' in props.keys():
                self.update_params(builds_specs,props['inherits'])
            self.__dict__.update(props)
