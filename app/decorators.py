import json
from uuid import UUID
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

from project_name import constants as const, utils
from uuid import UUID
from app import models

from django.db import connection, reset_queries
import time
import functools

def query_debugger(func):
 
    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        reset_queries()
        
        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func


def version_uuid(uuid):
    try:
        return UUID(uuid).version
    except ValueError:
        return None


def valid_uuid(request_function):
    def wrap(request, *args, **kwargs):
        uuid, version = None, None
        if 'uuid' in kwargs:
            uuid = kwargs["uuid"]
        elif 'kr_uuid' in kwargs:
            uuid = kwargs["kr_uuid"]
        if uuid:
            version = version_uuid(uuid)
        if not version:
            response = {
                'data': {},
                'statusCode': const.NOT_FOUND,
                'message': 'Requested data not found!',
            }

            return JsonResponse(response, safe=False)
        return request_function(request, *args, **kwargs)
    return wrap


def valid_json(request_function):
    def wrap(request, *args, **kwargs):
        
        try:
            data = json.loads(request.body)
            request.input_data = data
        except:
            response = {
                'statusCode': const.INVALID_JSON_CODE,
                'message': const.INVALID_JSON_MESSAGE,
            }

            return JsonResponse(response)
        return request_function(request, *args, **kwargs)
    return wrap