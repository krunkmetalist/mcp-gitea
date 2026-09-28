# Gitea MCP Server

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
* A Gitea Personal Access Token (Settings -> Applications -> Generate Token). See the [Gitea documentation](https://docs.gitea.com/development/api-usage#authenticating-as-a-user) for more details.

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

**Using a `.env` file (Recommended):**
To avoid having to set these variables every time, you can create a `.env` file in the root of the project. Many tools (including python-dotenv) will automatically load these:

```env
GITEA_URL="http://your-gitea-instance:3000"
GITEA_TOKEN="your_personal_access_token"
```

### Running the Server
You can run the server directly via Python. 

If you choose to set the variables directly in your terminal using `export`, note that this is only viable for the life of that specific shell session:

```bash
export GITEA_URL="http://your-gitea-instance:3000"
export GITEA_TOKEN="your_personal_access_token"
python gitea_mcp.py
```

## Client Configuration

Because MCP is a standardized protocol, you can use this server with any compatible client. Below are configuration examples for a few popular clients.

### Using with Hermes
You can integrate this server into a Hermes agent. By running `hermes config edit`, you can set the path and the tool name for the agent in your configuration:

```yaml
mcp_servers:
  gitea-local:
    command: /absolute/path/to/mcp-servers/.venv/bin/python
    args:
      - /absolute/path/to/mcp-servers/gitea_mcp.py
    env:
      GITEA_URL: http://<your-instance>:3000/
      GITEA_TOKEN: <your-PAT>
```

### Using with Claude Desktop (Example)
To use this with an MCP-compatible client like Claude Desktop, you would add it to your configuration file (usually `claude_desktop_config.json`). Make sure to specify the absolute path to the Python executable within your environment:

```json
{
  "mcpServers": {
    "gitea": {
      "command": "/absolute/path/to/mcp-servers/.venv/bin/python",
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
* `commit_files`: Commits a list of file changes (creations or updates) directly to a branch (automatically handles base64 encoding).
* `create_pull_request`: Opens a PR from a feature branch to a base branch.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
