"""Jubilant-backports extends Jubilant to include support for Juju 2.9."""

# Re-export everything from Jubilant that isn't getting extra functionality in Jubilant-backports.

from jubilant import (
    CLIError,
    ConfigValue,
    SecretURI,
    WaitError,
)

from . import statustypes
from ._all_any import (
    all_active,
    all_agents_idle,
    all_blocked,
    all_error,
    all_maintenance,
    all_waiting,
    any_active,
    any_blocked,
    any_error,
    any_maintenance,
    any_waiting,
)
from ._juju import Juju29 as Juju
from ._task import ExecTask29 as ExecTask  # Note that this is not present in Jubilant.
from ._task import Task29 as Task
from ._task import TaskError29 as TaskError
from ._test_helpers import temp_model
from .statustypes import Status

__all__ = [
    'CLIError',
    'ConfigValue',
    'ExecTask',
    'Juju',
    'SecretURI',
    'Status',
    'Task',
    'TaskError',
    'WaitError',
    'all_active',
    'all_agents_idle',
    'all_blocked',
    'all_error',
    'all_maintenance',
    'all_waiting',
    'any_active',
    'any_blocked',
    'any_error',
    'any_maintenance',
    'any_waiting',
    'statustypes',
    'temp_model',
]

__version__ = '1.0.0a1'
