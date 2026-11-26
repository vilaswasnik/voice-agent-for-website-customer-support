import ipaddress
import json
import re
import socket
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel, ValidationError

SCOPE_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "scope-limit.json"
_DOMAIN_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


class ScopeError(ValueError):
    """Raised when an inspect target is malformed or outside the site fence."""


class ScopeLimit(BaseModel):
    mode: str
    allowedDomains: list[str]


def load_scope_limit() -> ScopeLimit:
    try:
        raw_config = json.loads(SCOPE_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError("The website scope configuration could not be loaded.") from error

    try:
        config = ScopeLimit.model_validate(raw_config)
    except ValidationError as error:
        raise RuntimeError("The website scope configuration is invalid.") from error

    if config.mode not in {"single-site", "multi-site", "open"}:
        raise RuntimeError("The website scope mode must be single-site, multi-site, or open.")

    try:
        normalized_domains = [normalize_domain(domain) for domain in config.allowedDomains]
    except ScopeError as error:
        raise RuntimeError("The website scope contains an invalid allowed domain.") from error

    if config.mode == "single-site" and len(normalized_domains) != 1:
        raise RuntimeError("Single-site scope requires exactly one allowed domain.")
    if config.mode == "multi-site" and not normalized_domains:
        raise RuntimeError("Multi-site scope requires at least one allowed domain.")

    config.allowedDomains = normalized_domains
    return config


def normalize_domain(domain: str) -> str:
    if not domain or domain != domain.strip() or "/" in domain or ":" in domain:
        raise ScopeError("Allowed domains must be host names without a scheme or path.")
    try:
        normalized = domain.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError as error:
        raise ScopeError("The allowed domain is invalid.") from error

    try:
        ipaddress.ip_address(normalized)
    except ValueError:
        pass
    else:
        raise ScopeError("Allowed domains must be DNS names, not IP addresses.")

    if len(normalized) > 253 or not all(
        _DOMAIN_LABEL.fullmatch(label) for label in normalized.split(".")
    ):
        raise ScopeError("The allowed domain is invalid.")
    return normalized


def normalize_and_check_url(
    url: str,
    config: ScopeLimit | None = None,
    *,
    enforce_scope: bool = True,
) -> str:
    candidate = url.strip()
    if not candidate or len(candidate) > 2048:
        raise ScopeError("Enter a website address no longer than 2048 characters.")
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    try:
        parsed = urlsplit(candidate)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise ScopeError("Enter a valid website address.") from error

    if parsed.scheme.lower() not in {"http", "https"} or not hostname:
        raise ScopeError("Only public HTTP and HTTPS websites can be inspected.")
    if parsed.username is not None or parsed.password is not None:
        raise ScopeError("Website addresses cannot include a username or password.")
    if port not in {None, 80, 443}:
        raise ScopeError("Only standard HTTP and HTTPS ports can be inspected.")

    try:
        normalized_host = hostname.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError as error:
        raise ScopeError("Enter a valid website address.") from error
    if config is None:
        config = load_scope_limit()
    if enforce_scope and config.mode != "open" and not any(
        normalized_host == domain or normalized_host.endswith(f".{domain}")
        for domain in config.allowedDomains
    ):
        raise ScopeError("This website is outside the configured allowed domains.")
    _ensure_public_host(normalized_host)

    netloc = normalized_host
    if ":" in normalized_host:
        netloc = f"[{normalized_host}]"
    if port is not None:
        netloc = f"{netloc}:{port}"
    return urlunsplit(
        (
            parsed.scheme.lower(),
            netloc,
            parsed.path or "/",
            parsed.query,
            "",
        )
    )


def _ensure_public_host(hostname: str) -> None:
    if hostname in {"localhost"} or hostname.endswith((".localhost", ".local", ".internal")):
        raise ScopeError("Local and internal websites cannot be inspected.")

    try:
        addresses = {ipaddress.ip_address(hostname)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(result[4][0])
                for result in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
            }
        except (OSError, ValueError) as error:
            raise ScopeError("The website address could not be resolved.") from error

    if not addresses or any(not address.is_global for address in addresses):
        raise ScopeError("Only websites resolving to public IP addresses can be inspected.")
