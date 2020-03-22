from django.core.checks import Error, register
from django.conf import settings

import sh


with open(settings.REQUIRED_BIN_PATH) as fp:
    REQUIRED_BINS = fp.readlines()


@register()
def bin_installed_check(app_configs, **kwargs):
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