from .version import __version__
from .contrast_reserve import contrast_reserve, optimal_detection_magnification, surface_brightness
from .magnitude import nelm_to_sqm, nelm_to_bortle, sqm_to_nelm, sqm_to_bortle, bortle_to_nelm, bortle_to_sqm
from .deepskylog_interface import (dsl_instruments, dsl_eyepieces, dsl_lenses, dsl_filters,
                                   calculate_magnifications,
                                   convert_instrument_type_to_string, convert_instrument_type_to_int)
from .logging_config import configure_logging
import logging

configure_logging(logging.WARNING)

__all__ = ["__version__", "contrast_reserve", "optimal_detection_magnification", "surface_brightness", "nelm_to_sqm",
           "nelm_to_bortle", "sqm_to_nelm", "sqm_to_bortle", "bortle_to_nelm", "bortle_to_sqm", "dsl_instruments",
           "dsl_eyepieces", "dsl_lenses", "dsl_filters",
           "calculate_magnifications", "convert_instrument_type_to_string",
           "convert_instrument_type_to_int"]
