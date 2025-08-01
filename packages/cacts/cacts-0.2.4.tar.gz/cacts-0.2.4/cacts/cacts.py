"""
This module implements the CACTS testing infrastructure, along with the main
entry point for usage from command line.
"""
import os
import sys
from pathlib import Path
import concurrent.futures as threading
import shutil
import json
import itertools
import argparse
import psutil

from .parse_config  import parse_project, parse_machine, parse_builds
from .utils         import expect, run_cmd, get_current_ref, get_current_sha, is_git_repo, \
                           check_minimum_python_version, GoodFormatter, \
                           SharedArea, get_cpu_ids_from_slurm_env_var
from .version import __version__

check_minimum_python_version(3, 4)

###############################################################################
def main():
###############################################################################
    """
    Entry point for the command line cacts program
    """

    driver = Driver(**vars(parse_command_line(sys.argv, __doc__, __version__)))

    success = driver.run()

    print(f"OVERALL STATUS: {'PASS' if success else 'FAIL'}")

    sys.exit(0 if success else 1)

###############################################################################
# pylint: disable=too-many-instance-attributes
class Driver:
###############################################################################
    """
    Main CACTS class, responsible of handling the whole execution.
    It gathers configuration settings, parallelizes the builds,
    generates cmake/ctest commands, runs the tests, and possibly
    takes care of updating the baselines
    """

    ###########################################################################
    # pylint: disable=too-many-positional-arguments, too-many-arguments, too-many-locals, too-many-statements
    def __init__(self, config_file=None,
                 machine_name=None, local=False, build_types=None,
                 work_dir=None, root_dir=None, baseline_dir=None,
                 cmake_args=None, test_regex=None, test_labels=None,
                 config_only=False, build_only=False, skip_config=False, skip_build=False,
                 generate=False, submit=False, parallel=False, verbose=False):
    ###########################################################################

        self._submit        = submit
        self._parallel      = parallel
        self._generate      = generate
        self._baselines_dir = baseline_dir
        self._cmake_args    = cmake_args
        work_dir_str = work_dir or os.getcwd()+"/ctest-build"
        self._work_dir      = Path(work_dir_str).expanduser().absolute()
        self._verbose       = verbose
        self._config_only   = config_only
        self._build_only    = build_only
        self._skip_config   = skip_config or skip_build # If we skip build, we also skip config
        self._skip_build    = skip_build
        self._test_regex    = test_regex
        self._test_labels   = test_labels
        self._root_dir      = Path(root_dir or os.getcwd()).expanduser().absolute()
        self._machine       = None
        self._builds        = []
        self._config_file   = Path(config_file or self._root_dir / "cacts.yaml")

        # Ensure work dir exists
        self._work_dir.mkdir(parents=True,exist_ok=True)

        ###################################
        #  Parse the project config file  #
        ###################################

        expect (self._config_file.exists(),
                f"Could not find/open config file: {self._config_file}\n")
        expect (not (local and machine_name),
                "Makes no sense to use -m/--machine and -l/--local at the same time")

        self._project = parse_project(self._config_file,self._root_dir)
        if local:
            machine_name = 'local'
        self._machine = parse_machine(self._config_file,self._project,machine_name)
        self._builds  = parse_builds(self._config_file,self._project,
                                     self._machine,self._generate,build_types)

        ###################################
        #          Sanity Checks          #
        ###################################

        expect (not (self._config_only and self._skip_config),
                "Makes no sense to use --config-only and --skip-config/--skip-build together.\n")
        expect (not (self._build_only and self._skip_build),
                "Makes no sense to use --build-only and --skip-build together.\n")
        expect (not (self._generate and self._skip_config),
                "We do not allow to skip config/build phases when generating baselines.\n")

        # We print some git sha info (as well as store it in baselines),
        # so make sure we are in a git repo
        expect(is_git_repo(self._root_dir),
               f"Root dir: {self._root_dir}, does not appear to be a git repo.\n"
                "Did you forget to pass -r <repo-root>?")

        # If we submit, we must a) not be generating, and b) be able to find
        # the CTestConfig.cmake script in the root dir or have cdash options
        # from the project configuration settings
        if self._submit:
            expect (not self._generate,
                    "Cannot submit to cdash when generating baselines. Re-run without -g.")

            # Check all cdash settings are valid in the project
            cdash = self._project.cdash
            expect (cdash.get('ctest_config_file',None) or
                    (cdash.get('drop_site',None) and cdash.get('drop_location',None)),
                    "Cannot submit to cdash, since project.cdash.url is not set.\n"
                    "Please fix your yaml config file.\n")

        ###################################
        #      Compute baseline info      #
        ###################################

        if self._baselines_dir:
            if self._baselines_dir.casefold() == "AUTO".casefold():
                self._baselines_dir = Path(self._machine.baselines_dir)
            else:
                self._baselines_dir = Path(self._baselines_dir)

            self._baselines_dir = self._baselines_dir.expanduser().absolute()

            expect (self._work_dir != self._baselines_dir,
                    "For your safety, do NOT use the work dir to store baselines.\n"
                    "Use a different one (a subdirectory works too).")

            if not self._generate:
                self.check_baselines_are_present()

            self._enable_baselines_tests = True
        else:
            self._enable_baselines_tests = False

        # Make the baseline dir, if not already existing.
        if self._generate:
            expect(self._baselines_dir is not None, "Cannot generate without -b/--baseline-dir")

        ###################################
        #    Set computational resources  #
        ###################################

        if self._parallel:
            # NOTE: we ASSUME that num_run_res>=num_bld_res, which is virtually always true

            # Our way of partitioning the compute node among the different builds only
            # works if the number of bld/run resources is no-less than the number of builds
            expect (self._machine.num_run_res>=len(self._builds),
                    "Cannot process build types in parallel; not enough resources.\n"
                    f" - build types: {','.join(b.name for b in self._builds)}\n"
                    f" - num run res: {self._machine.num_run_res}")

            num_bld_res_left = self._machine.num_bld_res
            num_run_res_left = self._machine.num_run_res

            for i,b in enumerate(self._builds):
                num_left = len(self._builds)-i
                b.testing_res_count = num_bld_res_left // num_left
                b.compile_res_count = num_run_res_left // num_left

                num_bld_res_left -= b.compile_res_count
                num_run_res_left -= b.testing_res_count
        else:
            # We can use all the res on the node
            for b in self._builds:
                b.testing_res_count = self._machine.num_run_res
                b.compile_res_count = self._machine.num_bld_res

    ###############################################################################
    # pylint: disable=too-many-locals
    def run(self):
    ###############################################################################
        """
        Runs tests or generate baselines for all the requested configurations.
        """

        git_ref = get_current_ref ()
        git_sha = get_current_sha (short=True)

        print("###############################################################################")
        action = "Generating baselines" if self._generate else "Running tests"
        print(f"{action} with git ref '{git_ref}' ({git_sha}) on machine '{self._machine.name}'")
        if self._baselines_dir:
            print(f"  Baselines directory: {self._baselines_dir}")
        print(f"  Active builds: {', '.join(b.name for b in self._builds)}")
        print("###############################################################################")

        builds_success = {
            build : False
            for build in self._builds}

        num_workers = len(self._builds) if self._parallel else 1

        with threading.ProcessPoolExecutor(max_workers=num_workers) as executor:

            future_to_build = {
                    executor.submit(self.run_build,build) : build
                    for build in self._builds}
            for future in threading.as_completed(future_to_build):
                build = future_to_build[future]
                builds_success[build] = future.result()

        success = True
        for b,s in builds_success.items():
            success &= s
            if not s:
                last_submit = self.get_last_ctest_file(b,"Submit")
                last_test = self.get_last_ctest_file(b,"TestsFailed")
                last_build  = self.get_last_ctest_file(b,"Build")
                last_config = self.get_last_ctest_file(b,"Configure")
                if last_submit is not None:
                    print(f"Build type {b.longname} failed at submit time.\n"
                          f"Here's the content of {last_submit}:")
                    print (last_submit.read_text())
                if last_test is not None:
                    print(f"Build type {b.longname} failed at testing time.\n"
                          f"Here's the content of {last_test}:")
                    print (last_test.read_text())
                elif last_build is not None:
                    print(f"Build type {b.longname} failed at build time.\n"
                          f"Here's the content of {last_build}:")
                    print (last_build.read_text())
                elif last_config is not None:
                    print(f"Build type {b.longname} failed at config time.\n"
                          f"Here's the content of {last_config}:")
                    print (last_config.read_text())
                else:
                    print(f"Build type {b.longname} failed before configure step.")

        return success

    ###############################################################################
    # pylint: disable=too-many-locals
    def run_build(self,build):
    ###############################################################################
        """
        Runs tests or generate baselines for a particular configurations.
        """

        build_dir = self._work_dir / build.longname
        if self._skip_config:
            expect (build_dir.exists(),
                    "Build directory did not exist, but --skip-config/--skip-build was used.\n")
        else:
            if build_dir.exists():
                shutil.rmtree(build_dir)
            build_dir.mkdir()

        # If we're generating for the first time in this baseline dir, ensure that the folder exists
        if self._generate:
            baseline_dir = self._baselines_dir / build.longname
            baseline_data_dir = baseline_dir / "data"

            baseline_dir.mkdir(exist_ok=True)
            baseline_data_dir.mkdir(exist_ok=True)

        self.create_ctest_resource_file(build,build_dir)
        cmake_config = self.generate_cmake_config(build)
        ctest_cmd = self.generate_ctest_cmd(build,cmake_config)

        print("===============================================================================")
        print(f"Processing build {build.longname}")
        print(f"  ctest command: {ctest_cmd}")
        print("===============================================================================")

        # Generate the script ctest will run
        self.generate_ctest_script(build)

        # Run ctest
        env_setup = " && ".join(self._machine.env_setup)
        stat, _, _ = run_cmd(ctest_cmd,arg_stdout=None,arg_stderr=None,env_setup=env_setup,
                             from_dir=build_dir,verbose=True)
        success = stat==0

        if self._generate and success:

            # Read list of nc files to copy to baseline dir
            if self._project.baselines_summary_file is not None:
                summary_file = build_dir / self._project.baselines_summary_file
                with open(summary_file,"r",encoding="utf-8") as fd:
                    files = fd.read().splitlines()

                    with SharedArea():
                        for fn in files:
                            # In case appending to the file leaves an empty line at the end
                            if fn != "":
                                src = Path(fn)
                                dst = baseline_dir / "data" / src.name
                                shutil.copyfile(src, dst)

            # Store the sha used for baselines generation. This is only for record keeping.
            baseline_file = baseline_dir / "baseline_git_sha"
            with baseline_file.open("w", encoding="utf-8") as fd:
                sha = get_current_sha()
                fd.write(sha)
            build.baselines_missing = False

        return success

    ###############################################################################
    def create_ctest_resource_file(self, build, build_dir):
    ###############################################################################
        """
        Generate the ctest resource-spec-file used to spread tests across resources
        """
        # Create a json file in the build dir, which ctest will then use
        # to schedule tests in parallel.
        # In the resource file, we have N res groups with 1 slot, with N being
        # what's in build.testing_res_count. On CPU machines, res groups
        # are cores, on GPU machines, res groups are GPUs. In other words, a
        # res group is where we usually bind an individual MPI rank.
        # The id of the res groups is offset-ed so that it is unique across all builds

        resources = self.get_taskset_resources(build, for_compile=False)

        data = {}

        # This is the only version numbering supported by ctest, so far
        data["version"] = {"major":1,"minor":0}

        # We add leading zeroes to ensure that ids will sort correctly
        # both alphabetically and numerically
        devices = []
        for res_id in resources:
            devices.append({"id":f"{res_id:05d}"})

        # Add resource groups
        data["local"] = [{"devices":devices}]

        with (build_dir/"ctest_resource_file.json").open("w", encoding="utf-8") as outfile:
            json.dump(data,outfile,indent=2)

        return len(resources)

    ###############################################################################
    def get_taskset_resources(self, build, for_compile):
    ###############################################################################
        """
        Get the list of resources for this build, which we can later use with 'taskset' cmd
        """
        res_name = "compile_res_count" if for_compile else "testing_res_count"

        if not for_compile and self._machine.uses_gpu():
            # For GPUs, the cpu affinity is irrelevant. Just assume all GPUS are open
            affinity_cp = list(range(self._machine.num_run_res))
        elif "SLURM_CPU_BIND_LIST" in os.environ:
            affinity_cp = get_cpu_ids_from_slurm_env_var()
        else:
            this_process = psutil.Process()
            affinity_cp = list(this_process.cpu_affinity())

        affinity_cp.sort()

        if self._parallel:
            it = itertools.takewhile(lambda item: item != build, self._builds)
            offset = sum(getattr(prevs, res_name) for prevs in it)
        else:
            offset = 0

        expect(offset < len(affinity_cp),
               f"Offset {offset} out of bounds (max={len(affinity_cp)})\n"
               f"  - build: {build}\n"
               f"  - affinity_cp: {affinity_cp}")
        resources = []
        for i in range(0, getattr(build, res_name)):
            resources.append(affinity_cp[offset+i])

        return resources

    ###############################################################################
    def get_last_ctest_file(self,build,phase):
    ###############################################################################
        """
        Get the most recent file generated by CTest for this build and for the
        requested ctest execution phase (Configure, Build, Test, etc)
        """
        build_dir = self._work_dir / build.longname
        logs_dir = build_dir / "Testing/Temporary"
        files = list(logs_dir.glob(f"Last{phase}*"))
        # ctest creates files of the form Last{phase}_$TIMESTAMP.log, so lexicographical
        # sorting will ensure that the last one is the most recent
        files = sorted(files)
        return files[-1] if files else None

    ###############################################################################
    def generate_cmake_config(self, build):
    ###############################################################################
        """
        Generate the list of CMake options for this build
        """

        cmake_config = ""
        if self._machine.mach_file is not None:
            cmake_config += f"-C {self._machine.mach_file}"

        # Build-specific cmake options
        for key, value in build.cmake_args.items():
            cmake_config += f" -D{key}={value} "

        # Compilers
        if self._machine.cxx_compiler is not None:
            cmake_config += f" -DCMAKE_CXX_COMPILER={self._machine.cxx_compiler}"
        if self._machine.c_compiler is not None:
            cmake_config += f" -DCMAKE_C_COMPILER={self._machine.c_compiler}"
        if self._machine.ftn_compiler is not None:
            cmake_config += f" -DCMAKE_Fortran_COMPILER={self._machine.ftn_compiler}"

        proj_cmake_settings = self._project.cmake_settings
        if self._enable_baselines_tests:
            # If the project has cmake vars to set in order to ENABLE baseline tests,
            # set these vars to the specified values
            for var_name,var_value in proj_cmake_settings['baselines_on'].items():
                cmake_config += f" -D{var_name}={var_value}"

            if self._generate:
                # If the project has cmake vars to set in order to ONLY run baselines tests,
                # set these vars to the specified values
                # NOTE: this option may enable only a SUBSET of baseline tests,
                #       and help reduce the build/run time when generating
                for var_name,var_value in proj_cmake_settings['baselines_only'].items():
                    cmake_config += f" -D{var_name}={var_value}"
        else:
            # If the project has cmake vars to set in order to DISABLE baseline tests,
            # set these vars to the specified values
            for var_name,var_value in proj_cmake_settings['baselines_off'].items():
                cmake_config += f" -D{var_name}={var_value}"

        # User-requested config options
        for arg in self._cmake_args:
            expect ("=" in arg,
                    f"Invalid value for -c/--cmake-args: {arg}. Should be `VAR_NAME=VALUE`.")

            name, value = arg.split("=", 1)
            # Some effort is needed to ensure quotes are perserved
            cmake_config += f" -D{name}='{value}'"

        cmake_config += f" -S {self._project.root_dir}"

        return cmake_config

    ###############################################################################
    def generate_ctest_cmd(self, build, cmake_config):
    ###############################################################################
        """
        Generate the ctest command to run
        """

        ctest_cmd = "ctest"
        ctest_cmd += " -VV" if self._verbose else " --output-on-failure"
        ctest_cmd += f" -S {self._work_dir / build.longname / 'ctest_script.cmake'}"

        ctest_cmd += f' -DCMAKE_COMMAND="{cmake_config}"'

        if self._submit:
            ctest_cmd += " -D Experimental"

        ctest_res_file = f"{self._work_dir}/{build.longname}/ctest_resource_file.json"
        ctest_cmd += f' --resource-spec-file {ctest_res_file}'

        # If the build is not concurrent to other builds, this is not really necessary,
        # since we can use the whole node.
        if self._parallel:
            resources = self.get_taskset_resources(build, for_compile=True)
            ctest_cmd = f"taskset -c {','.join([str(r) for r in resources])} sh -c '{ctest_cmd}'"

        return ctest_cmd

    ###############################################################################
    # pylint: disable=too-many-statements
    def generate_ctest_script(self,build):
    ###############################################################################
        """
        Generate ctest_script.cmake in the build folder, which will be fed to ctest
        """

        text = '# This file was automatically generated by CACTS.\n'
        text += f'# CACTS yaml config file: {self._config_file}\n\n'

        text += 'cmake_minimum_required(VERSION 3.9)\n\n'
        text += 'set(CTEST_CMAKE_GENERATOR "Unix Makefiles")\n\n'

        text += f'set(CTEST_SOURCE_DIRECTORY {self._project.root_dir})\n'
        text += f'set(CTEST_BINARY_DIRECTORY {self._work_dir / build.longname})\n\n'

        if self._submit:
            cdash = self._project.cdash
            text += '# Submission specs\n'
            build_name = self._project.cdash.get("build_prefix","")+build.longname
            text += f'set(CTEST_BUILD_NAME {build_name})\n'
            text += f'set(CTEST_SITE {self._machine.name})\n'
            text += f'set(CTEST_DROP_SITE {cdash["drop_site"]})\n'
            text += f'set(CTEST_DROP_LOCATION {cdash["drop_location"]})\n'
            disable_ssl = cdash.get('curl_ssl_off',False)
            if disable_ssl:
                curl_options = 'CURLOPT_SSL_VERIFYPEER_OFF;CURLOPT_SSL_VERIFYHOST_OFF'
                text += f'set(DCTEST_CURL_OPTIONS "{curl_options}")\n\n'

        text += '# Start ctest session\n'
        text += 'ctest_start(Experimental)\n\n'

        text += '# Configure phase\n'
        text += 'separate_arguments(OPTIONS_LIST UNIX_COMMAND "${CMAKE_COMMAND}")\n'
        text += 'ctest_configure(OPTIONS "${OPTIONS_LIST}" RETURN_VALUE CONFIG_ERROR_CODE)\n'

        text += 'if (CONFIG_ERROR_CODE)\n'
        text += '  message (FATAL_ERROR "CTest failed during configure phase")\n'
        text += 'endif ()\n\n'

        if not self._config_only:
            text += '# Build phase\n'
            text += f'ctest_build(FLAGS "-j{build.compile_res_count}"\n'
            text +=  '            RETURN_VALUE BUILD_ERROR_CODE)\n'
            text += 'if (BUILD_ERROR_CODE)\n'
            text += '  message (FATAL_ERROR "CTest failed during build phase")\n'
            text += 'endif()\n\n'

            if not self._build_only:
                text += '# Test phase\n'
                test_line = 'ctest_test(RETURN_VALUE TEST_ERROR_CODE'
                test_line += f' PARALLEL_LEVEL {build.testing_res_count}'
                if self._test_regex:
                    test_line += f' INCLUDE {self._test_regex}'
                if self._test_labels:
                    test_line += f' INCLUDE_LABEL {self._test_labels}'
                elif self._generate and self._project.baselines_gen_label:
                    test_line += f' INCLUDE_LABEL {self._project.baselines_gen_label}'
                test_line += ")\n"

                text += test_line
                text += 'if (TEST_ERROR_CODE)\n'
                text += '    message (FATAL_ERROR "CTest failed during test phase")\n'
                text += 'endif()\n\n'

                if build.coverage:
                    text += '# Coverage phase\n'
                    text += 'ctest_coverage(RETURN_VALUE COVERAGE_ERROR_CODE)\n'
                    text += 'if (COVERAGE_ERROR_CODE)\n'
                    text += '  message (FATAL_ERROR "CTest failed during coverage phase")\n'
                    text += 'endif()\n\n'

                if self._submit:
                    text += '# Submit phase\n'
                    text += 'ctest_submit(RETRY_COUNT 10 RETRY_DELAY 60\n'
                    text += '             RETURN_VALUE SUBMIT_ERROR_CODE)\n'
                    text += 'if (SUBMIT_ERROR_CODE)\n'
                    text += '  message (FATAL_ERROR "CTest failed during submit phase")\n'
                    text += 'endif()\n'

        ctest_script_file = self._work_dir / build.longname / "ctest_script.cmake"
        with open( ctest_script_file, 'w', encoding='utf-8') as fd:
            fd.write(text)

    ###############################################################################
    def check_baselines_are_present(self):
    ###############################################################################
        """
        Check that all baselines are present for the build types that use baselines
        """

        print (f"Checking baselines directory: {self._baselines_dir}")
        missing = []
        for build in self._builds:
            if build.uses_baselines:
                data_dir = self._baselines_dir / build.longname / "data"
                if not data_dir.is_dir():
                    build.baselines_missing = True
                    missing.append(build.longname)
                    print(f" -> Build {build.longname} is missing baselines (no {data_dir} dir)")
                else:
                    print(f" -> Build {build.longname} appears to have baselines")
            else:
                print(f" -> Build {build.longname} does not use baselines")

        expect (len(missing)==0,
                f"Re-run with -g to generate missing baselines for builds {missing}")

###############################################################################
def parse_command_line(args, description, version):
###############################################################################
    """
    Parse command line options for cacts
    """
    cmd = Path(args[0]).name
    # pylint: disable=R0801
    parser = argparse.ArgumentParser(
        usage=f"""
{cmd} <ARGS> [--verbose]
OR
{cmd} --help

\033[1mEXAMPLES:\033[0m
    \033[1;32m# Run all tests on machine 'foo', using yaml config file /bar.yaml \033[0m
    > {cmd} -m foo -f /bar.yaml
""",
        description=description,
        formatter_class=GoodFormatter
    )

    parser.add_argument("-f","--config-file",
        help="YAML file containing valid project/machine settings")

    parser.add_argument("-m", "--machine-name",
        help="The name of the machine where we're testing. Must be found in machine_specs.py")
    parser.add_argument("-l", "--local", action="store_true",
        help="Allow to look for machine configuration in ~/.cime/catcs.yaml. "
             "The file should contain the machines section, with a machine called 'local'.")
    parser.add_argument("-t", "--build-types", action="extend", nargs='+', default=[],
        help="Only run specific test configurations")

    parser.add_argument("-w", "--work-dir",
        help="The work directory where all the building/testing will happen. "
             "Defaults to ${root_dir}/ctest-build")
    parser.add_argument("-r", "--root-dir",
        help="The root directory of the project (where the main CMakeLists.txt file is located)")
    parser.add_argument("-b", "--baseline-dir",
        help="Directory where baselines should be read/written from/to (depending if -g is used). "
             "Default is None (skips all baseline tests). AUTO means use machine-defined folder.")

    parser.add_argument("-c", "--cmake-args", nargs='+', action="extend", default=[],
        help="Extra custom options to pass to cmake. Can use multiple times for multiple cmake "
             "options. The -D is added for you, so just do VAR=VALUE. These value will supersed "
             "any other setting (including machine/build specs)")
    parser.add_argument("--test-regex",
        help="Limit ctest to running only tests that match this regex")
    parser.add_argument("--test-labels", nargs='+', default=[],
        help="Limit ctest to running only tests that match this label")

    parser.add_argument("--config-only", action="store_true",
        help="Only run config step, skip build and tests")
    parser.add_argument("--build-only", action="store_true",
        help="Only run config and build steps, skip tests (implies --no-build)")

    parser.add_argument("--skip-config", action="store_true",
        help="Skip cmake phase, pass directly to build. Requires the build directory to exist, "
                 "and will fail if cmake phase never completed in that dir.")
    parser.add_argument("--skip-build", action="store_true",
        help="Skip build phase, pass directly to test. Requires the build directory to exist, "
             "and will fail if build phase never completed in that dir (implies --skip-config).")

    parser.add_argument("-g", "--generate", action="store_true",
        help="Instruct test-all-eamxx to generate baselines from current commit. Skips tests")

    parser.add_argument("-s", "--submit", action="store_true", help="Submit results to dashboad")
    parser.add_argument("-p", "--parallel", action="store_true",
        help="Launch the different build types stacks in parallel")

    parser.add_argument("-v", "--verbose", action="store_true",
        help="Print output of config/build/test phases as they would be printed by a manual run.")

    parser.add_argument("--version", action="version", version=f"%(prog)s {version}",
        help="Show the version number and exit")

    return parser.parse_args(args[1:])
