import torch
from collections.abc import Iterable
from dataclasses import MISSING
from typing import Literal, TYPE_CHECKING

from omni.isaac.lab.utils import configclass
from omni.isaac.lab.actuators import IdealPDActuatorCfg

from .actuator_pd import IdentifiedActuator


@configclass
class IdentifiedActuatorCfg(IdealPDActuatorCfg):
    """Configuration for direct control (DC) motor actuator model."""

    class_type: type = IdentifiedActuator

    friction_torque: float = MISSING
    """ (in N-m)."""
    activation_vel: float = MISSING
    """ (in Rad/s)."""
    friction_vel: float = MISSING
    """ (in N-m-s/Rad)."""
