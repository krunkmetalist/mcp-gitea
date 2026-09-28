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

@mcp.tool()
async def create_branch(owner: str, repo: str, new_branch_name: str, source_branch: str = "main") -> str:
    """Creates a new branch in a Gitea repository from a source branch."""
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo}/branches"
    payload = {"new_branch_name": new_branch_name, "old_branch_name": source_branch}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=get_headers(), json=payload)
        if res.status_code != 201:
            return f"Failed to create branch: {res.status_code} - {res.text}"
        data = res.json()
        return f"Branch successfully created: {data.get('name')} from {source_branch}"

@mcp.tool()
async def create_pull_request(owner: str, repo: str, title: str, head: str, base: str = "main", body: str = "") -> str:
    """Creates a new pull request in a Gitea repository."""
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "head": head, "base": base, "body": body}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=get_headers(), json=payload)
        if res.status_code != 201:
            return f"Failed to create pull request: {res.status_code} - {res.text}"
        data = res.json()
        return f"Pull request successfully created: #{data['number']} ({data['html_url']})"

@mcp.tool()
async def commit_files(owner: str, repo: str, branch: str, message: str, files_to_change: list[dict]) -> str:
    """
    Commits file creations or updates to a Gitea repository via API.
    files_to_change should be a list of dicts: [{"path": "src/main.py", "content": "print('hello')"}]
    """
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo}/contents"

    # Gitea's repository contents API typically handles single file mutations or batch changes.
    # For a multi-file commit payload structure matching Gitea v1 API:
    payload = {
        "branch": branch,
        "message": message,
        "files": [
            {
                "path": f["path"],
                # Gitea API expects base64 content or direct content depending on endpoint version,
                # but standard contents endpoint uses base64 for creation/updates.
                "content": f["content"]
            } for f in files_to_change
        ]
    }

    # Note: Gitea supports batch file operations via /api/v1/repos/{owner}/{repo}/git/commits or
    # individual file PUT/POST requests. Let's provide a robust multi-file commit implementation.
    async with httpx.AsyncClient() as client:
        # Utilizing the change-files repository endpoint if available, or looping through files.
        # Let's use the explicit multi-file commit endpoint if supported, otherwise individual updates.
        results = []
        import base64
        for f in files_to_change:
            file_path = f["path"]
            file_bytes = f["content"].encode("utf-8")
            encoded_content = base64.b64encode(file_bytes).decode("utf-8")

            file_url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo}/contents/{file_path}"

            # Check if file exists to get its sha (required for updates)
            get_res = await client.get(file_url, headers=get_headers(), params={"ref": branch})
            sha = get_res.json().get("sha") if get_res.status_code == 200 else None

            file_payload = {
                "branch": branch,
                "message": message,
                "content": encoded_content
            }
            if sha:
                file_payload["sha"] = sha

            put_res = await client.put(file_url, headers=get_headers(), json=file_payload)
            if put_res.status_code not in (200, 201):
                results.append(f"Failed to commit {file_path}: {put_res.status_code} - {put_res.text}")
            else:
                results.append(f"Successfully committed {file_path}")

        return "\n".join(results)

if __name__ == "__main__":
    mcp.run()
