from typing import Union


class Tools:
    @staticmethod
    def generate_random_token(length: int) -> str:
        import secrets
        return secrets.token_hex(length)

    @staticmethod
    def check_for_none(value: str) -> Union[str, None]:
        str_values = ["null", "none", "undefined", ""]

        if isinstance(value, str):
            if value.lower() in str_values:
                return None

        if value is None:
            return None

        return value
