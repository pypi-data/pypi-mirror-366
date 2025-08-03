"""
Special Relativity Grapher - A Python library for visualizing special relativity effects.

Authors: Albert Han, Stephen He, and David Zhang

This library provides tools to simulate and visualize special relativity phenomena
including time dilation, length contraction, loss of simultaneity, and classic paradoxes
like the pole-barn paradox and twin paradox.
"""

__version__ = "0.1.0"
__authors__ = ["Albert Han", "Stephen He", "David Zhang"]

from .simulation import Simulation
from .transforms import (
    getGamma,
    lorentzTranformPt,
    addVelocities,
    lorentzTransformObject,
    getEOM
)
from .visualization import (
    Minkowski,
    RelatavisticAnimation
)
from .utils import (
    trueCond,
    stopAtTime,
    stopAtEvent
)

__all__ = [
    "Simulation",
    "getGamma",
    "lorentzTranformPt", 
    "addVelocities",
    "lorentzTransformObject",
    "getEOM",
    "Minkowski",
    "RelatavisticAnimation",
    "trueCond",
    "stopAtTime", 
    "stopAtEvent"
]
