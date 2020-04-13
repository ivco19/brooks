from django.conf import settings


def export_some_settings(request):
    context = {}

    for te in settings.TO_EXPORT:
        context[te] = getattr(settings, te, None)
    return context
