import asyncio
import socket
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from playwright.async_api import async_playwright

from agent.inspect import extract_page_details
from agent.main import app
from agent.scope import ScopeError, ScopeLimit, normalize_and_check_url


class ScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.public_dns = patch(
            "agent.scope.socket.getaddrinfo",
            return_value=[
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))
            ],
        )
        self.public_dns.start()
        self.addCleanup(self.public_dns.stop)

    def test_normalizes_public_url_and_allows_configured_subdomain(self) -> None:
        config = ScopeLimit(mode="single-site", allowedDomains=["example.com"])

        normalized = normalize_and_check_url("shop.example.com", config)

        self.assertEqual(normalized, "https://shop.example.com/")

    def test_rejects_out_of_scope_and_private_targets(self) -> None:
        config = ScopeLimit(mode="multi-site", allowedDomains=["example.com"])

        with self.assertRaises(ScopeError):
            normalize_and_check_url("other.com", config)
        with self.assertRaises(ScopeError):
            normalize_and_check_url("http://127.0.0.1", ScopeLimit(
                mode="open", allowedDomains=[]
            ))

    def test_checks_scope_before_resolving_an_out_of_scope_domain(self) -> None:
        config = ScopeLimit(mode="single-site", allowedDomains=["allowed.example"])
        with patch("agent.scope.socket.getaddrinfo") as resolver:
            with self.assertRaises(ScopeError):
                normalize_and_check_url("outside.example", config)
        resolver.assert_not_called()

    def test_inspect_endpoint_returns_scope_error_as_forbidden(self) -> None:
        response = TestClient(app).post(
            "/inspect",
            json={"url": "http://127.0.0.1"},
        )

        self.assertEqual(response.status_code, 403)


class PageExtractionTests(unittest.TestCase):
    def test_extracts_only_read_only_headings_and_clickable_labels(self) -> None:
        async def extract() -> dict[str, object]:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.set_content(
                        """
                        <title>Example Support</title>
                        <main>
                          <h1>Welcome</h1>
                          <h2>Find help</h2>
                          <a href="/help">Get help</a>
                          <button type="submit">Continue</button>
                          <button aria-label="Contact us">Ignored text</button>
                          <form><input value="private value"></form>
                        </main>
                        """
                    )
                    return await extract_page_details(page)
                finally:
                    await browser.close()

        details = asyncio.run(extract())

        self.assertEqual(details["title"], "Example Support")
        self.assertEqual(details["headings"], ["Welcome", "Find help"])
        self.assertEqual(
            details["options"],
            [
                {"label": "Get help", "kind": "link"},
                {"label": "Continue", "kind": "button"},
                {"label": "Contact us", "kind": "button"},
            ],
        )

    def test_limits_options_to_twenty(self) -> None:
        async def extract() -> dict[str, object]:
            buttons = "".join(f"<button>Option {index}</button>" for index in range(25))
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.set_content(f"<main>{buttons}</main>")
                    return await extract_page_details(page)
                finally:
                    await browser.close()

        details = asyncio.run(extract())

        self.assertEqual(len(details["options"]), 20)
        self.assertEqual(details["options"][-1]["label"], "Option 19")


if __name__ == "__main__":
    unittest.main()
