"""
Model components for AMPGen including discriminator and MIC scorer.
"""

from .Discriminator import *
from .MICscorer import *
from .train_discriminator import *

__all__ = ["Discriminator", "MICscorer", "train_discriminator"] 