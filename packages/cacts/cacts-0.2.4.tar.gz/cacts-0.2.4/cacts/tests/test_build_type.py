"""Tests for the BuildType class in cacts.build_type module."""
import types

import pytest

from cacts.build_type import BuildType


@pytest.fixture
def build_type_config():  # Rename from 'build_type' to avoid redefinition
    """Create a BuildType instance for testing"""
    name = 'test_build'
    project = types.SimpleNamespace(name="TestProject")
    machine = types.SimpleNamespace(name="TestMachine", env_setup=["echo 'Setting up environment'"])
    builds_specs = {
        'default': {
            'longname': 'default_longname',
            'description': 'default_description',
            'uses_baselines': 'True',
            'on_by_default': 'True',
            'cmake_args': {'arg1': 'value1'}
        },
        'test_build': {
            'longname': 'test_longname',
            'description': 'test_description',
            'uses_baselines': 'False',
            'on_by_default': 'False',
            'cmake_args': {'arg2': 'value2'}
        }
    }
    bt = BuildType(name, project, machine, builds_specs)
    return bt


# pylint: disable=redefined-outer-name
def test_build_type_initialization(build_type_config):
    """Test BuildType initialization."""
    build_type_obj = build_type_config
    assert build_type_obj.name == 'test_build'
    assert build_type_obj.longname == 'test_longname'
    assert build_type_obj.description == 'test_description'
    # Note: BuildType uses str_to_bool internally, so these should be boolean
    assert build_type_obj.uses_baselines is False
    assert build_type_obj.on_by_default is False
    # cmake_args should merge default and specific build args
    assert 'arg1' in build_type_obj.cmake_args
    assert 'arg2' in build_type_obj.cmake_args


# pylint: disable=redefined-outer-name
def test_build_type_default_values(build_type_config):
    """Test BuildType default values."""
    build_type_obj = build_type_config
    assert build_type_obj.name == 'test_build'
    assert build_type_obj.longname == 'test_longname'
    assert build_type_obj.description == 'test_description'
    # Note: BuildType uses str_to_bool internally, so these should be boolean
    assert build_type_obj.uses_baselines is False
    assert build_type_obj.on_by_default is False


def test_invalid_build_name():
    """Test BuildType with invalid build name"""
    project = types.SimpleNamespace(name="TestProject")
    machine = types.SimpleNamespace(name="TestMachine")
    builds_specs = {
        'default': {},
        'valid_build': {}
    }

    with pytest.raises(RuntimeError,
                       match="BuildType 'invalid_build' not found"):
        BuildType('invalid_build', project, machine, builds_specs)


def test_invalid_builds_specs_type():
    """Test BuildType with invalid builds_specs type"""
    project = types.SimpleNamespace(name="TestProject")
    machine = types.SimpleNamespace(name="TestMachine")

    with pytest.raises(RuntimeError,
                       match="Error! Invalid type for build_specs arg "
                             "to BuildType constructor"):
        BuildType('test', project, machine, "not_a_dict")
