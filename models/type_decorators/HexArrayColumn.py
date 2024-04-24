from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY, BYTEA


class HexArrayColumn(TypeDecorator):
    impl = ARRAY(BYTEA)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return [bytes.fromhex(v) if isinstance(v, str) else v for v in value]
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return [v.hex() for v in value]
        return value
