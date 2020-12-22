from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe

from http_requestor.core.models import HttpRequest, HttpResponse


@admin.register(HttpRequest)
class HttpRequestAdmin(admin.ModelAdmin):
    list_display = ["url", "method", "schedule_at", "task_id", "task_status", "httpresponse_status"]

    def httpresponse_status(self, obj):
        if obj.httpresponse:
            base_url = reverse('admin:core_httpresponse_changelist')
            status = obj.httpresponse.status_code
            return mark_safe(u'<a href="%s?request_id__exact=%d">%s</a>' % (base_url, obj.id, status))
        return ''

    httpresponse_status.short_description = _('Response Status Code')


@admin.register(HttpResponse)
class HttpResponseAdmin(admin.ModelAdmin):
    list_display = ["request", "status_code"]
