import datetime as dt
from typing import Any

from clickup_sdk.core import models


def microseconds_string_to_date(
    microseconds_string: str | None,
) -> dt.date | None:
    if not microseconds_string:
        return None
    try:
        return dt.datetime.fromtimestamp(
            timestamp=int(microseconds_string) / 1000,
            tz=dt.UTC,
        ).date()
    except ValueError:
        return None


def get_custom_field_value(
    custom_field: dict[str, Any],
):
    custom_field_type = custom_field["type"]
    value = custom_field.get("value")
    if custom_field_type != "drop_down":
        if value is not None:
            match custom_field_type:
                case "date":
                    custom_field_value = microseconds_string_to_date(
                        microseconds_string=value,
                    )
                case "number":
                    custom_field_value = float(value)
                case "currency":
                    custom_field_value = round(
                        number=float(value),
                        ndigits=2,
                    )
                case _:
                    custom_field_value = value
        else:
            custom_field_value = value
    elif custom_field_type == "drop_down":
        type_config = custom_field["type_config"]
        drop_down_type_config = models.DropDownTypeConfig(**type_config)
        option: int | None = (
            value if value is not None else drop_down_type_config.default
        )
        if option is None:
            custom_field_value = None
        else:
            custom_field_value = drop_down_type_config.options[option].name
    else:
        custom_field_value = value
    return custom_field_value
