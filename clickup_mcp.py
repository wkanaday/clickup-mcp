#!/usr/bin/env python3
"""
ClickUp MCP Server

A comprehensive MCP server that provides tools for interacting with ClickUp API.

Features:
- Workspace & Space Management: List workspaces, spaces, folders, and lists
- Task Management: Create, read, update, delete, and search tasks
- Task Details: Get comprehensive task information with custom fields
- Comments: Add and retrieve task comments
- Custom Fields: Get and update custom field values
- Time Tracking: Retrieve time entries
- Documents: Search and retrieve ClickUp documents
"""

import os
import httpx
from typing import Optional, Any
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("ClickUp MCP Server")

# ClickUp API configuration
CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN", "")
CLICKUP_API_BASE_URL = "https://api.clickup.com/api/v2"

# HTTP client configuration
headers = {
    "Authorization": CLICKUP_API_TOKEN,
    "Content-Type": "application/json"
}


async def make_clickup_request(
    method: str,
    endpoint: str,
    params: Optional[dict] = None,
    json_data: Optional[dict] = None
) -> dict[str, Any]:
    """
    Make an authenticated request to the ClickUp API.

    Args:
        method: HTTP method (GET, POST, PUT, etc.)
        endpoint: API endpoint (will be appended to base URL)
        params: Query parameters
        json_data: JSON body for POST/PUT requests

    Returns:
        API response as dictionary
    """
    url = f"{CLICKUP_API_BASE_URL}/{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_workspaces() -> str:
    """
    List all ClickUp workspaces (teams) accessible by the authenticated user.

    Returns:
        A formatted string containing workspace information including IDs and names.
    """
    try:
        data = await make_clickup_request("GET", "team")

        if not data.get("teams"):
            return "No workspaces found."

        result = "ClickUp Workspaces:\n\n"
        for team in data["teams"]:
            result += f"• {team['name']}\n"
            result += f"  ID: {team['id']}\n"
            if team.get("members"):
                result += f"  Members: {len(team['members'])}\n"
            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching workspaces: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def search_tasks(
    team_id: str,
    query: Optional[str] = None,
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    list_id: Optional[str] = None,
    space_id: Optional[str] = None
) -> str:
    """
    Search for tasks in a ClickUp workspace.

    Args:
        team_id: The workspace (team) ID to search in
        query: Search query text (optional)
        status: Filter by status (optional)
        assignee: Filter by assignee user ID (optional)
        list_id: Filter by list ID (optional)
        space_id: Filter by space ID (optional)

    Returns:
        A formatted string containing matching tasks.
    """
    try:
        params = {}
        if query:
            params["query"] = query
        if status:
            params["statuses[]"] = status
        if assignee:
            params["assignees[]"] = assignee
        if list_id:
            params["list_ids[]"] = list_id
        if space_id:
            params["space_ids[]"] = space_id

        endpoint = f"team/{team_id}/task"
        data = await make_clickup_request("GET", endpoint, params=params)

        tasks = data.get("tasks", [])

        if not tasks:
            return "No tasks found matching the criteria."

        result = f"Found {len(tasks)} task(s):\n\n"
        for task in tasks:
            result += f"• {task['name']}\n"
            result += f"  ID: {task['id']}\n"
            result += f"  Status: {task['status']['status']}\n"
            result += f"  URL: {task['url']}\n"

            if task.get("assignees"):
                assignee_names = [a.get("username", "Unknown") for a in task["assignees"]]
                result += f"  Assignees: {', '.join(assignee_names)}\n"

            if task.get("due_date"):
                result += f"  Due Date: {task['due_date']}\n"

            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error searching tasks: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_task(
    list_id: str,
    name: str,
    description: Optional[str] = None,
    assignees: Optional[list[int]] = None,
    priority: Optional[int] = None,
    status: Optional[str] = None,
    due_date: Optional[int] = None
) -> str:
    """
    Create a new task in ClickUp.

    Args:
        list_id: The list ID where the task will be created
        name: Task name (required)
        description: Task description (optional)
        assignees: List of user IDs to assign (optional)
        priority: Priority level: 1 (urgent), 2 (high), 3 (normal), 4 (low) (optional)
        status: Status name (optional)
        due_date: Due date as Unix timestamp in milliseconds (optional)

    Returns:
        A formatted string with the created task details.
    """
    try:
        task_data = {"name": name}

        if description:
            task_data["description"] = description
        if assignees:
            task_data["assignees"] = assignees
        if priority:
            task_data["priority"] = priority
        if status:
            task_data["status"] = status
        if due_date:
            task_data["due_date"] = due_date

        endpoint = f"list/{list_id}/task"
        data = await make_clickup_request("POST", endpoint, json_data=task_data)

        task = data
        result = "Task created successfully!\n\n"
        result += f"• Name: {task['name']}\n"
        result += f"  ID: {task['id']}\n"
        result += f"  URL: {task['url']}\n"
        result += f"  Status: {task['status']['status']}\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error creating task: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def update_task(
    task_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    assignees_add: Optional[list[int]] = None,
    assignees_remove: Optional[list[int]] = None,
    due_date: Optional[int] = None
) -> str:
    """
    Update an existing ClickUp task.

    Args:
        task_id: The task ID to update
        name: New task name (optional)
        description: New task description (optional)
        status: New status name (optional)
        priority: New priority level: 1 (urgent), 2 (high), 3 (normal), 4 (low) (optional)
        assignees_add: List of user IDs to add as assignees (optional)
        assignees_remove: List of user IDs to remove from assignees (optional)
        due_date: New due date as Unix timestamp in milliseconds (optional)

    Returns:
        A formatted string with the updated task details.
    """
    try:
        update_data = {}

        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        if priority is not None:
            update_data["priority"] = priority
        if assignees_add is not None:
            if "assignees" not in update_data:
                update_data["assignees"] = {}
            update_data["assignees"]["add"] = assignees_add
        if assignees_remove is not None:
            if "assignees" not in update_data:
                update_data["assignees"] = {}
            update_data["assignees"]["rem"] = assignees_remove
        if due_date is not None:
            update_data["due_date"] = due_date

        if not update_data:
            return "No updates provided. Please specify at least one field to update."

        endpoint = f"task/{task_id}"
        data = await make_clickup_request("PUT", endpoint, json_data=update_data)

        task = data
        result = "Task updated successfully!\n\n"
        result += f"• Name: {task['name']}\n"
        result += f"  ID: {task['id']}\n"
        result += f"  URL: {task['url']}\n"
        result += f"  Status: {task['status']['status']}\n"

        if task.get("assignees"):
            assignee_names = [a.get("username", "Unknown") for a in task["assignees"]]
            result += f"  Assignees: {', '.join(assignee_names)}\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error updating task: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_task_details(task_id: str, include_subtasks: bool = False) -> str:
    """
    Get detailed information about a specific ClickUp task.

    Args:
        task_id: The task ID to retrieve
        include_subtasks: Whether to include subtasks information (optional, default: False)

    Returns:
        A formatted string with comprehensive task details.
    """
    try:
        params = {}
        if include_subtasks:
            params["include_subtasks"] = "true"

        endpoint = f"task/{task_id}"
        task = await make_clickup_request("GET", endpoint, params=params)

        result = "Task Details:\n\n"
        result += f"Name: {task['name']}\n"
        result += f"ID: {task['id']}\n"
        result += f"Status: {task['status']['status']}\n"
        result += f"URL: {task['url']}\n"

        if task.get("description"):
            result += f"\nDescription:\n{task['description']}\n"

        if task.get("assignees"):
            assignee_names = [a.get("username", "Unknown") for a in task["assignees"]]
            result += f"\nAssignees: {', '.join(assignee_names)}\n"

        if task.get("creator"):
            result += f"Created by: {task['creator'].get('username', 'Unknown')}\n"

        if task.get("date_created"):
            result += f"Created: {task['date_created']}\n"

        if task.get("date_updated"):
            result += f"Last updated: {task['date_updated']}\n"

        if task.get("due_date"):
            result += f"Due date: {task['due_date']}\n"

        if task.get("priority"):
            priority_map = {1: "Urgent", 2: "High", 3: "Normal", 4: "Low"}
            priority_name = priority_map.get(task["priority"].get("id"), "None")
            result += f"Priority: {priority_name}\n"

        if task.get("tags"):
            tag_names = [t.get("name", "") for t in task["tags"]]
            result += f"Tags: {', '.join(tag_names)}\n"

        if task.get("list"):
            result += f"\nList: {task['list']['name']}\n"

        if task.get("folder"):
            result += f"Folder: {task['folder']['name']}\n"

        if task.get("space"):
            result += f"Space: {task['space']['name']}\n"

        if task.get("custom_fields"):
            result += "\nCustom Fields:\n"
            for field in task["custom_fields"]:
                field_name = field.get("name", "Unknown")
                field_value = field.get("value", "Not set")
                result += f"  • {field_name}: {field_value}\n"

        if include_subtasks and task.get("subtasks"):
            result += f"\nSubtasks ({len(task['subtasks'])}):\n"
            for subtask in task["subtasks"]:
                result += f"  • {subtask['name']} (ID: {subtask['id']})\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching task details: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_list_spaces(team_id: str) -> str:
    """
    List all spaces in a ClickUp workspace.

    Args:
        team_id: The workspace (team) ID

    Returns:
        A formatted string containing space information including IDs, names, and settings.
    """
    try:
        endpoint = f"team/{team_id}/space"
        data = await make_clickup_request("GET", endpoint, params={"archived": "false"})

        spaces = data.get("spaces", [])

        if not spaces:
            return "No spaces found in this workspace."

        result = f"Spaces in workspace {team_id}:\n\n"
        for space in spaces:
            result += f"• {space['name']}\n"
            result += f"  ID: {space['id']}\n"
            if space.get("private"):
                result += f"  Private: Yes\n"
            if space.get("statuses"):
                status_names = [s.get("status", "") for s in space["statuses"]]
                result += f"  Statuses: {', '.join(status_names)}\n"
            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching spaces: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_list_folders(space_id: str) -> str:
    """
    List all folders in a ClickUp space.

    Args:
        space_id: The space ID

    Returns:
        A formatted string containing folder information including IDs and names.
    """
    try:
        endpoint = f"space/{space_id}/folder"
        data = await make_clickup_request("GET", endpoint, params={"archived": "false"})

        folders = data.get("folders", [])

        if not folders:
            return "No folders found in this space."

        result = f"Folders in space {space_id}:\n\n"
        for folder in folders:
            result += f"• {folder['name']}\n"
            result += f"  ID: {folder['id']}\n"
            if folder.get("hidden"):
                result += f"  Hidden: Yes\n"
            if folder.get("lists"):
                result += f"  Lists: {len(folder['lists'])}\n"
            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching folders: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_list_lists(
    space_id: Optional[str] = None,
    folder_id: Optional[str] = None
) -> str:
    """
    List all lists in a ClickUp space or folder.

    Args:
        space_id: The space ID (required if folder_id not provided)
        folder_id: The folder ID (required if space_id not provided)

    Returns:
        A formatted string containing list information including IDs and names.
    """
    try:
        if not space_id and not folder_id:
            return "Error: Must provide either space_id or folder_id"

        if folder_id:
            endpoint = f"folder/{folder_id}/list"
        else:
            endpoint = f"space/{space_id}/list"

        data = await make_clickup_request("GET", endpoint, params={"archived": "false"})

        lists = data.get("lists", [])

        if not lists:
            return "No lists found."

        result = f"Lists:\n\n"
        for list_item in lists:
            result += f"• {list_item['name']}\n"
            result += f"  ID: {list_item['id']}\n"
            if list_item.get("folder"):
                result += f"  Folder: {list_item['folder'].get('name', 'Unknown')}\n"
            if list_item.get("task_count") is not None:
                result += f"  Tasks: {list_item['task_count']}\n"
            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching lists: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_get_list_tasks(
    list_id: str,
    include_closed: bool = False,
    order_by: Optional[str] = None
) -> str:
    """
    Get all tasks from a specific ClickUp list.

    Args:
        list_id: The list ID
        include_closed: Whether to include closed/completed tasks (default: False)
        order_by: Field to order by (optional): 'created', 'updated', 'due_date'

    Returns:
        A formatted string containing task information.
    """
    try:
        params = {"archived": "false"}
        if include_closed:
            params["include_closed"] = "true"
        if order_by:
            params["order_by"] = order_by

        endpoint = f"list/{list_id}/task"
        data = await make_clickup_request("GET", endpoint, params=params)

        tasks = data.get("tasks", [])

        if not tasks:
            return f"No tasks found in list {list_id}."

        result = f"Tasks in list {list_id} ({len(tasks)} total):\n\n"
        for task in tasks:
            result += f"• {task['name']}\n"
            result += f"  ID: {task['id']}\n"
            result += f"  Status: {task['status']['status']}\n"
            result += f"  URL: {task['url']}\n"

            if task.get("assignees"):
                assignee_names = [a.get("username", "Unknown") for a in task["assignees"]]
                result += f"  Assignees: {', '.join(assignee_names)}\n"

            if task.get("due_date"):
                result += f"  Due Date: {task['due_date']}\n"

            if task.get("priority"):
                priority_map = {1: "Urgent", 2: "High", 3: "Normal", 4: "Low"}
                priority_name = priority_map.get(task["priority"].get("id"), "None")
                result += f"  Priority: {priority_name}\n"

            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching list tasks: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_add_comment(
    task_id: str,
    comment_text: str,
    assignee: Optional[int] = None,
    notify_all: bool = True
) -> str:
    """
    Add a comment to a ClickUp task.

    Args:
        task_id: The task ID
        comment_text: The comment text
        assignee: User ID to assign the comment to (optional)
        notify_all: Whether to notify all assignees (default: True)

    Returns:
        A formatted string with the created comment details.
    """
    try:
        comment_data = {
            "comment_text": comment_text,
            "notify_all": notify_all
        }

        if assignee:
            comment_data["assignee"] = assignee

        endpoint = f"task/{task_id}/comment"
        data = await make_clickup_request("POST", endpoint, json_data=comment_data)

        result = "Comment added successfully!\n\n"
        result += f"Comment ID: {data['id']}\n"
        result += f"Comment: {data['comment_text']}\n"
        result += f"Posted by: {data['user'].get('username', 'Unknown')}\n"
        result += f"Date: {data['date']}\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error adding comment: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_get_comments(task_id: str) -> str:
    """
    Get all comments from a ClickUp task.

    Args:
        task_id: The task ID

    Returns:
        A formatted string containing all task comments.
    """
    try:
        endpoint = f"task/{task_id}/comment"
        data = await make_clickup_request("GET", endpoint)

        comments = data.get("comments", [])

        if not comments:
            return f"No comments found for task {task_id}."

        result = f"Comments for task {task_id} ({len(comments)} total):\n\n"
        for comment in comments:
            result += f"• {comment['user'].get('username', 'Unknown')}\n"
            result += f"  Date: {comment['date']}\n"
            result += f"  Comment: {comment['comment_text']}\n"
            if comment.get("resolved"):
                result += f"  Status: Resolved\n"
            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching comments: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_delete_task(task_id: str) -> str:
    """
    Delete a ClickUp task.

    Args:
        task_id: The task ID to delete

    Returns:
        A confirmation message.
    """
    try:
        endpoint = f"task/{task_id}"
        await make_clickup_request("DELETE", endpoint)

        return f"Task {task_id} deleted successfully."
    except httpx.HTTPStatusError as e:
        return f"Error deleting task: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_get_custom_fields(list_id: str) -> str:
    """
    Get all custom fields for a ClickUp list.

    Args:
        list_id: The list ID

    Returns:
        A formatted string containing custom field information.
    """
    try:
        endpoint = f"list/{list_id}/field"
        data = await make_clickup_request("GET", endpoint)

        fields = data.get("fields", [])

        if not fields:
            return f"No custom fields found for list {list_id}."

        result = f"Custom fields for list {list_id}:\n\n"
        for field in fields:
            result += f"• {field['name']}\n"
            result += f"  ID: {field['id']}\n"
            result += f"  Type: {field['type']}\n"

            if field.get("type_config"):
                if field["type"] == "drop_down" and field["type_config"].get("options"):
                    options = [opt.get("name", "") for opt in field["type_config"]["options"]]
                    result += f"  Options: {', '.join(options)}\n"

            if field.get("required"):
                result += f"  Required: Yes\n"

            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching custom fields: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_update_custom_field(
    task_id: str,
    field_id: str,
    value: Any
) -> str:
    """
    Update a custom field value on a ClickUp task.

    Args:
        task_id: The task ID
        field_id: The custom field ID
        value: The new value for the field

    Returns:
        A confirmation message.
    """
    try:
        field_data = {"value": value}

        endpoint = f"task/{task_id}/field/{field_id}"
        await make_clickup_request("POST", endpoint, json_data=field_data)

        return f"Custom field {field_id} updated successfully on task {task_id}."
    except httpx.HTTPStatusError as e:
        return f"Error updating custom field: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_get_time_entries(
    team_id: str,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    assignee: Optional[int] = None
) -> str:
    """
    Get time entries for a ClickUp workspace.

    Args:
        team_id: The workspace (team) ID
        start_date: Start date as Unix timestamp in milliseconds (optional)
        end_date: End date as Unix timestamp in milliseconds (optional)
        assignee: Filter by assignee user ID (optional)

    Returns:
        A formatted string containing time entry information.
    """
    try:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if assignee:
            params["assignee"] = assignee

        endpoint = f"team/{team_id}/time_entries"
        data = await make_clickup_request("GET", endpoint, params=params)

        entries = data.get("data", [])

        if not entries:
            return "No time entries found."

        result = f"Time entries ({len(entries)} total):\n\n"
        for entry in entries:
            result += f"• Duration: {entry.get('duration', 0)} ms\n"
            result += f"  User: {entry['user'].get('username', 'Unknown')}\n"

            if entry.get("task"):
                result += f"  Task: {entry['task'].get('name', 'Unknown')}\n"
                result += f"  Task ID: {entry['task'].get('id', 'Unknown')}\n"

            if entry.get("description"):
                result += f"  Description: {entry['description']}\n"

            if entry.get("start"):
                result += f"  Start: {entry['start']}\n"

            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching time entries: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_search_docs(
    team_id: str,
    query: Optional[str] = None
) -> str:
    """
    Search for documents in a ClickUp workspace.

    Args:
        team_id: The workspace (team) ID
        query: Search query text (optional)

    Returns:
        A formatted string containing matching documents.
    """
    try:
        params = {}
        if query:
            params["search"] = query

        endpoint = f"team/{team_id}/docs"
        data = await make_clickup_request("GET", endpoint, params=params)

        docs = data.get("docs", [])

        if not docs:
            return "No documents found."

        result = f"Documents ({len(docs)} total):\n\n"
        for doc in docs:
            result += f"• {doc.get('name', 'Untitled')}\n"
            result += f"  ID: {doc['id']}\n"

            if doc.get("creator"):
                result += f"  Created by: {doc['creator'].get('username', 'Unknown')}\n"

            if doc.get("date_created"):
                result += f"  Created: {doc['date_created']}\n"

            if doc.get("date_updated"):
                result += f"  Updated: {doc['date_updated']}\n"

            result += "\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error searching documents: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clickup_get_doc(team_id: str, doc_id: str) -> str:
    """
    Get detailed information about a specific ClickUp document.

    Args:
        team_id: The workspace (team) ID
        doc_id: The document ID

    Returns:
        A formatted string with comprehensive document details.
    """
    try:
        endpoint = f"team/{team_id}/docs/{doc_id}"
        doc = await make_clickup_request("GET", endpoint)

        result = "Document Details:\n\n"
        result += f"Name: {doc.get('name', 'Untitled')}\n"
        result += f"ID: {doc['id']}\n"

        if doc.get("content"):
            result += f"\nContent:\n{doc['content']}\n"

        if doc.get("creator"):
            result += f"\nCreated by: {doc['creator'].get('username', 'Unknown')}\n"

        if doc.get("date_created"):
            result += f"Created: {doc['date_created']}\n"

        if doc.get("date_updated"):
            result += f"Last updated: {doc['date_updated']}\n"

        if doc.get("sharing"):
            result += f"\nSharing: {doc['sharing'].get('public', False) and 'Public' or 'Private'}\n"

        return result
    except httpx.HTTPStatusError as e:
        return f"Error fetching document: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
