from django.db.models.signals import post_save
from django.dispatch import receiver
from http_requestor.core.models import HttpRequest
from http_requestor.core.tasks import schedule_http_request_for_instance


@receiver(post_save, sender=HttpRequest)
def schedule_http_request(sender, instance, created, **kwargs):
    if created and not instance.task_id:
        result = schedule_http_request_for_instance(instance)
        task_id = result.task_id
        instance.task_id = task_id
        instance.save()
