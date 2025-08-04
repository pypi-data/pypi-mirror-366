"""Parameter validation utilities for ESO Logs API client."""

import re
from datetime import datetime
from typing import Any, Optional, Union

from esologs._generated.base_model import UNSET, UnsetType


class ValidationError(Exception):
    """Validation error for API parameters."""

    pass


# Security constants
MAX_STRING_LENGTH = 1000  # Prevent DoS via large strings
MAX_GUILD_NAME_LENGTH = 100  # Reasonable guild name limit
MAX_SERVER_SLUG_LENGTH = 50  # Reasonable server slug limit


def validate_string_length(
    value: str, field_name: str, max_length: int = MAX_STRING_LENGTH
) -> None:
    """
    Validate string length to prevent DoS attacks and ensure reasonable input sizes.

    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length

    Raises:
        ValidationError: If string is too long
    """
    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} exceeds maximum length of {max_length} characters"
        )


def sanitize_api_key_from_error(error_message: str) -> str:
    """
    Sanitize error messages to prevent API key exposure.

    Args:
        error_message: Original error message

    Returns:
        Sanitized error message with potential API keys masked
    """
    # Pattern to match potential API keys (32+ character alphanumeric strings)
    api_key_pattern = r"[a-zA-Z0-9]{32,}"

    def mask_key(match: re.Match[str]) -> str:
        key = match.group(0)
        if len(key) >= 32:  # Likely an API key
            return f"{key[:4]}...{key[-4:]}"
        return key

    return re.sub(api_key_pattern, mask_key, error_message)


def validate_report_code(code: str) -> None:
    """
    Validate report code format.

    Args:
        code: The report code to validate

    Raises:
        ValidationError: If the code format is invalid
    """
    if not code:
        raise ValidationError("Report code cannot be empty")

    if not isinstance(code, str):
        raise ValidationError("Report code must be a string")

    # ESO Logs report codes are typically alphanumeric
    if not re.match(r"^[a-zA-Z0-9]+$", code):
        raise ValidationError("Report code must contain only alphanumeric characters")

    if len(code) < 3:
        raise ValidationError("Report code must be at least 3 characters long")


def validate_ability_id(ability_id: Optional[Union[float, int]]) -> None:
    """
    Validate ability ID parameter.

    Args:
        ability_id: The ability ID to validate

    Raises:
        ValidationError: If the ability ID is invalid
    """
    if ability_id is None:
        return

    if not isinstance(ability_id, (int, float)):
        raise ValidationError("Ability ID must be a number")

    if ability_id <= 0:
        raise ValidationError("Ability ID must be positive")

    # Check if it's a whole number (even if passed as float)
    if isinstance(ability_id, float) and not ability_id.is_integer():
        raise ValidationError("Ability ID should be a whole number")


def validate_time_range(
    start_time: Union[Optional[float], UnsetType],
    end_time: Union[Optional[float], UnsetType],
) -> None:
    """
    Validate time range parameters.

    Args:
        start_time: Start time timestamp
        end_time: End time timestamp

    Raises:
        ValidationError: If the time range is invalid
    """
    if (
        start_time is not None
        and start_time is not UNSET
        and not isinstance(start_time, (int, float))
    ):
        raise ValidationError("Start time must be a number")

    if (
        end_time is not None
        and end_time is not UNSET
        and not isinstance(end_time, (int, float))
    ):
        raise ValidationError("End time must be a number")

    if (
        start_time is not None
        and start_time is not UNSET
        and isinstance(start_time, (int, float))
        and start_time < 0
    ):
        raise ValidationError("Start time cannot be negative")

    if (
        end_time is not None
        and end_time is not UNSET
        and isinstance(end_time, (int, float))
        and end_time < 0
    ):
        raise ValidationError("End time cannot be negative")

    if (
        start_time is not None
        and start_time is not UNSET
        and isinstance(start_time, (int, float))
        and end_time is not None
        and end_time is not UNSET
        and isinstance(end_time, (int, float))
        and start_time >= end_time
    ):
        raise ValidationError("Start time must be less than end time")


def validate_positive_integer(value: Optional[int], param_name: str) -> None:
    """
    Validate that a parameter is a positive integer.

    Args:
        value: The value to validate
        param_name: Name of the parameter for error messages

    Raises:
        ValidationError: If the value is invalid
    """
    if value is None:
        return

    if not isinstance(value, int):
        raise ValidationError(f"{param_name} must be an integer")

    if value <= 0:
        raise ValidationError(f"{param_name} must be positive")


def validate_limit_parameter(limit: Optional[int]) -> None:
    """
    Validate limit parameter for pagination.

    Args:
        limit: The limit value to validate

    Raises:
        ValidationError: If the limit is invalid
    """
    if limit is None:
        return

    if not isinstance(limit, int):
        raise ValidationError("Limit must be an integer")

    if limit <= 0:
        raise ValidationError("Limit must be positive")

    if limit > 10000:  # ESO Logs API maximum allowed limit
        raise ValidationError("Limit cannot exceed 10,000")


def validate_fight_ids(fight_ids: Optional[list]) -> None:
    """
    Validate fight IDs parameter.

    Args:
        fight_ids: List of fight IDs to validate

    Raises:
        ValidationError: If the fight IDs are invalid
    """
    if fight_ids is None:
        return

    if not isinstance(fight_ids, list):
        raise ValidationError("Fight IDs must be a list")

    for fight_id in fight_ids:
        if fight_id is not None and not isinstance(fight_id, int):
            raise ValidationError("Fight ID must be an integer")

        if fight_id is not None and fight_id <= 0:
            raise ValidationError("Fight ID must be positive")


def validate_required_string(value: Any, param_name: str) -> None:
    """
    Validate that a required parameter is a non-empty string.

    Args:
        value: The value to validate
        param_name: Name of the parameter for error messages

    Raises:
        ValidationError: If the value is invalid
    """
    if value is None:
        raise ValidationError(f"{param_name} is required")

    if not isinstance(value, str):
        raise ValidationError(f"{param_name} must be a string")

    if not value.strip():
        raise ValidationError(f"{param_name} cannot be empty")


def validate_report_search_params(
    guild_name: Union[Optional[str], UnsetType] = None,
    guild_server_slug: Union[Optional[str], UnsetType] = None,
    guild_server_region: Union[Optional[str], UnsetType] = None,
    limit: Union[Optional[int], UnsetType] = None,
    page: Union[Optional[int], UnsetType] = None,
    **kwargs: Any,
) -> None:
    """
    Validate report search parameters.

    Args:
        guild_name: Guild name (requires server slug and region)
        guild_server_slug: Guild server slug
        guild_server_region: Guild server region
        limit: Results per page limit
        page: Page number
        **kwargs: Additional parameters

    Raises:
        ValidationError: If parameters are invalid
    """
    # Validate guild name requirements with security checks
    if guild_name is not None and guild_name is not UNSET:
        if (
            guild_server_slug is None
            or guild_server_slug is UNSET
            or guild_server_region is None
            or guild_server_region is UNSET
        ):
            raise ValidationError(
                "guild_name requires both guild_server_slug and guild_server_region"
            )
        validate_required_string(guild_name, "guild_name")
        if isinstance(guild_name, str):
            validate_string_length(guild_name, "guild_name", MAX_GUILD_NAME_LENGTH)
        validate_required_string(guild_server_slug, "guild_server_slug")
        if isinstance(guild_server_slug, str):
            validate_string_length(
                guild_server_slug, "guild_server_slug", MAX_SERVER_SLUG_LENGTH
            )
        validate_required_string(guild_server_region, "guild_server_region")

    # Validate limit (ESO Logs API allows 1-25 for reports)
    if limit is not None and limit is not UNSET:
        if not isinstance(limit, int):
            raise ValidationError("Limit must be an integer")
        if limit < 1 or limit > 25:
            raise ValidationError("Limit must be between 1 and 25")

    # Validate page number
    if page is not None and page is not UNSET:
        if not isinstance(page, int):
            raise ValidationError("page must be an integer")
        validate_positive_integer(page, "page")

    # Validate time range if either are provided
    start_time = kwargs.get("start_time", UNSET)
    end_time = kwargs.get("end_time", UNSET)
    if (start_time is not None and start_time is not UNSET) or (
        end_time is not None and end_time is not UNSET
    ):
        validate_time_range(start_time, end_time)


def parse_date_to_timestamp(date_input: Union[str, datetime, float, int]) -> float:
    """
    Convert various date formats to UNIX timestamp with milliseconds.

    Args:
        date_input: Date in various formats (string, datetime, timestamp)

    Returns:
        float: UNIX timestamp with millisecond precision

    Raises:
        ValidationError: If date format is invalid

    Examples:
        # String dates
        parse_date_to_timestamp("2023-01-01")
        parse_date_to_timestamp("2023-01-01T12:00:00")

        # Datetime object
        parse_date_to_timestamp(datetime(2023, 1, 1))

        # Timestamp (seconds or milliseconds)
        parse_date_to_timestamp(1672531200)
        parse_date_to_timestamp(1672531200000)
    """
    if isinstance(date_input, (int, float)):
        # Validate timestamp bounds (allow Unix epoch for testing)
        # Allow from Unix epoch (1970) to future dates
        MIN_TIMESTAMP_SECONDS = 0  # Unix epoch (Jan 1, 1970 UTC)
        MAX_TIMESTAMP_SECONDS = 4102444800  # Jan 1, 2100 UTC

        # Assume it's already a timestamp
        # If it's too small, assume it's in seconds and convert to milliseconds
        if date_input < 1e10:  # Less than 10 billion (seconds format)
            if date_input < MIN_TIMESTAMP_SECONDS:
                raise ValueError(f"Timestamp {date_input} is before Unix epoch (1970)")
            if date_input > MAX_TIMESTAMP_SECONDS:
                raise ValueError(f"Timestamp {date_input} is after year 2100")
            return float(date_input * 1000)
        else:  # Milliseconds format
            if date_input < MIN_TIMESTAMP_SECONDS * 1000:
                raise ValueError(f"Timestamp {date_input} is before Unix epoch (1970)")
            if date_input > MAX_TIMESTAMP_SECONDS * 1000:
                raise ValueError(f"Timestamp {date_input} is after year 2100")
            return float(date_input)

    if isinstance(date_input, datetime):
        return date_input.timestamp() * 1000

    if isinstance(date_input, str):
        try:
            # Try common date formats
            for fmt in [
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%SZ",
            ]:
                try:
                    dt = datetime.strptime(date_input, fmt)
                    return dt.timestamp() * 1000
                except ValueError:
                    continue

            # Try to parse as timestamp string
            timestamp = float(date_input)
            return parse_date_to_timestamp(timestamp)

        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid date format: {date_input}. "
                "Use YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, or timestamp"
            ) from e

    raise ValidationError(f"Unsupported date type: {type(date_input)}")


def validate_guild_search_params(
    guild_id: Optional[int] = None,
    guild_name: Optional[str] = None,
    guild_server_slug: Optional[str] = None,
    guild_server_region: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Validate guild identification parameters for search.

    Args:
        guild_id: Guild ID
        guild_name: Guild name
        guild_server_slug: Guild server slug
        guild_server_region: Guild server region
        **kwargs: Additional parameters

    Raises:
        ValidationError: If parameters are invalid
    """
    # Must provide either guild_id OR complete guild name info
    has_guild_id = guild_id is not None
    has_guild_name_info = all(
        x is not None for x in [guild_name, guild_server_slug, guild_server_region]
    )

    if not has_guild_id and not has_guild_name_info:
        return  # No guild filtering is fine

    if has_guild_id and has_guild_name_info:
        raise ValidationError(
            "Provide either guild_id OR guild_name with server info, not both"
        )

    if guild_id is not None:
        validate_positive_integer(guild_id, "guild_id")

    if guild_name is not None:
        validate_string_length(guild_name, "guild_name", MAX_GUILD_NAME_LENGTH)
        validate_report_search_params(
            guild_name=guild_name,
            guild_server_slug=guild_server_slug,
            guild_server_region=guild_server_region,
        )
