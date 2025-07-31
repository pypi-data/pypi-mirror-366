import logging
from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Atlassian

from arcade_jira.client import APIType, JiraClient
from arcade_jira.utils import (
    clean_board_dict,
    create_board_result_dict,
    create_error_entry,
    resolve_cloud_id_and_name,
    validate_board_limit,
)

logger = logging.getLogger(__name__)


@tool(
    requires_auth=Atlassian(
        scopes=[
            "read:board-scope:jira-software",  # /board/{boardId}, /board
            "read:project:jira",  # project info included in /board responses
            "read:issue-details:jira",  # issue metadata in /board/{boardId}, /board responses
        ]
    )
)
async def get_boards(
    context: ToolContext,
    board_identifiers_list: Annotated[
        list[str] | None,
        "List of board names or numeric IDs (as strings) to retrieve using pagination. "
        "Include all mentioned boards in a single list for best performance. "
        "Default None retrieves all boards. Maximum 50 boards returned per call.",
    ] = None,
    limit: Annotated[
        int,
        "Maximum number of boards to return (1-50). Defaults to max that is 50.",
    ] = 50,
    offset: Annotated[
        int,
        "Number of boards to skip for pagination. Must be 0 or greater. Defaults to 0.",
    ] = 0,
    atlassian_cloud_id: Annotated[
        str | None,
        "Atlassian Cloud ID to use. Defaults to None (uses single authorized cloud).",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Dictionary with 'boards' list containing board metadata (ID, name, type, location) "
    "and 'errors' array for unfound boards. Includes pagination metadata and deduplication.",
]:
    """
    Retrieve Jira boards either by specifying their names or IDs, or get all
    available boards.
    All requests support offset and limit with a maximum of 50 boards returned per call.

    MANDATORY ACTION: ALWAYS when you need to get multiple boards, you must
    include all the board identifiers in a single call rather than making
    multiple separate tool calls, as this provides much better performance, not doing that will
    bring huge performance penalties.

    The tool automatically handles mixed identifier types (names and IDs), deduplicates results, and
    falls back from ID lookup to name lookup when needed.
    """
    cloud_data = await resolve_cloud_id_and_name(context, atlassian_cloud_id)
    client = JiraClient(context, cloud_data["cloud_id"], client_type=APIType.AGILE)
    limit = validate_board_limit(limit)

    # If no specific boards requested, get boards without name/id filtering
    if not board_identifiers_list:
        return await _get_boards_with_offset(client, limit, offset, cloud_data["cloud_name"])

    # Process specific board identifiers with deduplication
    return await _get_boards_by_identifiers(
        client, board_identifiers_list, cloud_data["cloud_name"]
    )


async def _get_boards_by_identifiers(
    client: JiraClient,
    board_identifiers_list: list[str],
    cloud_name: str,
) -> dict[str, Any]:
    """
    Get boards by specific identifiers with deduplication logic.

    Args:
        client: JiraClient instance for API calls
        board_identifiers_list: List of board names or IDs to retrieve
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Dictionary containing deduplicated boards and any errors
    """
    results: dict[str, Any] = {
        "boards": [],
        "errors": [],
    }

    # Track processed identifiers (both IDs and names) to prevent duplicates
    processed_identifiers = set()

    for board_identifier in board_identifiers_list:
        # Skip if we already processed this identifier or found this board
        if board_identifier in processed_identifiers:
            continue

        try:
            board_result = await _find_board_by_identifier(client, board_identifier, cloud_name)

            if board_result:
                # Add both the board ID and name to processed set to prevent future duplicates
                processed_identifiers.add(str(board_result["id"]))
                processed_identifiers.add(board_result["name"])
                results["boards"].append(board_result)
            else:
                # Board not found, add to errors
                error_entry = create_error_entry(
                    board_identifier,
                    f"Board '{board_identifier}' not found",
                )
                results["errors"].append(error_entry)

        except Exception as e:
            error_entry = create_error_entry(
                board_identifier,
                f"Unexpected error processing board '{board_identifier}': {e!s}",
            )
            results["errors"].append(error_entry)

    return results


async def _find_board_by_identifier(
    client: JiraClient,
    board_identifier: str,
    cloud_name: str,
) -> dict[str, Any] | None:
    """
    Find a board by either ID or name.

    Args:
        client: JiraClient instance for API calls
        board_identifier: Board ID or name to search for
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Cleaned board dictionary if found, None otherwise
    """
    # If identifier is numeric, try to get by ID first
    if board_identifier.isdigit():
        board_result = await _find_board_by_id(client, board_identifier, cloud_name)
        if board_result:
            return board_result
        # ID lookup failed, fall back to name lookup
        logger.warning(f"Board ID lookup failed for '{board_identifier}'. Attempting name lookup.")

    # Try by name (for non-numeric identifiers or failed ID lookup)
    return await _find_board_by_name(client, board_identifier, cloud_name)


async def _find_board_by_id(
    client: JiraClient,
    board_id: str,
    cloud_name: str,
) -> dict[str, Any] | None:
    """
    Find a board by its ID.

    Args:
        client: JiraClient instance for API calls
        board_id: Board ID to search for
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Cleaned board dictionary if found, None otherwise
    """
    try:
        board = await client.get(f"/board/{board_id}")
    except Exception:
        logger.warning(f"Board ID lookup failed for '{board_id}'. API error.")
        return None
    else:
        board_result = clean_board_dict(board, cloud_name)
        board_result["found_by"] = "id"
        return board_result


async def _find_board_by_name(
    client: JiraClient,
    board_name: str,
    cloud_name: str,
) -> dict[str, Any] | None:
    """
    Find a board by its name using Jira API name filter.

    Args:
        client: JiraClient instance for API calls
        board_name: Board name to search for
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Cleaned board dictionary if found, None otherwise
    """
    try:
        response = await client.get("/board", params={"name": board_name, "maxResults": 1})
        boards = response.get("values", [])
        if boards:
            board_result = clean_board_dict(boards[0], cloud_name)
            board_result["found_by"] = "name"
            return board_result
    except Exception:
        logger.warning(f"Board name lookup failed for '{board_name}'. API error.")

    return None


async def _get_boards_with_offset(
    client: JiraClient,
    limit: int,
    offset: int,
    cloud_name: str,
) -> dict[str, Any]:
    """
    Get boards with pagination using offset and limit parameters.

    Args:
        client: JiraClient instance for API calls
        limit: Maximum number of boards to return (capped at 50)
        offset: Number of boards to skip
        cloud_name: The name of the Atlassian Cloud to use for API calls

    Returns:
        Dictionary containing boards and pagination metadata
    """
    # Enforce maximum limit of 50 boards for this function
    limit = min(limit, 50)

    response = await client.get(
        "/board",
        params={
            "startAt": offset,
            "maxResults": limit,
        },
    )

    boards = [clean_board_dict(board, cloud_name) for board in response.get("values", [])]

    return create_board_result_dict(
        boards,
        len(boards),
        response.get("isLast", False),
        offset,
        limit,
        cloud_name,
    )
