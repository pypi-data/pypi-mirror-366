"""Colección de entornos disponibles en AGI Core."""

from .env_base import AGIEnvironment, SimpleEnvironment
from .video_game import VideoGameEnvironment
from .vr import VREnvironment
from .robotics import RobotEnvironment

__all__ = [
    "AGIEnvironment",
    "SimpleEnvironment",
    "VideoGameEnvironment",
    "VREnvironment",
    "RobotEnvironment",
]
