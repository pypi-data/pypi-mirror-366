import uuid

from request_logging.middleware.RequestResponseLogging import ctx_request_id

def get_request_id():
    try:
        request_id = ctx_request_id.get()
    except LookupError:
        request_id = uuid.uuid4().hex
    return request_id