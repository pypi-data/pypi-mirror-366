import logging
from datetime import datetime
from typing import Annotated, Any, cast

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Atlassian
from arcade_tdk.errors import RetryableToolError, ToolExecutionError

from arcade_jira.client import APIType, JiraClient
from arcade_jira.constants import BOARD_TYPES_WITH_SPRINTS, SprintState
from arcade_jira.tools.boards import get_boards
from arcade_jira.utils import (
    build_sprint_params,
    clean_sprint_dict,
    convert_date_string_to_date,
    create_error_entry,
    create_sprint_result_dict,
    is_valid_date_string,
    resolve_cloud_id_and_name,
    validate_sprint_limit,
)

logger = logging.getLogger(__name__)

# Error message constants to comply with TRY003
SPECIFIC_DATE_FORMAT_ERROR = "Invalid specific_date format. Expected YYYY-MM-DD format."
START_DATE_FORMAT_ERROR = "Invalid start_date format. Expected YYYY-MM-DD format."
END_DATE_FORMAT_ERROR = "Invalid end_date format. Expected YYYY-MM-DD format."

# Error message constants
CONFLICTING_DATE_PARAMS_ERROR = (
    "Cannot use specific_date together with start_date or end_date. "
    "Use either specific_date alone for exact date, or start_date/end_date for range."
)


@tool(
    requires_auth=Atlassian(
        scopes=[
            "read:board-scope:jira-software",  # /board, /board/{boardId} (via get_boards)
            "read:project:jira",  # project info from /board responses (via get_boards)
            "read:sprint:jira-software",  # /board/{boardId}/sprint
            "read:issue-details:jira",  # issue metadata in /board/{boardId}, /board responses
            # administrative access to /board/{boardId}/sprint
            "read:board-scope.admin:jira-software",
        ]
    )
)
async def list_sprints_for_boards(
    context: ToolContext,
    board_identifiers_list: Annotated[
        list[str] | None,
        "List of board names or numeric IDs (as strings) to retrieve sprints from. "
        "Include all mentioned boards in a single list for best performance. "
        "Optional, defaults to None.",
    ] = None,
    max_sprints_per_board: Annotated[
        int,
        "Maximum sprints per board (1-50). Latest sprints first. Optional, defaults to 50.",
    ] = 50,
    offset: Annotated[
        int,
        "Number of sprints to skip per board for pagination. Optional, defaults to 0.",
    ] = 0,
    state: Annotated[
        SprintState | None,
        "Filter by sprint state using SprintState enum value. Available options: "
        "SprintState.FUTURE (future sprints), SprintState.ACTIVE (active sprints), "
        "SprintState.CLOSED (closed sprints), SprintState.FUTURE_AND_ACTIVE (future + active), "
        "SprintState.FUTURE_AND_CLOSED (future + closed), "
        "SprintState.ACTIVE_AND_CLOSED (active + closed), SprintState.ALL (all states). "
        "Optional, defaults to None (all states).",
    ] = None,
    start_date: Annotated[
        str | None,
        "Start date filter in YYYY-MM-DD format. Can combine with end_date. "
        "Optional, defaults to None.",
    ] = None,
    end_date: Annotated[
        str | None,
        "End date filter in YYYY-MM-DD format. Can combine with start_date. "
        "Optional, defaults to None.",
    ] = None,
    specific_date: Annotated[
        str | None,
        "Specific date in YYYY-MM-DD to find sprints active on that date. "
        "Cannot combine with start_date/end_date. Optional, defaults to None.",
    ] = None,
    atlassian_cloud_id: Annotated[
        str | None,
        "Atlassian Cloud ID to use. Optional, defaults to None (uses single authorized cloud).",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Dict with 'boards' list, 'sprints_by_board' mapping, and 'errors' array. "
    "Sprints sorted latest first.",
]:
    """
    Retrieve sprints from Jira boards with filtering options for planning and tracking purposes.

    Use this when you need to view sprints from specific boards, filter by sprint states
    (active, future, closed), or find sprints within specific date ranges. Leave
    board_identifiers_list as None to get sprints from all available boards.

    Returns sprint data along with a backlog GUI URL link where you can see detailed sprint
    information and manage sprint items.

    MANDATORY ACTION: ALWAYS when you need to get sprints from multiple boards, you must
    include all the board identifiers in a single call rather than making
    multiple separate tool calls, as this provides much better performance, not doing that will
    bring huge performance penalties.

    The tool supports flexible date filtering - use start_date/end_date for ranges,
    specific_date for historical lookups, or state filters for current sprint status.
    Handles mixed board identifiers (names and IDs) with automatic fallback and deduplication.
    """
    # Validate all parameters first (with proper error handling)
    # Convert enum state to API format
    api_states = state.to_api_value() if state else None

    _validate_parameters(board_identifiers_list, specific_date, start_date, end_date, api_states)

    max_sprints_per_board = validate_sprint_limit(max_sprints_per_board)
    cloud_data = await resolve_cloud_id_and_name(context, atlassian_cloud_id)
    client = JiraClient(context, cloud_data["cloud_id"], client_type=APIType.AGILE)

    results: dict[str, Any] = {
        "boards": [],
        "sprints_by_board": {},
        "errors": [],
    }

    # Get boards by ID or name using the boards tool
    board_response = await get_boards(
        context, board_identifiers_list, atlassian_cloud_id=cloud_data["cloud_id"]
    )

    # If board_identifiers_list is empty, use all returned board IDs
    boards_to_process = (
        board_identifiers_list
        if board_identifiers_list
        else [str(board["id"]) for board in board_response.get("boards", [])]
    )

    # Process each board ID
    for board_id in boards_to_process:
        board_result = await _process_single_board(
            context,
            client,
            board_id,
            board_response,
            offset,
            max_sprints_per_board,
            api_states,
            start_date,
            end_date,
            specific_date,
            cloud_data["cloud_name"],
        )

        # Merge the non-mutating results
        results["boards"].extend(board_result["boards"])
        results["sprints_by_board"].update(board_result["sprints_by_board"])
        results["errors"].extend(board_result["errors"])

    return results


def _find_board_in_response(board_id: str, board_response: dict[str, Any]) -> dict[str, Any] | None:
    """
    Find a specific board from the board response that matches the given board_id.

    Args:
        board_id: Board identifier to search for
        board_response: Response from get_boards containing list of boards

    Returns:
        Board info dictionary if found, None otherwise
    """
    if not board_response["boards"]:
        return None

    for board in board_response["boards"]:
        # Check if board_id matches either the ID or name
        if (
            str(board["id"]) == str(board_id)
            or board.get("name", "").casefold() == board_id.casefold()
        ):
            return board  # type: ignore[no-any-return]
    return None


def _handle_board_not_found(
    board_id: str, board_response: dict[str, Any], results: dict[str, Any]
) -> None:
    """
    Handle case when board is not found and add appropriate error to results.

    Args:
        board_id: Board identifier that wasn't found
        board_response: Response from get_boards
        results: Results dictionary to update with error
    """
    if board_response["errors"]:
        # Board not found, add the existing errors to our results
        results["errors"].extend(board_response["errors"])
    else:
        # Unexpected case - no boards and no errors
        error_entry = create_error_entry(
            board_id,
            f"Board '{board_id}' could not be resolved",
        )
        results["errors"].append(error_entry)


async def _process_board_sprints(
    client: JiraClient,
    board_info: dict[str, Any],
    board_id: str,
    offset: int,
    max_sprints_per_board: int,
    state: list[str] | None,
    start_date: str | None,
    end_date: str | None,
    specific_date: str | None,
    results: dict[str, Any],
    cloud_name: str,
) -> None:
    """
    Process sprints for a single board and add results.

    Args:
        client: JiraClient instance for API calls
        board_info: Board information dictionary
        board_id: Original board identifier
        offset: Number of sprints to skip
        max_sprints_per_board: Maximum sprints per board
        state: Optional state filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        specific_date: Optional specific date filter
        results: Results dictionary to update
        cloud_name: The name of the Atlassian Cloud to use for API calls
    """
    board_id_resolved = board_info["id"]

    # Check if board supports sprints and get final type, fetch sprints in one call
    params = build_sprint_params(offset, max_sprints_per_board, state)
    supports_sprints, final_type, response = await _try_fetch_sprints_and_determine_type(
        client, board_info, cast(dict[str, Any], params)
    )

    if not supports_sprints:
        error_entry = create_error_entry(
            board_id,
            f"Board '{board_info.get('name', board_id)}' does not support sprints "
            f"(type: {board_info.get('type', 'unknown')}). "
            f"Only Scrum boards support sprints.",
            board_info.get("name", "Unknown"),
            board_id_resolved,
        )
        results["errors"].append(error_entry)
        return

    # Update board type if it changed (simple -> scrum)
    board_info["type"] = final_type

    # Process the sprints we already fetched
    if response is None:
        # This should not happen if supports_sprints is True, but handle it gracefully
        error_entry = create_error_entry(
            board_id,
            f"Unexpected error: No sprint data received for board "
            f"'{board_info.get('name', board_id)}'",
            board_info.get("name", "Unknown"),
            board_id_resolved,
        )
        results["errors"].append(error_entry)
        return

    sprints = [clean_sprint_dict(s, cloud_name) for s in response.get("values", [])]

    # Apply date filtering if specified
    if start_date or end_date or specific_date:
        sprints = _filter_sprints_by_date(sprints, start_date, end_date, specific_date)

    # Sort sprints with latest first (by end date, then start date, then ID)
    sprints = _sort_sprints_latest_first(sprints)

    results["boards"].append(board_info)
    results["sprints_by_board"][board_id_resolved] = create_sprint_result_dict(
        board_info, sprints, response, cloud_name
    )


async def _process_single_board(
    context: ToolContext,
    client: JiraClient,
    board_id: str,
    board_response: dict[str, Any],
    offset: int,
    max_sprints_per_board: int,
    state: list[str] | None,
    start_date: str | None,
    end_date: str | None,
    specific_date: str | None,
    cloud_name: str,
) -> dict[str, Any]:
    """
    Process a single board and return results without mutating input.

    Args:
        context: Tool context for authentication
        client: JiraClient instance for API calls
        board_id: Board identifier to process
        board_response: Board response from get_boards
        offset: Number of sprints to skip
        max_sprints_per_board: Maximum sprints per board
        state: Optional state filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        specific_date: Optional specific date filter
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Dictionary with processed results: {'boards': [...], 'sprints_by_board': {...},
        'errors': [...]}
    """
    # Initialize result structure (copy pattern)
    result: dict[str, Any] = {
        "boards": [],
        "sprints_by_board": {},
        "errors": [],
    }

    try:
        # Find the board in the response
        board_info = _find_board_in_response(board_id, board_response)

        if not board_info:
            _handle_board_not_found(board_id, board_response, result)
            return result

        # Process the board's sprints
        await _process_board_sprints(
            client,
            board_info,
            board_id,
            offset,
            max_sprints_per_board,
            state,
            start_date,
            end_date,
            specific_date,
            result,
            cloud_name,
        )

    except ToolExecutionError:
        # Re-raise ToolExecutionErrors as-is
        raise
    except Exception as e:
        error_entry = create_error_entry(
            board_id,
            f"Unexpected error processing board '{board_id}': {e!s}",
        )
        result["errors"].append(error_entry)

    return result


async def _try_fetch_sprints_and_determine_type(
    client: JiraClient, board_info: dict[str, Any], params: dict[str, Any]
) -> tuple[bool, str, dict[str, Any] | None]:
    """
    Try to fetch sprints for a board and determine if it supports sprints.

    Args:
        client: JiraClient instance for API calls
        board_info: Board information dictionary
        params: Parameters for sprint API call

    Returns:
        Tuple of (supports_sprints, final_board_type, response)
    """
    board_id = board_info["id"]
    board_type = board_info.get("type", "").lower()

    # If already known to support sprints, fetch directly
    if board_type in BOARD_TYPES_WITH_SPRINTS:
        try:
            response = await client.get(f"/board/{board_id}/sprint", params=params)
        except Exception:
            return False, board_type, None
        else:
            return True, board_type, response

    # For 'simple' boards or unknown types, try fetching to see if it works
    try:
        response = await client.get(f"/board/{board_id}/sprint", params=params)
    except Exception:
        # Board doesn't support sprints
        return False, board_type, None
    else:
        # If successful, it's actually a scrum board
        return True, "scrum", response


def _filter_sprints_by_date(
    sprints: list[dict], start_date: str | None, end_date: str | None, specific_date: str | None
) -> list[dict]:
    """
    Filter sprints by date range or specific date.

    Args:
        sprints: List of sprint dictionaries
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
        specific_date: Specific date string in YYYY-MM-DD format

    Returns:
        Filtered list of sprints
    """
    if not sprints:
        return sprints

    if specific_date:
        return _filter_sprints_by_specific_date(sprints, specific_date)
    elif start_date or end_date:
        return _filter_sprints_by_date_range(sprints, start_date, end_date)

    return sprints


def _filter_sprints_by_specific_date(sprints: list[dict], target_date: str) -> list[dict]:
    """
    Filter sprints that are active on a specific date.

    Args:
        sprints: List of sprint dictionaries
        target_date: Target date string in YYYY-MM-DD format

    Returns:
        Filtered list of sprints
    """
    # Date validation is done at tool entry, so we can parse directly
    target = convert_date_string_to_date(target_date)

    filtered_sprints = []
    for sprint in sprints:
        start_date_str = sprint.get("startDate")
        end_date_str = sprint.get("endDate")

        # Skip sprints without dates
        if not start_date_str or not end_date_str:
            continue

        # Parse Jira date format (ISO format with timezone)
        start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
        end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()

        # Check if target date is within sprint dates
        if start_date <= target <= end_date:
            filtered_sprints.append(sprint)

    return filtered_sprints


def _filter_sprints_by_date_range(
    sprints: list[dict], start_date: str | None, end_date: str | None
) -> list[dict]:
    """
    Filter sprints that overlap with the specified date range.

    Args:
        sprints: List of sprint dictionaries
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format

    Returns:
        Filtered list of sprints
    """
    # Date validation is done at tool entry, so we can parse directly
    filter_start = convert_date_string_to_date(start_date) if start_date else None
    filter_end = convert_date_string_to_date(end_date) if end_date else None

    filtered_sprints = []
    for sprint in sprints:
        start_date_str = sprint.get("startDate")
        end_date_str = sprint.get("endDate")

        # Skip sprints without dates if we have date filters
        if (filter_start or filter_end) and (not start_date_str or not end_date_str):
            continue

        # Parse Jira date format (ISO format with timezone)
        sprint_start = (
            datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
            if start_date_str
            else None
        )
        sprint_end = (
            datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()
            if end_date_str
            else None
        )

        # Check if sprint overlaps with filter range
        overlap = True

        if filter_start and sprint_end and sprint_end < filter_start:
            overlap = False

        if filter_end and sprint_start and sprint_start > filter_end:
            overlap = False

        if overlap:
            filtered_sprints.append(sprint)

    return filtered_sprints


def _sort_sprints_latest_first(sprints: list[dict]) -> list[dict]:
    """
    Sort sprints with latest first (by end date, start date, then ID).

    Args:
        sprints: List of sprint dictionaries

    Returns:
        Sorted list of sprints with latest first
    """
    from datetime import date as min_date

    def sort_key(sprint: dict) -> tuple:
        end_date_str = sprint.get("endDate")
        start_date_str = sprint.get("startDate")
        sprint_id = sprint.get("id")

        try:
            end_date = (
                datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()
                if end_date_str
                else min_date.min
            )
        except (ValueError, AttributeError):
            end_date = min_date.min

        try:
            start_date = (
                datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
                if start_date_str
                else min_date.min
            )
        except (ValueError, AttributeError):
            start_date = min_date.min

        return (
            -end_date.toordinal() if end_date != min_date.min else float("inf"),
            -start_date.toordinal() if start_date != min_date.min else float("inf"),
            -int(sprint_id) if isinstance(sprint_id, int | str) and str(sprint_id).isdigit() else 0,
        )

    return sorted(sprints, key=sort_key)


def _validate_parameters(
    board_identifiers_list: list[str] | None,
    specific_date: str | None,
    start_date: str | None,
    end_date: str | None,
    state: list[str] | None,
) -> None:
    """
    Validate input parameters for sprint listing.

    Args:
        board_identifiers_list: List of board IDs or names
        specific_date: Specific date for filtering
        start_date: Start date for range filtering
        end_date: End date for range filtering
        state: List of sprint states

    Raises:
        RetryableToolError: If parameters are invalid
    """
    # Validate date parameters
    if specific_date and (start_date or end_date):
        raise RetryableToolError(CONFLICTING_DATE_PARAMS_ERROR)

    # Validate date formats
    if specific_date and not is_valid_date_string(specific_date):
        raise RetryableToolError(SPECIFIC_DATE_FORMAT_ERROR)

    if start_date and not is_valid_date_string(start_date):
        raise RetryableToolError(START_DATE_FORMAT_ERROR)

    if end_date and not is_valid_date_string(end_date):
        raise RetryableToolError(END_DATE_FORMAT_ERROR)
