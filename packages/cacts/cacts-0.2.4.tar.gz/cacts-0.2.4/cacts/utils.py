"""
Utilities for cacts.py - this has common functionality that is frequently used.
"""

import argparse
import os
import platform
import subprocess
import sys

import psutil

###############################################################################
def expect(condition, error_msg, exc_type=RuntimeError, error_prefix="ERROR:"):
###############################################################################
    """
    Similar to assert except doesn't generate an ugly stacktrace. Useful for
    checking user error, not programming error.

    >>> expect(True, "error1")
    >>> expect(False, "error2")
    Traceback (most recent call last):
        ...
    SystemExit: ERROR: error2
    """
    if not condition:
        msg = error_prefix + " " + error_msg
        raise exc_type(msg)

###############################################################################
# pylint: disable=too-many-positional-arguments, too-many-arguments
def run_cmd(cmd, from_dir=None, verbose=None, dry_run=False, env_setup=None,
            arg_stdout=subprocess.PIPE, arg_stderr=subprocess.PIPE,
            combine_output=False):
###############################################################################
    """
    Wrapper around subprocess to make it much more convenient to run shell commands

    >>> run_cmd('ls file_i_hope_doesnt_exist')[0] != 0
    True
    """

    # If the cmd needs some env setup, the user can pass the setup string, which will be
    # executed right before the cmd
    if env_setup:
        cmd = f"{env_setup} && {cmd}"

    arg_stderr = subprocess.STDOUT if combine_output else arg_stderr

    from_dir = str(from_dir) if from_dir else from_dir

    if verbose:
        print(f"RUN: {cmd}\nFROM: {os.getcwd() if from_dir is None else from_dir}")

    if dry_run:
        return 0, "", ""

    with subprocess.Popen(cmd, shell=True,
                          stdout=arg_stdout, stderr=arg_stderr,
                          stdin=None, text=True, # automatically decode output bytes to string
                          cwd=from_dir) as proc:

        output, errput = proc.communicate(None)
        if output is not None:
            output = output.strip()
        if errput is not None:
            errput = errput.strip()
        proc.wait()

        return proc.returncode, output, errput

###############################################################################
# pylint: disable=too-many-positional-arguments, too-many-arguments
def run_cmd_no_fail(cmd, from_dir=None, verbose=None, dry_run=False,env_setup=None,
                    arg_stdout=subprocess.PIPE, arg_stderr=subprocess.PIPE,
                    combine_output=False):
###############################################################################
    """
    Wrapper around subprocess to make it much more convenient to run shell commands.
    Expects command to work. Just returns output string.
    """
    stat, out, err = run_cmd(cmd,from_dir=from_dir,verbose=verbose,dry_run=dry_run,
                             env_setup=env_setup,arg_stdout=arg_stdout,arg_stderr=arg_stderr,
                            combine_output=combine_output)
    expect (stat==0,
            "Command failed unexpectedly"
            f"  - command: {cmd}"
            f"  - error: {err if err else out}"
            f"  - from dir: {from_dir or os.getcwd()}")

    return out

###############################################################################
def check_minimum_python_version(major, minor):
###############################################################################
    """
    Check your python version.

    >>> check_minimum_python_version(sys.version_info[0], sys.version_info[1])
    >>>
    """
    msg = f"Python {major}, minor version {minor} is required." \
          f"You have {sys.version_info[0]}.{sys.version_info[1]}"
    expect(sys.version_info[0] > major or
           (sys.version_info[0] == major and sys.version_info[1] >= minor), msg)

###############################################################################
class GoodFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
###############################################################################
    """
    We want argument default info to be added but we also want to
    preserve formatting in the description string.
    """

###############################################################################
def logical_cores_per_physical_core():
###############################################################################
    """
    Returns how many logical cores are available on each physical core
    """
    return psutil.cpu_count() // psutil.cpu_count(logical=False)

###############################################################################
def get_cpu_ids_from_slurm_env_var():
###############################################################################
    """
    Parse the SLURM_CPU_BIND_LIST, and use the hexadecimal value to determine
    which CPUs on this node are assigned to the job
    NOTE: user should check that the var is set BEFORE calling this function
    """

    cpu_bind_list = os.getenv('SLURM_CPU_BIND_LIST')

    expect (cpu_bind_list is not None,
            "SLURM_CPU_BIND_LIST env variable is not set.")

    # Remove the '0x' prefix and convert to an integer
    mask_int = int(cpu_bind_list, 16)

    # Generate the list of CPU IDs
    cpu_ids = []
    for i in range(mask_int.bit_length()):  # Check each bit position
        if mask_int & (1 << i):  # Check if the i-th bit is set
            cpu_ids.append(i)

    return cpu_ids

###############################################################################
def get_available_cpu_count(logical=True):
###############################################################################
    """
    Get number of CPUs available to this process and its children. logical=True
    will include hyperthreads, logical=False will return only physical cores
    """
    if 'SLURM_CPU_BIND_LIST' in os.environ:
        cpu_count = len(get_cpu_ids_from_slurm_env_var())
    elif platform.system() == "Darwin":  # macOS
        cpu_count = os.cpu_count()  # Fallback for macOS
    else:
        cpu_count = len(psutil.Process().cpu_affinity())

    if not logical:
        hyperthread_ratio = logical_cores_per_physical_core()
        cpu_count = int(cpu_count / hyperthread_ratio)

    return cpu_count

###############################################################################
class SharedArea:
###############################################################################
    """
    Enable 0002 umask within this manager
    """

    def __init__(self, new_perms=0o002):
        self._orig_umask = None
        self._new_perms  = new_perms

    def __enter__(self):
        self._orig_umask = os.umask(self._new_perms)

    def __exit__(self, *_):
        os.umask(self._orig_umask)

###############################################################################
def evaluate_py_expressions(tgt_obj, src_obj_dict):
###############################################################################
    """
    Expand occurrences of ${...} with the evaluation of the content of the
    parentheses interpreted as a python expression. For security reasons,
    We severely limit which builtin functions can be used: we only allow
    basic types (set, list, dict, int, etc) or basic functions (max, min,
    len, enumerate, etc). The user must also provide a dict str->obj of
    objects that can be used in these expressions.
    If the target object is a string, we proceed with the evaluation,
    while if it is a dict, list, or object, we recursively call the function
    on its entries/attributes.
    """
    # Only user-defined types have the __dict__ attribute
    if hasattr(tgt_obj,'__dict__'):
        for name,val in vars(tgt_obj).items():
            setattr(tgt_obj,name,evaluate_py_expressions(val,src_obj_dict))

    elif isinstance(tgt_obj,dict):
        for name,val in tgt_obj.items():
            tgt_obj[name] = evaluate_py_expressions(val,src_obj_dict)

    elif isinstance(tgt_obj,list):
        for i,val in enumerate(tgt_obj):
            tgt_obj[i] = evaluate_py_expressions(val,src_obj_dict)

    elif isinstance(tgt_obj,str):

        # First, extract content of ${...} (if any)
        beg = tgt_obj.find("${")
        end = tgt_obj.rfind("}")

        if beg==-1:
            expect (end==-1,
                    f"Badly formatted expression '{tgt_obj}'."
                     "Found '}' but no '${'.")
            return tgt_obj

        expect (end>=0,
                f"Badly formatted expression '{tgt_obj}'."
                 "Found '${' but no '}'.")
        expect (end>beg,
                f"Badly formatted expression '{tgt_obj}'."
                 "Found '}' before '${'.")
        expect (tgt_obj.rfind("${")==beg,
                f"Badly formatted expression '{tgt_obj}'."
                 "Multiple ${..} instances found.")

        expression = tgt_obj[beg+2:end]

        restricted_globals = {
            "__builtins__": {
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "set": set,
                "tuple": tuple,
                "dict": dict,
                "enumerate": enumerate,
                "len": len,
                "sum": sum,
                "abs": abs,
                "max": max,
                "min": min,
                "round": round
            }
        }
        restricted_globals.update(src_obj_dict)
        result = eval(expression,restricted_globals) # pylint: disable=eval-used
        tgt_obj = tgt_obj[:beg] + str(result) + tgt_obj[end+1:]

    return tgt_obj

###############################################################################
def str_to_bool(s, var_name):
###############################################################################
    """
    Converts a string representation of a bool ('True'/'False') into a bool
    """
    if s=="True":
        return True
    if s=="False":
        return False

    raise ValueError(f"Invalid value '{s}' for '{var_name}'.\n"
                      "Should be either 'True' or 'False'")

###############################################################################
def is_git_repo(repo=None):
###############################################################################
    """
    Check that the folder is indeed a git repo
    """

    stat, _, _ = run_cmd("git rev-parse --is-inside-work-tree",from_dir=repo)

    return stat==0

###############################################################################
def get_current_ref(repo=None):
###############################################################################
    """
    Return the name of the current branch for a repository
    If in detached HEAD state, returns None
    """

    return run_cmd_no_fail("git rev-parse --abbrev-ref HEAD",from_dir=repo)

###############################################################################
def get_current_sha(short=False,repo=None):
###############################################################################
    """
    Return the sha1 of the current HEAD commit

    >>> get_current_commit() is not None
    True
    """

    return run_cmd_no_fail(f"git rev-parse {'--short' if short else ''} HEAD",from_dir=repo)
