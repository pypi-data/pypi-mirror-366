"""code_validator utils module"""

from re import compile as re_compile


class CodeValidator:

    """CodeValidator"""

    @staticmethod
    def validate_js(code: str):
        """validates js code string with a regex pattern"""
        pattern = re_compile(r"^function(\s+)?\(([^)]?)+\)\s\{[\s\S]*\}$")
        matched = pattern.match(code)
        if not matched:
            raise ValueError("JS pattern not valid")
