from django.core.checks import Error, register
from django.conf import settings

import sh

# =============================================================================
# CONSTANTS
# =============================================================================

with open(settings.REQUIRED_BIN_PATH) as fp:
    REQUIRED_BINS = fp.readlines()


# =============================================================================
# FUNCTIONS
# =============================================================================

@register()
def bin_installed_check(app_configs, **kwargs):
    """Check if all the listed binaries in required_bin.txt are installed"""
    errors = []
    for rbin in REQUIRED_BINS:
        try:
            sh.Command(rbin)
        except sh.CommandNotFound:
            errors.append(
                Error(
                    f"Command '{rbin}' not found",
                    hint=f"Please install '{rbin}'",
                    id='brooks.E001',
                ))
    return errors
