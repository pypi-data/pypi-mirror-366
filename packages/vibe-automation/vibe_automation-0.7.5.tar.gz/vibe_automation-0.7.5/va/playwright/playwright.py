import asyncio
import logging
import os
from contextlib import asynccontextmanager, contextmanager

from stagehand import Stagehand, StagehandConfig, StagehandPage
from stagehand.context import StagehandContext

from .page import Page as VibePage

logger = logging.getLogger(__name__)


class WrappedContext:
    """Browser context wrapper that automatically wraps pages with VibePage functionality."""

    def __init__(
        self, stagehand_context: StagehandContext, stagehand_pages: list[StagehandPage]
    ):
        self._stagehand_context = stagehand_context
        self._pages = []
        for stagehand_page in stagehand_pages:
            self._pages.append(VibePage(stagehand_page))

    @property
    def pages(self):
        return self._pages

    async def _wait_for_login_tasks(self):
        """Wait for any background login tasks to complete before closing"""
        for page in self._pages:
            await page._wait_for_login_task()

    def __getattr__(self, name):
        # Forward attribute lookups to the underlying StagehandContext
        attr = getattr(self._stagehand_context, name)

        # Special handling for methods that return pages
        if name == "new_page":
            # Replace with our own implementation that wraps the page
            async def wrapped_new_page(*args, **kwargs):
                stagehand_page = await self._stagehand_context.new_page(*args, **kwargs)
                vibe_page = VibePage(stagehand_page)
                self._pages.append(vibe_page)
                return vibe_page

            return wrapped_new_page

        return attr


def get_browser(headless: bool | None = None, slow_mo: float | None = None):
    """Get browser - use get_browser_sync for sync contexts or get_browser_async for async contexts"""
    # For backward compatibility, try to detect if we're in async context
    import asyncio

    try:
        asyncio.get_running_loop()
        # We're in an async context, but this function is sync
        # We'll return the sync version and let the user handle async properly
        return get_browser_sync(headless, slow_mo)
    except RuntimeError:
        # No event loop, use sync version
        return get_browser_sync(headless, slow_mo)


@contextmanager
def get_browser_sync(headless: bool | None = None, slow_mo: float | None = None):
    """Recommended way to get a Playwright browser instance in Vibe Automation Framework.

    There are three running modes:
    1. during local development, we can get a local browser instance
    2. in managed execution environment, the browser instance are provided by Orby. This is
       activated via the presence of CONNECTION_URL.
    Returns a wrapped browser that automatically wraps pages with VibePage functionality
    when new_page() is called, eliminating the need for manual wrap() calls.
    """
    try:
        wrapped_context, stagehand = asyncio.run(
            create_browser_context_async(headless, slow_mo)
        )
        yield wrapped_context
    finally:
        # Wait for any background login tasks before closing
        asyncio.run(wrapped_context._wait_for_login_tasks())
        asyncio.run(stagehand.close())


@asynccontextmanager
async def get_browser_context(
    headless: bool | None = None, slow_mo: float | None = None
):
    """Async version of get_browser for use in async contexts."""

    try:
        wrapped_context, stagehand = await create_browser_context_async(
            headless, slow_mo
        )
        yield wrapped_context
    finally:
        # Wait for any background login tasks before closing
        await wrapped_context._wait_for_login_tasks()
        await stagehand.close()


async def create_browser_context_async(
    headless: bool | None = None, slow_mo: float | None = None
):
    """Create a browser context"""
    connection_url = os.environ.get("CONNECTION_URL")
    if connection_url:
        # Connect to existing browser instance via CDP
        local_browser_launch_options = {
            "cdp_url": connection_url,
        }
    else:
        # Launch a new browser instance
        local_browser_launch_options = {
            "headless": headless,
            "slow_mo": slow_mo,
            # scale ratio is set to 1 to ensure coordinates are calculated correctly
            "args": ["--force-device-scale-factor=1"],
        }

    config = StagehandConfig(
        env="LOCAL",
        model_name="claude-3-7-sonnet-20250219",
        model_client_options={"apiKey": os.getenv("ANTHROPIC_API_KEY")},
        local_browser_launch_options=local_browser_launch_options,
    )

    stagehand = Stagehand(config)
    await stagehand.init()
    stagehand.context.set_default_timeout(5000)  # 5s timeout
    stagehand_pages = await stagehand.context.pages()

    wrapped_context = WrappedContext(stagehand.context, stagehand_pages)

    return wrapped_context, stagehand
