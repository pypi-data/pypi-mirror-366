#!/usr/bin/env python3
"""
BloodRecon - OSINT Intelligence Gathering Tool
A comprehensive OSINT toolkit for cybersecurity professionals 
Author : Alex Butler (@VritraSecz)
Org    : Vritra Security Organization
"""

__version__ = "1.2.0"
__author__ = "Alex Butler [Vritra Security Organization]"
__email__ = "None"
__description__ = "A comprehensive OSINT toolkit for cybersecurity professionals"
__url__ = "https://github.com/VritraSecz/BloodRecon"

from .cli import main

__all__ = ['main', '__version__', '__author__', '__email__', '__description__', '__url__']
