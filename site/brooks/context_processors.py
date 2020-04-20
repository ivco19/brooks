from django.conf import settings


def export_some_settings(request):
    context = {}

    to_export = ["DEMO_MODE"]

    for te in to_export:
        context[te] = getattr(settings, te, None)
    return context
