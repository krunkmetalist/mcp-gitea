import os
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server instance
mcp = FastMCP("Gitea Engine")

# Read Gitea endpoint & access token from environment variables
GITEA_URL = os.getenv("GITEA_URL", "http://gunter:3000").rstrip("/")
GITEA_TOKEN = os.getenv("GITEA_TOKEN", "")

def get_headers():
    if not GITEA_TOKEN:
        raise ValueError("GITEA_TOKEN environment variable is missing.")
    return {
        "Authorization": f"token {GITEA_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

@mcp.tool()
async def list_repositories() -> str:
    """Lists all repositories accessible by the current Gitea user."""
    url = f"{GITEA_URL}/api/v1/user/repos"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_headers())
        if res.status_code != 200:
            return f"Error fetching repos: {res.status_code} - {res.text}"
        
        repos = res.json()
        output = [f"- {r['full_name']} (Private: {r['private']}) -> {r['html_url']}" for r in repos]
        return "\n".join(output) if output else "No repositories found."

@mcp.tool()
async def list_issues(owner: str, repo: str, state: str = "open") -> str:
    """Fetches issues for a specific repository (state can be 'open', 'closed', or 'all')."""
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo}/issues"
    params = {"state": state}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_headers(), params=params)
        if res.status_code != 200:
            return f"Error fetching issues: {res.status_code} - {res.text}"
        
        issues = res.json()
        if not issues:
            return f"No {state} issues found in {owner}/{repo}."
        
        formatted = [f"#{i['number']} [{i['state']}] {i['title']} (by {i['user']['username']})" for i in issues]
        return "\n".join(formatted)

@mcp.tool()
async def create_issue(owner: str, repo: str, title: str, body: str = "") -> str:
    """Creates a new issue in a Gitea repository."""
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo}/issues"
    payload = {"title": title, "body": body}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=get_headers(), json=payload)
        if res.status_code != 201:
            return f"Failed to create issue: {res.status_code} - {res.text}"
        
        data = res.json()
        return f"Issue successfully created: #{data['number']} ({data['html_url']})"

@mcp.tool()
async def list_workflow_runs(owner: str, repo: str) -> str:
    """Lists recent Gitea Actions CI/CD workflow runs for a repository."""
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo}/actions/runs"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_headers())
        if res.status_code != 200:
            return f"Error fetching workflow runs: {res.status_code} - {res.text}"
        
        runs = res.json().get("workflow_runs", [])
        if not runs:
            return f"No workflow runs found for {owner}/{repo}."
            
        formatted = [f"ID: {r['id']} | Event: {r['event']} | Status: {r['status']} | Conclusion: {r['conclusion']}" for r in runs[:10]]
        return "\n".join(formatted)

if __name__ == "__main__":
    mcp.run()
