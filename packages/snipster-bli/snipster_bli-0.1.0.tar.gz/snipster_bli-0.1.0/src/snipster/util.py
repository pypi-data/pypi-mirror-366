import httpx
from decouple import config

from .models import RunResult

PISTON_API_URL = config(
    "PISTON_API_URL", default="https://emkc.org/api/v2/piston/execute"
)

GITHUB_API_URL = "https://api.github.com/gists"

CLIENT_TIMEOUT = 4.0
GITHUB_TOKEN = config("GITHUB_TOKEN")
LANG_EXT = {"PYTHON": "py", "GO": "go", "JAVA": "java", "RUST": "rs"}


class RunCodeError(Exception):
    pass


class GistCreationError(Exception):
    pass


async def run_code(snippet) -> RunResult:
    """
    Run code using the Piston API and return the output.

    Args:
        snippet: An object with `.language` and `.code` attributes.

    Returns:
        RunResult with the output of the code execution.

    Raises:
        RunCodeError on failure.
    """
    piston_lang = snippet.language.value.lower()

    payload = {
        "language": piston_lang,
        "version": "*",
        "files": [{"name": "main", "content": snippet.code}],
    }

    try:
        async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
            response = await client.post(PISTON_API_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            output = result.get("run", {}).get("output", "").strip()
            return RunResult(output=output)
    except httpx.HTTPError as e:
        raise RunCodeError(f"Failed to run code: {str(e)}")


async def create_gist(snippet, public: bool) -> RunResult:
    """
    Create a GitHub Gist for the given snippet.

    Args:
        snippet: A snippet object with .title, .code, and .language
        public: Whether the Gist should be public

    Returns:
        RunResult with the Gist URL

    Raises:
        GistCreationError on failure
    """
    payload = {
        "description": snippet.title,
        "public": public,
        "files": {
            f"{snippet.title.replace(' ', '_')}.{LANG_EXT[snippet.language]}": {
                "content": snippet.code
            }
        },
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
            response = await client.post(GITHUB_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            output = result.get("html_url", "").strip()
            return RunResult(output=output)
    except httpx.HTTPError as e:
        raise GistCreationError(f"Failed to create a gist: {str(e)}")
