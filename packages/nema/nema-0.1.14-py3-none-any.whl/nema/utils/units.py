import pint

try:
    from pint.delegates.formatter.plain import DefaultFormatter as DefaultPintFormatter

    UNIT_REGISTRY = pint.UnitRegistry()
    DEFAULT_PINT_FORMATTER = DefaultPintFormatter()
    DEFAULT_PINT_FORMATTER._registry = UNIT_REGISTRY

    def format_unit_str_for_backend(units: pint.Unit):
        return (
            DEFAULT_PINT_FORMATTER.format_unit(units, "~")
            .replace(" ", "")
            .replace("**", "^")
        )

except ImportError:
    UNIT_REGISTRY = pint.UnitRegistry()
    DEFAULT_PINT_FORMATTER = None

    def format_unit_str_for_backend(units: pint.Unit):
        return format(units, "~").replace(" ", "").replace("**", "^")
