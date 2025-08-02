import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Optional, Dict, Any

# API Configuration
api_url = "http://52.24.104.170:8086/RestSimulator"
proxies: List[str] = []
proxy_lock = threading.Lock()
active_threads: List[threading.Thread] = []

# Debug Utilities
def _print_debug(msg: str) -> None:
    """Print debug messages with timestamps"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}")

# Core Functions
def addproxy(proxy: str) -> None:
    """Add a proxy to the rotation pool"""
    if not proxy.startswith(('http://', 'https://')):
        proxy = f"http://{proxy}"
    
    with proxy_lock:
        if proxy not in proxies:
            proxies.append(proxy)
            _print_debug(f"Proxy added: {proxy}")
        else:
            _print_debug(f"Proxy already exists: {proxy}")

def clear_proxies() -> None:
    """Clear all registered proxies"""
    with proxy_lock:
        proxies.clear()
    _print_debug("All proxies cleared")

def donate(
    company_name: str,
    country: str,
    war_id: str,
    donation_sum: str = "100000000000",
    proxy: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Send a single donation request
    Returns: JSON response if successful, None otherwise
    """
    params = {
        "Operation": "postDonation",
        "available_patriotism": "0",
        "company_id": "4456964",
        "company_name": company_name,
        "country": country,
        "donation_sum": donation_sum,
        "donation_type": "0",
        "sender_company_id": "4456964",
        "user_id": "3CE57CF11AFA43A1ABB7DB10431C2234",
        "version_code": "22",
        "war_id": war_id
    }

    proxy_display = proxy or "DIRECT"
    _print_debug(f"Starting donation: {company_name} via {proxy_display}")

    try:
        start_time = time.time()
        response = requests.post(
            api_url,
            params=params,
            headers={"Content-Length": "0"},
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=10
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        _print_debug(f"Success ({response.status_code}) in {elapsed_ms}ms")
        _print_debug(f"Response: {response.text[:200]}")
        return response.json()
    except Exception as e:
        _print_debug(f"Failed via {proxy_display}: {str(e)}")
        return None

def donatewithproxy(
    company_name: str,
    country: str,
    war_id: str,
    times: int = 1,
    delay: int = 0,
    max_workers: int = 10
) -> None:
    """
    Start automated concurrent donations with proxy rotation
    Args:
        times: Requests per proxy per cycle
        delay: Seconds between full cycles
        max_workers: Max concurrent requests (default: 10)
    """
    def _worker():
        cycle = 0
        while True:
            cycle += 1
            _print_debug(f"=== START CYCLE {cycle} ===")
            
            # Get proxies (thread-safe)
            with proxy_lock:
                current_proxies = proxies.copy() or [None]
            
            # Process all proxies concurrently
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Schedule all requests
                futures = []
                for proxy in current_proxies:
                    for _ in range(times):
                        futures.append(
                            executor.submit(
                                donate,
                                company_name,
                                country,
                                war_id,
                                proxy=proxy
                            )
                        )
                
                # Wait for completion
                for future in futures:
                    try:
                        future.result(timeout=30)
                    except Exception as e:
                        _print_debug(f"Request failed: {str(e)}")
            
            # Cycle complete
            _print_debug(f"Cycle {cycle} complete. Waiting {delay}s...")
            time.sleep(delay)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    active_threads.append(thread)
    _print_debug(f"Started donation controller (ID: {thread.ident})")

def stop_all_donations() -> None:
    """Gracefully stop all active donation threads"""
    for thread in active_threads:
        thread.join(timeout=1)
    active_threads.clear()
    _print_debug("All donation threads stopped")

# Make functions available at package level
__all__ = [
    'addproxy',
    'clear_proxies',
    'donate',
    'donatewithproxy',
    'stop_all_donations'
]