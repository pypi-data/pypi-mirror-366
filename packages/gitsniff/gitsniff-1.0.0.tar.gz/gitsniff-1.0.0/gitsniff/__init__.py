"""
GitSniff - GitHub Email Scanner for OSINT

A command-line tool for extracting email addresses from GitHub repositories
and user public events for Open Source Intelligence (OSINT).
"""

__version__ = "1.0.0"
__author__ = "WKoA"
__email__ = "reginaldgillespie@protonmail.com"
__license__ = "MIT"

from .scanner import GitHubScanner
from .utils import load_token_from_file

__all__ = ["GitHubScanner", "load_token_from_file"]