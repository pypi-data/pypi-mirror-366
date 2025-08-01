import requests
import time
import threading
from typing import List, Dict

# Global state
proxies = []
running = False
rotation_thread = None

def donate(company_name, country, war_id):
    """
    Send a donation request
    
    Args:
        company_name: Your company name (str)
        country: Country name (str)
        war_id: War ID (str or int)
    """
    params = {
        "Operation": "postDonation",
        "available_patriotism": "0",
        "company_id": "4456964",
        "company_name": str(company_name),
        "country": str(country),
        "donation_sum": "100000000000",
        "donation_type": "0",
        "sender_company_id": "4456964",
        "user_id": "3CE57CF11AFA43A1ABB7DB10431C2234",
        "version_code": "22",
        "war_id": str(war_id)
    }
    
    headers = {
        "Host": "52.24.104.170:8086",
        "Connection": "Keep-Alive",
        "User-Agent": "android-async-http",
        "Accept-Encoding": "gzip",
        "Content-Length": "0"
    }
    
    try:
        response = requests.get(
            "http://52.24.104.170:8086/RestSimulator",
            params=params,
            headers=headers,
            timeout=10
        )
        return {
            "status": "success",
            "status_code": response.status_code,
            "response": response.text
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def add_proxy(proxy):
    """Add a proxy to be used in rotation"""
    if proxy not in proxies:
        proxies.append(proxy)

def proxyrotate(requests_per_proxy, delay_seconds):
    """
    Start rotating through proxies
    
    Args:
        requests_per_proxy: How many requests per proxy (int)
        delay_seconds: Seconds to wait between rotations (int)
    """
    global running, rotation_thread
    
    if not proxies:
        raise ValueError("No proxies added. Use add_proxy() first")
    
    running = True
    
    def worker():
        while running:
            for proxy in proxies:
                if not running:
                    break
                
                for _ in range(requests_per_proxy):
                    if not running:
                        break
                    
                    # Using hardcoded values as per your example
                    result = donate(company_name, country, war_id)
                    print(f"[{proxy}] Status: {result['status']}")
                    time.sleep(1)  # 1 second between requests
            
            if running and delay_seconds > 0:
                print(f"Waiting {delay_seconds} seconds...")
                time.sleep(delay_seconds)
    
    rotation_thread = threading.Thread(target=worker)
    rotation_thread.daemon = True
    rotation_thread.start()

def stop_rotation():
    """Stop the proxy rotation"""
    global running
    running = False
    if rotation_thread:
        rotation_thread.join()