from mcp import types


# Core set of tools provided by our Playwright page, shared between the MCP server and the neural fallback agent.
# all the tool names directly map to the corresponding Playwright method with parameters, reducing boilerplate.
PLAYWRIGHT_TOOLS = [
    types.Tool(
        name="get_page_snapshot",
        description="Get AI-optimized page structure. Use this first to understand what you're working with.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    types.Tool(
        name="inspect_element",
        description="Inspect an element by coordinates. Use this to get the element's ref. The result looks similar to Chrome DevTools' element inspector.",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {
                    "type": "integer",
                    "description": "X coordinate of the element",
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate of the element",
                },
                "num_ancestors": {
                    "type": "integer",
                    "description": "Number of ancestors to inspect",
                    "default": 3,
                },
            },
            "required": ["x", "y"],
        },
    ),
    types.Tool(
        name="inspect_html",
        description="Inspect an element by coordinates and optionally its ancestors, returning the raw HTML of the element. Use this to help get locator strings for elements.",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {
                    "type": "integer",
                    "description": "X coordinate of the element",
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate of the element",
                },
                "num_ancestors": {
                    "type": "integer",
                    "description": "Number of ancestors to inspect",
                    "default": 3,
                },
                "max_characters": {
                    "type": "integer",
                    "description": "Maximum characters in response.",
                    "default": 1024,
                },
            },
            "required": ["x", "y"],
        },
    ),
    types.Tool(
        name="find_element_by_ref",
        description="Find element by ref from snapshot. Use refs from page snapshots to locate elements precisely.",
        inputSchema={
            "type": "object",
            "properties": {
                "ref": {
                    "type": "string",
                    "description": "Element ref (e.g., 'e3')",
                }
            },
            "required": ["ref"],
        },
    ),
    types.Tool(
        name="get_page_screenshot",
        description="Take screenshot for visual understanding. Use when you need to see the page visually.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]

PLAYWRIGHT_TOOL_NAMES = [tool.name for tool in PLAYWRIGHT_TOOLS]


# Generic tools that work with the page but aren't strictly Playwright-specific
GENERIC_TOOLS = [
    types.Tool(
        name="execute_python_command",
        description="Execute a Python command to interact with the page",
        inputSchema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Python command to execute",
                }
            },
            "required": ["command"],
        },
    ),
]


async def _handle_get_page_snapshot(page, arguments):
    """Handler for get_page_snapshot tool."""
    result = await page.snapshot_for_ai()
    return [types.TextContent(type="text", text=result)]


async def _handle_inspect_element(page, arguments):
    """Handler for inspect_element tool."""
    x = arguments.get("x", 0)
    y = arguments.get("y", 0)
    num_ancestors = arguments.get("num_ancestors", 3)
    result = await page.inspect_element(x, y, num_ancestors)
    return [types.TextContent(type="text", text=str(result))]


async def _handle_inspect_html(page, arguments):
    """Handler for inspect_html tool."""
    x = arguments.get("x", 0)
    y = arguments.get("y", 0)
    num_ancestors = arguments.get("num_ancestors", 3)
    max_characters = arguments.get("max_characters", 1024)
    result = await page.inspect_html(x, y, num_ancestors, max_characters)
    return [types.TextContent(type="text", text=str(result))]


async def _handle_find_element_by_ref(page, arguments):
    """Handler for find_element_by_ref tool."""
    ref = arguments.get("ref", "")
    try:
        locator = page.locator(f"aria-ref={ref}")
        if await locator.count() > 0:
            locator_string = await locator.generate_locator_string()
            result = f"page.{locator_string}"
        else:
            result = "Element not found"
    except Exception as e:
        result = f"Error finding element: {e}"
    return [types.TextContent(type="text", text=result)]


async def _handle_get_page_screenshot(page, arguments):
    """Handler for get_page_screenshot tool."""
    try:
        import base64

        screenshot_bytes = await page.screenshot()
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        return [
            types.ImageContent(
                type="image", data=screenshot_base64, mimeType="image/png"
            )
        ]
    except Exception as e:
        error_msg = f"Error taking screenshot: {e}"
        return [types.TextContent(type="text", text=error_msg)]


async def _handle_execute_python_command(page, arguments, context=None):
    """Handler for execute_python_command tool with optional context support."""
    command = arguments.get("command", "")
    try:
        # Create execution context with captured output
        captured_output = []
        execution_context = {
            "page": page,
            "print": lambda *args: captured_output.append(
                " ".join(str(arg) for arg in args)
            ),
        }

        # Add context if provided (used by web agent)
        if context is not None:
            execution_context["context"] = context

        result = None
        # Handle async commands
        if "await " in command:
            # Wrap in async function and capture return value
            async_command = f"""
async def __execute_command():
    {command.replace(chr(10), chr(10) + "    ")}
    
__result = __execute_command()
"""
            exec(compile(async_command, "<string>", "exec"), execution_context)
            if "__result" in execution_context:
                result = await execution_context["__result"]
        else:
            # Execute synchronous command and capture return value
            result = exec(command, execution_context)

        # Build response message
        response_parts = []
        if captured_output:
            response_parts.append("Output: " + "\n".join(captured_output))
        if result is not None:
            response_parts.append(f"Return value: {result}")
        if not response_parts:
            response_parts.append("Command executed successfully")

        success_msg = f"Success: True\n{chr(10).join(response_parts)}"
        return [types.TextContent(type="text", text=success_msg)]
    except Exception as e:
        error_msg = f"Success: False\nError executing command: {e}"
        return [types.TextContent(type="text", text=error_msg)]


# Dictionary mapping tool names to their handler functions
PLAYWRIGHT_TOOL_HANDLERS = {
    "get_page_snapshot": _handle_get_page_snapshot,
    "inspect_element": _handle_inspect_element,
    "inspect_html": _handle_inspect_html,
    "find_element_by_ref": _handle_find_element_by_ref,
    "get_page_screenshot": _handle_get_page_screenshot,
}

# Dictionary mapping generic tool names to their handler functions
GENERIC_TOOL_HANDLERS = {
    "execute_python_command": _handle_execute_python_command,
}

# Combined handlers dictionary
ALL_TOOL_HANDLERS = {**PLAYWRIGHT_TOOL_HANDLERS, **GENERIC_TOOL_HANDLERS}
