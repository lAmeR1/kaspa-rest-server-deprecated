from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import BYTEA


class ByteColumn(TypeDecorator):
    impl = BYTEA
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.encode()
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.decode()
        return value
