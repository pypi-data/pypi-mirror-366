# main.py for mcp-http-tool
import httpx
import json
import mimetypes
import os
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("mcp-http-tool")

async def _make_request(
    ctx: Context,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    content: Optional[Any] = None,
    json_data: Optional[Dict[str, Any]] = None,
    form_data: Optional[Dict[str, str]] = None,
    files: Optional[Dict[str, Any]] = None,
    auth: Optional[str] = None,
    timeout: float = 30.0,
) -> dict:
    headers = headers or {}
    auth_obj = None
    if auth:
        try:
            auth_type, auth_value = auth.split(" ", 1)
            if auth_type.lower() == "basic":
                if ":" not in auth_value:
                    raise ValueError("Basic auth value must be in 'user:pass' format.")
                auth_obj = tuple(auth_value.split(":", 1))
            elif auth_type.lower() == "bearer":
                headers["Authorization"] = f"Bearer {auth_value}"
        except ValueError as e:
            return {"success": False, "error": "InvalidAuthFormat", "message": str(e)}
    request_kwargs = {
        "method": method,
        "url": url,
        "headers": headers,
        "params": params,
        "content": content,
        "json": json_data,
        "data": form_data,
        "files": files,
        "timeout": timeout,
        "auth": auth_obj,
    }
    await ctx.debug(f"Executing request: {method} {url}")
    try:
        async with httpx.AsyncClient(follow_redirects=False) as client:
            response = await client.request(
                **{k: v for k, v in request_kwargs.items() if v is not None}
            )
            if response.is_redirect:
                await ctx.warning(f"Redirect response received: {response.status_code}")
                return {
                    "success": False,
                    "error": "RedirectResponse",
                    "status_code": response.status_code,
                    "message": f"Request redirected to {response.headers.get('Location')}",
                    "headers": dict(response.headers),
                }
            response.raise_for_status()
            await ctx.info(
                f"Request to {url} succeeded with status {response.status_code}."
            )
            response_body = ""
            try:
                response_body = response.json()
            except json.JSONDecodeError:
                response_body = response.text
            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_body,
            }
    except httpx.HTTPStatusError as e:
        await ctx.error(
            f"HTTP error for {url}: {e.response.status_code} - {e.response.text}"
        )
        return {
            "success": False,
            "error": "HTTPStatusError",
            "status_code": e.response.status_code,
            "message": str(e),
            "response_body": e.response.text,
        }
    except httpx.RequestError as e:
        await ctx.error(f"Request error for {url}: {e}")
        return {
            "success": False,
            "error": "RequestError",
            "message": f"An error occurred: {e!s}",
        }
    except Exception as e:
        await ctx.error(f"An unexpected error occurred for {url}: {e}")
        return {"success": False, "error": "UnexpectedError", "message": str(e)}

@mcp.tool()
async def http_get(
    ctx: Context,
    url: str,
    params: Optional[Dict[str, str]] = None,
    auth: Optional[str] = None,
) -> dict:
    """Performs an HTTP GET request to retrieve data from a URL."""
    return await _make_request(ctx, "GET", url, params=params, auth=auth)

@mcp.tool()
async def http_post_json(
    ctx: Context, url: str, json_data: Dict[str, Any], auth: Optional[str] = None
) -> dict:
    """Performs an HTTP POST request with a JSON body."""
    headers = {"Content-Type": "application/json"}
    return await _make_request(
        ctx, "POST", url, headers=headers, json_data=json_data, auth=auth
    )
@mcp.tool()
async def http_post_form(
    ctx: Context, url: str, form_data: Dict[str, str], auth: Optional[str] = None
) -> dict:
    """Performs an HTTP POST request with URL-encoded form data."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return await _make_request(
        ctx, "POST", url, headers=headers, form_data=form_data, auth=auth
    )
@mcp.tool()
async def http_upload_file(
    ctx: Context,
    url: str,
    file_path: str,
    form_data: Optional[Dict[str, str]] = None,
    auth: Optional[str] = None,
) -> dict:
    """Uploads a single file to a URL using multipart/form-data."""
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": "FileNotFound",
            "message": f"The file was not found at: {file_path}",
        }
    files_to_send = {}
    file_name = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    with open(file_path, "rb") as f:
        files_to_send["file"] = (file_name, f.read(), mime_type)
    return await _make_request(
        ctx, "POST", url, form_data=form_data, files=files_to_send, auth=auth
    )
@mcp.tool(
    name="ai_driven_http_request",
    description="Intelligently performs a web request based on a goal. It automatically selects the correct low-level tool (GET, POST JSON, upload, etc.). This is the preferred tool for most tasks.",
)
async def ai_driven_http_request(
    ctx: Context,
    goal: str,
    url: str,
    method: str,
    data: Optional[Dict[str, Any]] = None,
    file_path: Optional[str] = None,
    auth: Optional[str] = None,
) -> dict:
    await ctx.info(f"AI Goal: '{goal}'. Determining best tool for {method} {url}.")
    method_upper = method.upper()
    if file_path:
        if method_upper != "POST":
            return {
                "success": False,
                "error": "InvalidMethod",
                "message": "File uploads must use the POST method.",
            }
        await ctx.debug("Selected tool: http_upload_file")
        return await http_upload_file(
            ctx, url=url, file_path=file_path, form_data=data, auth=auth
        )
    if method_upper == "GET":
        await ctx.debug("Selected tool: http_get")
        return await http_get(ctx, url=url, params=data, auth=auth)
    if method_upper == "POST":
        if data:
            if any(not isinstance(v, (dict, list)) for v in data.values()):
                await ctx.debug("Selected tool: http_post_form")
                return await http_post_form(ctx, url=url, form_data=data, auth=auth)
            else:
                await ctx.debug("Selected tool: http_post_json")
                return await http_post_json(ctx, url=url, json_data=data, auth=auth)
        else:
            return await _make_request(ctx, "POST", url, auth=auth)
    await ctx.debug(f"Selected tool: _make_request (fallback for {method_upper})")
    return await _make_request(ctx, method_upper, url, json_data=data, auth=auth)

def run():
    """
    Entry point for running the FastMCP server.
    """
    mcp.run()

if __name__ == '__main__':
    # This is the entry point for the stdio server.
    run()