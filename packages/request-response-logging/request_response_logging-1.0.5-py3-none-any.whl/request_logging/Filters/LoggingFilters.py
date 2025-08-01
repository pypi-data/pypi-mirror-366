import logging
import re
import uuid
import simplejson as json
from django.conf import settings
from request_logging.middleware.RequestResponseLogging import ctx_request_id

MASKING_FIELDS = [field.upper()
                  for field in getattr(
        settings, 'REQUEST_RESPONSE_LOGGING_MASKING_FIELDS', list())]


class RequestIdFilter(logging.Filter):
    """
        Adds request id field in log record with uuid for each request
    """

    def filter(self, record):
        record.request_id = ctx_request_id.get(uuid.uuid4().hex)
        return True


class MaskingFilter(logging.Filter):
    """
    Masks data in log based on list of fields provided in
    settings.REQUEST_ID_MASKING_FIELDS
    """

    def filter(self, record):
        try:
            if MASKING_FIELDS:
                msg = json.loads(record.msg)
                if isinstance(msg.get('request_response_contents'),
                              (list, dict)):
                    mask_sensitive_data(msg.get('request_response_contents'), MASKING_FIELDS)
                record.msg = json.dumps(msg)
        except Exception as _:
            pass
        return True

def mask_sensitive_data(data, fields_to_mask):
    if isinstance(data, dict):
        for key, value in data.items():
            if key.upper() in fields_to_mask:
                data[key] = "***"
            elif isinstance(value, (dict, list)):
                mask_sensitive_data(value, fields_to_mask)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                mask_sensitive_data(item, fields_to_mask)
