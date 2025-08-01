"""Tests for the Machine class in cacts.machine module."""
import types

import pytest

from cacts.machine import Machine


@pytest.fixture
def machine_config():  # Rename from 'machine' to avoid redefinition
    """Create a Machine instance for testing"""
    project = types.SimpleNamespace(name="TestProject")
    machines_specs = {
        'default': {
            'num_bld_res': 4,
            'num_run_res': 8,
            'env_setup': ['echo "Setting up environment"']
        },
        'test_machine': {
            'num_bld_res': 2,
            'num_run_res': 4,
            'env_setup': ['echo "Setting up test environment"']
        }
    }
    return Machine('test_machine', project, machines_specs)


# pylint: disable=redefined-outer-name
def test_machine_initialization(machine_config):
    """Test Machine initialization."""
    machine_obj = machine_config
    assert machine_obj.name == 'test_machine'
    assert machine_obj.num_bld_res == 2
    assert machine_obj.num_run_res == 4
    assert machine_obj.env_setup == ['echo "Setting up test environment"']


# pylint: disable=redefined-outer-name
def test_machine_uses_gpu(machine_config):
    """Test Machine uses_gpu method"""
    machine_obj = machine_config
    # Initially should not use GPU
    assert machine_obj.uses_gpu() is False

    # After setting gpu_arch, should use GPU
    machine_obj.gpu_arch = 'test_gpu_arch'
    assert machine_obj.uses_gpu() is True


def test_invalid_machine_name():
    """Test Machine with invalid machine name"""
    project = types.SimpleNamespace(name="TestProject")
    machines_specs = {
        'default': {},
        'valid_machine': {}
    }

    with pytest.raises(RuntimeError, match="Machine 'invalid_machine' not found"):
        Machine('invalid_machine', project, machines_specs)


def test_invalid_machines_specs_type():
    """Test Machine with invalid machines_specs type"""
    project = types.SimpleNamespace(name="TestProject")

    with pytest.raises(RuntimeError, match="Machine constructor expects a dict object"):
        Machine('test', project, "not_a_dict")
