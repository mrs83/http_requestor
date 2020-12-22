import json
import requests
from celery.utils.log import get_logger
from config import celery_app
from http_requestor.core.models import HttpRequest, HttpResponse

logger = get_logger(__name__)
METHOD_CHOICES = {choice[0] for choice in HttpRequest.METHOD_CHOICES}


@celery_app.task()
def http_request(url, method='GET', timeout=2, **kwargs):
    """Generic task to make an http request."""
    headers = kwargs.get('headers', {})
    params = kwargs.get('params', {})
    data = kwargs.get('data', {})
    request_kwargs = {}
    if headers:
        request_kwargs['headers'] = headers
    if params:
        request_kwargs['params'] = params
    if method in ['post', 'put']:
        request_kwargs['data'] = data

    s = requests.Session()
    if method not in METHOD_CHOICES:
        raise ValueError(f'{method} not supported!')
    method = method.lower()
    request = getattr(s, method)
    try:
        response = request(url, timeout=timeout, **request_kwargs)
        # response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception('%s request to url %s failed!', method, url)
        return None
    else:
        logger.info('%s request to url %s successfull!', method, url)
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'text': response.text
        }


@celery_app.task()
def store_result(result, request_id):
    if not result:
        return
    request = HttpRequest.objects.get(id=request_id)
    response = HttpResponse(
        request=request,
        status_code=result['status_code'],
        headers=json.dumps(result['headers']),
        text=result['text']
    )
    response.save()


def schedule_http_request_for_instance(request):
    result = http_request.apply_async([request.url], {
        'method': request.method,
        'headers': request.headers,
        'params': request.params,
        'data': request.data
    }, eta=request.schedule_at, link=store_result.s(request.id))
    return result
