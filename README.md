# Gitea MCP Server 🦊

A Model Context Protocol (MCP) server that empowers AI agents to interact with a Gitea version control instance. 

This server provides tools that allow LLMs (via clients like Claude Desktop or autonomous agents) to read repositories, manage issues, trigger workflows, and even commit code directly to your self-hosted Gitea instance.

## Features
* **Repository Management:** List accessible repositories.
* **Issue Tracking:** Read existing issues and create new ones.
* **CI/CD Integration:** Check the status of recent Gitea Actions workflow runs.
* **Code Modification:** Create branches, open Pull Requests, and commit multiple files directly via the Gitea API.

## Getting Started

### Prerequisites
* Python 3.10+
* `uv` or `pip` for dependency management.
* A running Gitea instance.
* A Gitea Personal Access Token (Settings -> Applications -> Generate Token).

### Installation
Clone the repository and install the required packages:

```bash
git clone https://github.com/your-username/mcp-servers.git
cd mcp-servers
pip install -r requirements.txt
```
*(Note: Consider extracting `gitea_mcp.py` to its own repository if you plan to build more MCP servers).*

### Configuration
The server requires two environment variables to connect to your Gitea instance:

* `GITEA_URL`: The URL of your Gitea instance (e.g., `http://gitea.local:3000`).
* `GITEA_TOKEN`: Your Personal Access Token.

### Running the Server
You can run the server directly using the FastMCP CLI:

```bash
export GITEA_URL="http://your-gitea-instance:3000"
export GITEA_TOKEN="your_personal_access_token"
python gitea_mcp.py
```

## Using with an MCP Client (e.g., Claude Desktop)
To use this with an MCP-compatible client like Claude Desktop, add it to your configuration file (usually `claude_desktop_config.json`), ensuring you pass the required environment variables:

```json
{
  "mcpServers": {
    "gitea": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-servers/gitea_mcp.py"],
      "env": {
        "GITEA_URL": "http://your-gitea-instance:3000",
        "GITEA_TOKEN": "your_personal_access_token"
      }
    }
  }
}
```

## Available Tools

* `list_repositories`: Lists all repositories accessible by the configured user.
* `list_issues`: Fetches open or closed issues for a specific repository.
* `create_issue`: Opens a new issue in a repository.
* `list_workflow_runs`: Lists recent Gitea Actions CI/CD pipeline runs.
* `create_branch`: Creates a new branch from a specified base branch.
* `commit_files`: Commits a list of file changes (creations or updates) directly to a branch using base64 encoding.
* `create_pull_request`: Opens a PR from a feature branch to a base branch.

## License
MIT License (Suggested)
