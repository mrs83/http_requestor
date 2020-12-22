import sys
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from celery import states
from celery.result import AsyncResult, allow_join_result

from .fields import JSONField


def validate_schedule_at(value):
    if value < timezone.now():
        raise ValidationError("Request schedule cannot be in the past!")
    return value


class HttpRequest(models.Model):
    GET = 'get'
    HEAD = 'head'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'

    METHOD_CHOICES = (
        (GET, _('Get')),
        (HEAD, _('Head')),
        (POST, _('Post')),
        (PUT, _('Put')),
        (DELETE, _('Delete')),
    )

    url = models.URLField()
    method = models.CharField(max_length=8, choices=METHOD_CHOICES)
    headers = JSONField(blank=True)
    params = JSONField(blank=True)
    data = JSONField(blank=True)
    schedule_at = models.DateTimeField(validators=[validate_schedule_at])
    task_id = models.CharField(max_length=36, blank=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def task_status(self):
        if not self.task_id:
            return states.PENDING
        if self.httpresponse:
            return states.SUCCESS
        in_celery = sys.argv and sys.argv[0].endswith('celery') and 'worker' in sys.argv
        if in_celery:
            with allow_join_result():
                result = AsyncResult(self.task_id)
        else:
            result = AsyncResult(self.task_id)
        return result.state

    def __str__(self):
        return f'{self.url} ({self.method}) at {self.schedule_at}'


class HttpResponse(models.Model):
    request = models.OneToOneField(HttpRequest, on_delete=models.CASCADE)
    status_code = models.PositiveIntegerField()
    headers = JSONField()
    text = models.TextField(blank=True)

    def __str__(self):
        return f'Response from url {self.request} ({self.request.method}): {self.status_code}'
