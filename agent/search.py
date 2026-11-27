"""Search inside a single website and read back the top results.

Read-only at the website level: the agent only types into the site search box
and reads the results page. It never logs in, never fills any other form,
and never stores personal data.
"""

import asyncio
import re
from typing import TypedDict
from urllib.parse import urljoin, urlsplit

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from playwright.async_api import Route
from playwright.async_api import async_playwright

from agent.inspect import NAVIGATION_TIMEOUT_MS, BrowserUnavailableError
from agent.scope import ScopeError, load_scope_limit, normalize_and_check_url

RESULTS_LIMIT = 10
SUMMARY_TITLES = 3
RESULTS_TIMEOUT_MS = 15_000

# The search input on the site, tried in DOM order. The first visible match wins.
SEARCH_INPUT_SELECTOR = (
    "input[type=search], input[name=q], input[name=search], "
    "input[placeholder*=Search i], input[aria-label*=Search i]"
)

# Where result links live, most specific first. The first selector that
# yields results wins, so the result list from the site is used when present.
RESULT_LINK_SELECTORS = [
    ".mw-search-result-heading a",
    "[class*=search-result i] a",
    "[id*=results i] a",
    "main h2 a",
    "main h3 a",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class SearchResultItem(TypedDict):
    title: str
    url: str


class SearchResult(TypedDict):
    url: str
    query: str
    site: str
    title: str
    results: list[SearchResultItem]
    summary: str


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _site_name(normalized_url: str) -> str:
    hostname = urlsplit(normalized_url).hostname or normalized_url
    return hostname.removeprefix("www.").split(".")[0].capitalize()


async def _find_search_input(page: Page):
    """Return the first visible search input, or None if the site has none."""
    locator = page.locator(SEARCH_INPUT_SELECTOR)
    try:
        await locator.first.wait_for(state="attached", timeout=5_000)
    except PlaywrightError:
        pass
    count = await locator.count()
    for index in range(count):
        candidate = locator.nth(index)
        try:
            await candidate.wait_for(state="visible", timeout=2_000)
            return candidate
        except PlaywrightError:
            continue
    role_locator = page.get_by_role("searchbox")
    count = await role_locator.count()
    for index in range(count):
        candidate = role_locator.nth(index)
        try:
            await candidate.wait_for(state="visible", timeout=2_000)
            return candidate
        except PlaywrightError:
            continue
    return None


async def _extract_results(page: Page) -> list[SearchResultItem]:
    """Collect up to RESULTS_LIMIT result titles and links from the page."""
    base_url = page.url
    seen: set[str] = set()
    for selector in RESULT_LINK_SELECTORS:
        results: list[SearchResultItem] = []
        locator = page.locator(selector)
        count = await locator.count()
        for index in range(count):
            if len(results) >= RESULTS_LIMIT:
                break
            link = locator.nth(index)
            href = await link.get_attribute("href")
            if not href:
                continue
            title = _clean_text(await link.inner_text() or "")
            if not title:
                title = _clean_text(
                    (await link.get_attribute("aria-label") or "")
                    or (await link.get_attribute("title") or "")
                )
            if not title:
                continue
            absolute = urljoin(base_url, href)
            if absolute.startswith(("javascript:", "mailto:")):
                continue
            if absolute == base_url or absolute in seen:
                continue
            seen.add(absolute)
            results.append({"title": title[:200], "url": absolute})
        if results:
            return results
    return []


def _build_summary(site: str, query: str, results: list[SearchResultItem]) -> str:
    if not results:
        return f"I searched {site} for \"{query}\", but I could not find any results."
    named = [item["title"] for item in results[:SUMMARY_TITLES]]
    if len(results) == 1:
        return f"I searched {site} for \"{query}\". Here is the top result: {named[0]}."
    joined = "; ".join(named)
    return f"I searched {site} for \"{query}\". Here are the top results: {joined}."


async def search_site(url: str, query: str) -> dict[str, object]:
    """Search one website for a query and return the top results."""
    config = load_scope_limit()
    normalized_url = normalize_and_check_url(url, config)
    clean_query = query.strip()
    if not clean_query:
        raise ValueError("Enter something to search for.")
    site = _site_name(normalized_url)

    try:
        playwright = await async_playwright().start()
    except Exception as exc:
        raise BrowserUnavailableError(
            "Playwright is installed but its browser could not be started."
        ) from exc

    blocked_navigation: str | None = None
    try:
        browser = await playwright.chromium.launch(
            headless=True, args=["--disable-http2"]
        )
        try:
            context = await browser.new_context(
                service_workers="block",
                user_agent=USER_AGENT,
            )
            page = await context.new_page()

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

            await page.route("**/*", guard_request)
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

            title = (await page.title()).strip() or site
            search_input = await _find_search_input(page)
            if search_input is None:
                return {
                    "url": normalized_url,
                    "query": clean_query,
                    "site": site,
                    "title": title,
                    "results": [],
                    "summary": f"I could not find a search box on {site}.",
                }

            await search_input.fill(clean_query)
            previous_url = page.url
            await search_input.press("Enter")
            try:
                await page.wait_for_url(
                    lambda current: current != previous_url,
                    timeout=RESULTS_TIMEOUT_MS,
                )
            except PlaywrightError:
                # The search may update the same page without navigating.
                pass
            await page.wait_for_load_state(
                "domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS
            )
            title = (await page.title()).strip() or title
            results = await _extract_results(page)
            return {
                "url": page.url,
                "query": clean_query,
                "site": site,
                "title": title,
                "results": results,
                "summary": _build_summary(site, clean_query, results),
            }
        finally:
            await browser.close()
    finally:
        await playwright.stop()
