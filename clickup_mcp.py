#!/usr/bin/env python3
"""
ClickUp MCP Server

An MCP server that provides tools for interacting with ClickUp API.
Supports listing workspaces, searching tasks, creating/updating tasks, and getting task details.
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


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
