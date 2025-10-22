# ClickUp MCP Server

An MCP (Model Context Protocol) server that enables Claude to interact with ClickUp's API. This server provides tools for managing workspaces, tasks, and more through a standardized interface.

## Features

- **List Workspaces**: View all accessible ClickUp workspaces (teams)
- **Search Tasks**: Find tasks with flexible filtering options
- **Create Tasks**: Create new tasks with assignees, priorities, and due dates
- **Update Tasks**: Modify existing tasks
- **Get Task Details**: Retrieve comprehensive information about specific tasks

## Prerequisites

- Python 3.10 or higher
- A ClickUp account and API token
- Claude Desktop or another MCP-compatible client

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd clickup-mcp
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Getting Your ClickUp API Token

1. Log in to your ClickUp account
2. Go to Settings > Apps
3. Click "Generate" under API Token
4. Copy your API token

### Setting Up the Environment Variable

Set your ClickUp API token as an environment variable:

**Linux/macOS:**
```bash
export CLICKUP_API_TOKEN="your_api_token_here"
```

**Windows (Command Prompt):**
```cmd
set CLICKUP_API_TOKEN=your_api_token_here
```

**Windows (PowerShell):**
```powershell
$env:CLICKUP_API_TOKEN="your_api_token_here"
```

### Configuring Claude Desktop

Add this server to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "clickup": {
      "command": "python",
      "args": ["/absolute/path/to/clickup-mcp/clickup_mcp.py"],
      "env": {
        "CLICKUP_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

Make sure to replace `/absolute/path/to/clickup-mcp/` with the actual path to your installation.

## Running the Server

### Standalone Mode

You can run the server directly for testing:

```bash
python clickup_mcp.py
```

### With Claude Desktop

1. Update your Claude Desktop configuration as described above
2. Restart Claude Desktop
3. The ClickUp tools will be available in your conversations

## Available Tools

### 1. list_workspaces

Lists all ClickUp workspaces accessible to your account.

**Parameters:** None

**Example:**
```
List my ClickUp workspaces
```

### 2. search_tasks

Search for tasks with various filters.

**Parameters:**
- `team_id` (required): The workspace ID
- `query` (optional): Search text
- `status` (optional): Filter by status
- `assignee` (optional): Filter by assignee user ID
- `list_id` (optional): Filter by list ID
- `space_id` (optional): Filter by space ID

**Example:**
```
Search for tasks in workspace 12345 with status "in progress"
```

### 3. create_task

Create a new task in ClickUp.

**Parameters:**
- `list_id` (required): The list ID where the task will be created
- `name` (required): Task name
- `description` (optional): Task description
- `assignees` (optional): List of user IDs
- `priority` (optional): 1 (urgent), 2 (high), 3 (normal), 4 (low)
- `status` (optional): Status name
- `due_date` (optional): Unix timestamp in milliseconds

**Example:**
```
Create a task named "Update documentation" in list 67890
```

### 4. update_task

Update an existing task.

**Parameters:**
- `task_id` (required): The task ID to update
- `name` (optional): New task name
- `description` (optional): New description
- `status` (optional): New status
- `priority` (optional): New priority level
- `assignees_add` (optional): User IDs to add
- `assignees_remove` (optional): User IDs to remove
- `due_date` (optional): New due date

**Example:**
```
Update task abc123 to status "complete"
```

### 5. get_task_details

Get comprehensive information about a task.

**Parameters:**
- `task_id` (required): The task ID
- `include_subtasks` (optional): Include subtasks (default: false)

**Example:**
```
Get details for task abc123 including subtasks
```

## Usage Examples

Once configured, you can use natural language with Claude:

```
"List my ClickUp workspaces"

"Search for high-priority tasks in workspace 12345"

"Create a task called 'Review PR' in list 67890 with high priority"

"Update task abc123 to mark it as complete"

"Show me all details for task abc123"
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:
- Verify your API token is correct
- Check that the token has the necessary permissions
- Ensure the environment variable is properly set

### Connection Issues

If the server can't connect to ClickUp:
- Check your internet connection
- Verify ClickUp's API status at [status.clickup.com](https://status.clickup.com)
- Ensure you're not hitting rate limits

### Server Not Found

If Claude Desktop can't find the server:
- Verify the path in your configuration is absolute, not relative
- Check that Python is in your system PATH
- Restart Claude Desktop after configuration changes

## API Reference

This server uses the ClickUp API v2. For more information:
- [ClickUp API Documentation](https://clickup.com/api)
- [ClickUp API Rate Limits](https://clickup.com/api#rate-limits)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this project for any purpose.

## Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **ClickUp API**: Check [ClickUp's API documentation](https://clickup.com/api)
- **Claude Desktop**: Visit [Claude's help center](https://support.anthropic.com)
