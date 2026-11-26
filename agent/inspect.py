import asyncio
from typing import TypedDict
from urllib.parse import urlsplit

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from playwright.async_api import Route
from playwright.async_api import async_playwright

from agent.scope import ScopeError, load_scope_limit, normalize_and_check_url

NAVIGATION_TIMEOUT_MS = 60_000


class InspectOption(TypedDict):
    label: str
    kind: str


class PageDetails(TypedDict):
    title: str
    headings: list[str]
    options: list[InspectOption]


class BrowserUnavailableError(RuntimeError):
    """Raised when Playwright is installed but its Chromium binary is missing."""


async def extract_page_details(page: Page) -> PageDetails:
    return await page.evaluate(
        """() => {
            const root = document.querySelector("main") || document.body;
            const clean = (value) => value.replace(/\\s+/g, " ").trim();
            const headings = [...root.querySelectorAll("h1, h2, h3")]
                .map((heading) => clean(heading.innerText || heading.textContent || ""))
                .filter(Boolean)
                .slice(0, 20);
            const options = [];
            const seen = new Set();
            for (const element of root.querySelectorAll(
                "a[href], button, [role='button']"
            )) {
                const label = clean(
                    element.getAttribute("aria-label") ||
                    element.innerText ||
                    element.textContent ||
                    element.getAttribute("title") ||
                    ""
                ).slice(0, 160);
                if (!label || seen.has(label.toLowerCase())) continue;
                seen.add(label.toLowerCase());
                options.push({
                    label,
                    kind: element.matches("a[href]") ? "link" : "button"
                });
                if (options.length === 20) break;
            }
            return {
                title: clean(document.title || "").slice(0, 300),
                headings,
                options
            };
        }"""
    )


async def inspect_website(url: str) -> dict[str, object]:
    config = load_scope_limit()
    normalized_url = await asyncio.to_thread(normalize_and_check_url, url, config)
    blocked_navigation: str | None = None

    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(headless=True, args=["--disable-http2"])
        except PlaywrightError as error:
            raise BrowserUnavailableError(
                "The Playwright Chromium browser is not installed. "
                "Run `playwright install chromium`."
            ) from error

        try:
            context = await browser.new_context(
                service_workers="block",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                java_script_enabled=False,
            )

            async def guard_request(route: Route) -> None:
                nonlocal blocked_navigation
                request = route.request
                if request.resource_type in {"image", "font", "media"}:
                    await route.abort()
                    return

                is_navigation = request.is_navigation_request()
                try:
                    await asyncio.to_thread(
                        normalize_and_check_url,
                        request.url,
                        config,
                        enforce_scope=is_navigation,
                    )
                except ScopeError as error:
                    if is_navigation:
                        blocked_navigation = str(error)
                    await route.abort()
                    return

                await route.continue_()

            await context.route("**/*", guard_request)
            page = await context.new_page()
            try:
                await page.goto(
                    normalized_url,
                    wait_until="domcontentloaded",
                    timeout=NAVIGATION_TIMEOUT_MS,
                )
            except PlaywrightError as error:
                if blocked_navigation:
                    raise ScopeError(blocked_navigation) from error
                raise RuntimeError("The website did not finish loading.") from error

            details = await extract_page_details(page)
        finally:
            await browser.close()

    title = str(details["title"]).strip()
    options = details["options"]
    labels = [option["label"] for option in options]
    site_name = title or urlsplit(normalized_url).hostname or "the website"
    if labels:
        summary = (
            f"I opened {site_name}. Here is what I can help with on this site: "
            f"{', '.join(labels[:5])}."
        )
    else:
        summary = (
            f"I opened {site_name}. I couldn't find any main links or buttons on this page."
        )

    return {
        "url": normalized_url,
        "title": title,
        "headings": details["headings"],
        "options": options,
        "summary": summary,
    }
