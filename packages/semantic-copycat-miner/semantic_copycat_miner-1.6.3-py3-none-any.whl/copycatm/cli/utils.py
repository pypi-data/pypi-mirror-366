"""
CLI utilities for CopycatM.
"""

import logging
from typing import Literal

VerbosityLevel = Literal["quiet", "normal", "verbose", "very_verbose", "debug"]


def get_verbosity_level(verbose: int, quiet: bool, debug: bool) -> VerbosityLevel:
    """Determine verbosity level from CLI options."""
    if quiet:
        return "quiet"
    elif debug:
        return "debug"
    elif verbose >= 3:
        return "debug"
    elif verbose == 2:
        return "very_verbose"
    elif verbose == 1:
        return "verbose"
    else:
        return "normal"


def setup_logging(verbosity: VerbosityLevel) -> None:
    """Setup logging configuration based on verbosity level."""
    log_levels = {
        "quiet": logging.ERROR,
        "normal": logging.INFO,
        "verbose": logging.INFO,
        "very_verbose": logging.DEBUG,
        "debug": logging.DEBUG,
    }
    
    logging.basicConfig(
        level=log_levels[verbosity],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Set specific logger levels
    if verbosity == "quiet":
        logging.getLogger("copycatm").setLevel(logging.ERROR)
    elif verbosity in ["verbose", "very_verbose", "debug"]:
        logging.getLogger("copycatm").setLevel(logging.DEBUG)
    else:
        logging.getLogger("copycatm").setLevel(logging.INFO) 