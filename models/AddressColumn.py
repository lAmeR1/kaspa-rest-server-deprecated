from sqlalchemy import TypeDecorator
from sqlalchemy.types import VARCHAR


class AddressColumn(TypeDecorator):
    impl = VARCHAR
    cache_ok = True

    PREFIX = "kaspa:"

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value[len(self.PREFIX):]
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return self.PREFIX + value
        return value
