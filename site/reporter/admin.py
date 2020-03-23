from django.contrib import admin

from solo.admin import SingletonModelAdmin

from reporter.models import ReportConfiguration


admin.site.register(ReportConfiguration, SingletonModelAdmin)
