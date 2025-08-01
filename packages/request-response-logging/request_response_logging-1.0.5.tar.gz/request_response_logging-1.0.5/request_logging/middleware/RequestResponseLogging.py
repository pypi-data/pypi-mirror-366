import logging
import time
import uuid
from contextvars import ContextVar

from django.http import HttpResponse
from rest_framework.response import Response

import simplejson as json
from django.conf import settings

LOGGER_NAME = getattr(settings,
                      'REQUEST_RESPONSE_LOGGING_LOGGER_NAME',
                      'request_middleware_logger')

logger = logging.getLogger(LOGGER_NAME)

REQUEST_ID_HEADER_KEY = getattr(settings, 'REQUEST_RESPONSE_ID_HEADER_KEY',
                                'X-REQUEST-ID')
ENDPOINTS_TO_IGNORE = getattr(settings, 'REQUEST_RESPONSE_LOGGING_IGNORE_LIST',
                              list())
RESPONSE_KEYS_TO_POP = [field for field in getattr(
        settings, 'REQUEST_RESPONSE_LOGGING_POP_RESPONSE_KEYS', list())]
HEALTH_CHECK_API = getattr(settings,
                           'REQUEST_RESPONSE_LOGGING_HEALTH_CHECK_API', None)
LOG_META_OPTIONS = getattr(settings,
                           'REQUEST_RESPONSE_LOGGING_META_OPTIONS', None)
LOG_META_OPTIONS_IN_RESPONSE = getattr(settings,
                           'REQUEST_RESPONSE_LOGGING_META_OPTIONS_IN_RESPONSE', False)
LOG_2XX_RESPONSES = getattr(settings, 'REQUEST_RESPONSE_LOGGING_LOG_2XX_RESPONSES', False)
HEADERS_TO_LOG = getattr(settings, 'REQUEST_RESPONSE_LOGGING_HEADERS_TO_LOG', list())

# Add new settings for conditional 2XX logging
CONDITIONAL_2XX_KEY = getattr(settings, 'REQUEST_RESPONSE_LOGGING_2XX_CONDITIONAL_KEY', None)
CONDITIONAL_2XX_VALUES = getattr(settings, 'REQUEST_RESPONSE_LOGGING_2XX_CONDITIONAL_VALUES', list())

ctx_request_id = ContextVar('request_id')


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if HEALTH_CHECK_API and request.path == HEALTH_CHECK_API:
            return HttpResponse(content='OK', status=200)

        start_time = time.time()
        request_id = uuid.uuid4().hex

        # check if endpoint is to be ignored for logging
        logging_required = request.path not in ENDPOINTS_TO_IGNORE

        # set request id context variable
        ctx_request_id.set(request.headers.get(REQUEST_ID_HEADER_KEY,
                                               request_id))

        # Add request_id to request META
        request.META[REQUEST_ID_HEADER_KEY] = ctx_request_id.get()

        # Log request parameters
        if logging_required:
            self.log_request(request)

        response = self.get_response(request)

        # Add request id to response header if not present
        if not hasattr(response, REQUEST_ID_HEADER_KEY):
            response.headers[REQUEST_ID_HEADER_KEY] = ctx_request_id.get()

        # Log response data
        if logging_required:
            self.log_response(request, response, start_time)

        try:
            if isinstance(response, Response):
                for key in RESPONSE_KEYS_TO_POP:
                    response.data.pop(key, None)
                # you need to change private attribute `_is_render`
                # to call render second time
                response._is_rendered = False
                response.render()
        except:
            pass

        return response

    def log_request(self, request):
        input_body = None
        headers_logged = {}
        try:
            if request.method == 'GET':
                input_body = json.loads(json.dumps(request.GET))
            elif request.method == 'POST':
                if request.POST:
                    input_body = json.loads(json.dumps(request.POST))
                elif request.FILES:
                    input_body = "Request contains file"
                else:
                    input_body = json.loads(request.body)
        except json.JSONDecodeError:
            error = 'Json parsing error'
            self.log_error_request(request, error)
        except Exception as e:
            error = str(e)
            self.log_error_request(request, error)

        # Log specified headers (case-insensitive)
        if HEADERS_TO_LOG and isinstance(HEADERS_TO_LOG, list):
            # Create a lowercased mapping of request headers
            request_headers_lower = {k.lower(): v for k, v in request.headers.items()}
            for header in HEADERS_TO_LOG:
                value = request_headers_lower.get(header.lower())
                if value is not None:
                    headers_logged[header] = value

        log_request = {
            "descr": "REQUEST",
            "request_method": request.META.get("REQUEST_METHOD"),
            "url_requested": request.path,
            "request_response_contents": input_body,
            "content_length": request.META.get("CONTENT_LENGTH"),
            "client_ip_address": request.META.get(
                "HTTP_X_FORWARDED_FOR") or request.META.get('REMOTE_ADDR'),
            "client_host_name": request.META.get("REMOTE_HOST"),
            "server_host_name": request.META.get("SERVER_NAME"),
            "server_port_number": request.META.get("SERVER_PORT"),
            "logged_headers": headers_logged
        }

        if LOG_META_OPTIONS and isinstance(LOG_META_OPTIONS, list):
            for key in LOG_META_OPTIONS:
                if request.META.get(key):
                    log_request.update({key: request.META[key]})


        logger.info(json.dumps(log_request))

    @staticmethod
    def log_error_request(request, error):
        request_data = None
        try:
            if request.method == 'GET':
                request_data = request.GET
            elif request.method == 'POST':
                if request.POST:
                    request_data = request.POST
                else:
                    request_data = request.body
        except:
            pass
        logger.error(f'request_data: {request_data}, '
                     f'request_error: {error}')

    def log_response(self, request, response, start_time):
        response_content = None
        should_log_2xx = False
        if response.status_code >= 400 or LOG_2XX_RESPONSES:
            try:
                if hasattr(response, 'streaming_content'):
                    response_content = "Response contains streaming response"
                elif hasattr(response, 'content'):
                    response_content = json.loads(response.content)
            except json.JSONDecodeError:
                response_error = 'Json parsing error'
                logger.error(f"response_content: {response.content}, "
                             f"response_error:{response_error}")
            except Exception as e:
                response_error = str(e)
                if hasattr(response, 'content'):
                    logger.error(f"response_content: {response.content}, "
                                 f"response_error: {response_error}")
                else:
                    logger.error(
                        f"response_content: No response content available, "
                        f"response_error: {response_error}")

        # Determine if we should log based on conditional key/values for 2XX
        if response.status_code < 400 and LOG_2XX_RESPONSES:
            should_log_2xx = True
            if CONDITIONAL_2XX_KEY and isinstance(response_content, dict):
                value = response_content.get(CONDITIONAL_2XX_KEY)
                if value not in CONDITIONAL_2XX_VALUES:
                    should_log_2xx = False

        if not should_log_2xx:
            response_content = None
        duration = round(time.time() - start_time, 3)

        log_response = {
            "descr": "RESPONSE",
            "request_response_contents": response_content,
            "response_code": response.status_code,
            "X-total-time": duration,
            "response_for_request": request.path
        }

        if LOG_META_OPTIONS_IN_RESPONSE and LOG_META_OPTIONS and \
                isinstance(LOG_META_OPTIONS, list):
            for key in LOG_META_OPTIONS:
                if request.META.get(key):
                    log_response.update({key: request.META[key]})

        if response.status_code < 400:
            logger.info(json.dumps(log_response))
        else:
            logger.error(json.dumps(log_response))
