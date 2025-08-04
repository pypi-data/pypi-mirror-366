from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class CloudflareBypassResult:
    """Result object for Cloudflare bypass operation"""
    success: bool
    cookies: List[Dict[str, Any]]
    html: str
    title: str
    error: Optional[str] = None

class CloudflareBypass:
    """Main class for bypassing Cloudflare protection"""
    
    def __init__(self, 
                 headless: bool = False, 
                 timeout: int = 60000,
                 wait_time: int = 10,
                 save_html: bool = True):
        """
        Initialize CloudflareBypass instance
        
        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Global timeout in milliseconds
            wait_time (int): Maximum time to wait for challenge in seconds
            save_html (bool): Whether to save HTML content to file
        """
        self.headless = headless
        self.timeout = timeout
        self.wait_time = wait_time
        self.save_html = save_html

    def _is_cloudflare_challenge(self, page) -> bool:
        """Check if current page is a Cloudflare challenge page"""
        try:
            return page.query_selector("iframe[title*='challenge']") is not None or \
                   page.query_selector("div#challenge-running") is not None or \
                   "challenge" in page.title().lower() or \
                   "cloudflare" in page.title().lower()
        except:
            return False

    def _solve_challenge(self, page) -> bool:
        """Attempt to solve the Cloudflare challenge automatically"""
        try:
            challenge_frame = page.frame_locator("iframe[title*='challenge']")
            if not challenge_frame:
                return False

            # Try different selectors for verify button
            verify_button_selectors = [
                "input[type='button'][value*='Verify']",
                "input[type='submit'][value*='Verify']",
                "button:has-text('Verify')",
                "#challenge-stage button",
                "[class*='button'][class*='verify']",
                "[class*='btn'][class*='verify']"
            ]

            for selector in verify_button_selectors:
                try:
                    button = challenge_frame.locator(selector)
                    if button.is_visible(timeout=5000):
                        print(f"[INFO] Found verify button with selector: {selector}")
                        button.click(delay=100)
                        return True
                except:
                    continue

            # Try checkbox challenge
            checkbox_selectors = [
                "input[type='checkbox']",
                "#checkbox",
                "[class*='checkbox']"
            ]

            for selector in checkbox_selectors:
                try:
                    checkbox = challenge_frame.locator(selector)
                    if checkbox.is_visible(timeout=5000):
                        print(f"[INFO] Found checkbox with selector: {selector}")
                        checkbox.check(force=True)
                        return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"[ERROR] Error in solve_challenge: {str(e)}")
            return False

    def _wait_for_challenge(self, page) -> bool:
        """Wait for challenge to be solved"""
        start_time = time.time()
        max_wait = self.wait_time

        while time.time() - start_time < max_wait:
            if self._is_cloudflare_challenge(page):
                print("[INFO] Attempting to solve challenge automatically...")
                if self._solve_challenge(page):
                    print("[INFO] Challenge solution attempted, waiting for result...")
                    time.sleep(2)
                else:
                    print("[INFO] No interactive elements found, waiting...")
            else:
                print("[INFO] No challenge detected or challenge completed")
                return True
                
            time.sleep(1)
        
        return False

    def bypass(self, url: str, proxy: Optional[str] = None) -> CloudflareBypassResult:
        """
        Bypass Cloudflare protection for a given URL
        
        Args:
            url (str): Target URL
            proxy (str, optional): Proxy server URL (e.g., "http://user:pass@host:port")
            
        Returns:
            CloudflareBypassResult: Result object containing success status, cookies, HTML content
        """
        try:
            with sync_playwright() as p:
                launch_args = {
                    "headless": self.headless,
                }

                if proxy:
                    launch_args["proxy"] = {
                        "server": proxy
                    }

                browser = p.chromium.launch(**launch_args)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    color_scheme='dark',
                    locale='en-US',
                    timezone_id='Europe/London',
                    permissions=['notifications']
                )

                page = context.new_page()
                page.set_default_timeout(self.timeout)

                page.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'DNT': '1',
                    'Upgrade-Insecure-Requests': '1'
                })

                print(f"[INFO] Navigating to: {url}")
                page.goto(url, wait_until="domcontentloaded")

                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except PlaywrightTimeout:
                    print("[INFO] Initial networkidle timeout - continuing anyway")

                if self._is_cloudflare_challenge(page):
                    print("[INFO] Detected Cloudflare challenge, attempting to solve...")
                    challenge_solved = self._wait_for_challenge(page)
                    
                    if not challenge_solved:
                        raise Exception("Challenge solution timeout")

                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except PlaywrightTimeout:
                    print("[INFO] Final networkidle timeout - continuing anyway")

                title = page.title()
                cookies = context.cookies()
                content = page.content()

                print(f"[SUCCESS] Page title: {title}")
                print(f"[INFO] Found {len(cookies)} cookies")
                
                for cookie in cookies:
                    if any(k in cookie['name'].lower() for k in ['cf_', 'cloudflare']):
                        print(f"[COOKIE] {cookie['name']}: {cookie['value']}")

                if self.save_html:
                    with open("page.html", "w", encoding="utf-8") as f:
                        f.write(content)
                        print("[INFO] HTML saved: page.html")

                browser.close()

                return CloudflareBypassResult(
                    success=True,
                    cookies=cookies,
                    html=content,
                    title=title
                )

        except Exception as e:
            error_msg = f"Bypass failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return CloudflareBypassResult(
                success=False,
                cookies=[],
                html="",
                title="",
                error=error_msg
            )