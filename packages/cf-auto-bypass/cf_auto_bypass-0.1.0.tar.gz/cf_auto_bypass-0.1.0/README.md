# CF Auto Bypass

A Python library to automatically bypass Cloudflare's JavaScript challenges and protection mechanisms.

## Features

- Automatic Cloudflare JavaScript challenge solving
- Support for proxy configuration
- Browser fingerprint customization
- Cookie management
- Detailed error handling and logging

## Installation

```bash
pip install cf-auto-bypass
```

## Quick Start

```python
from cf_auto_bypass import CloudflareBypass

# Create a bypass instance
bypass = CloudflareBypass(headless=False)

# Bypass Cloudflare protection
result = bypass.bypass("https://example.com")

if result.success:
    print(f"Title: {result.title}")
    print(f"Cookies: {result.cookies}")
    print(f"HTML content length: {len(result.html)}")
else:
    print(f"Error: {result.error}")
```

## Advanced Usage

```python
# Using with proxy
bypass = CloudflareBypass(
    headless=True,
    timeout=60000,
    wait_time=15
)

result = bypass.bypass(
    url="https://example.com",
    proxy="http://user:pass@proxy.example.com:8080"
)
```

## License

MIT License - see LICENSE file for details.