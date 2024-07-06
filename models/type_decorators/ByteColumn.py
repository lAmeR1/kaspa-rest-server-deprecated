import logging
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import BYTEA

_logger = logging.getLogger(__name__)


class ByteColumn(TypeDecorator):
    impl = BYTEA
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return int(value).to_bytes((int(value).bit_length() + 7) // 8, 'big')
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return str(int.from_bytes(value, 'big'))
            except Exception as e:
                _logger.error("Error decoding value '%s': %s", value, e)
                return ''
        return value
