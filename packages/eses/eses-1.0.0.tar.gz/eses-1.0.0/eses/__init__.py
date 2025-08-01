import requests
import time
from itertools import cycle
import threading

# Default configuration
api_url = "http://52.24.104.170:8086/RestSimulator"
default_params = {
    "Operation": "postDonation",
    "available_patriotism": "0",
    "company_id": "4456964",
    "donation_sum": "100000000000",
    "donation_type": "0",
    "sender_company_id": "4456964",
    "user_id": "3CE57CF11AFA43A1ABB7DB10431C2234",
    "version_code": "22"
}

default_headers = {
    "Host": "52.24.104.170:8086",
    "Connection": "Keep-Alive",
    "User-Agent": "android-async-http",
    "Accept-Encoding": "gzip",
    "Content-Length": "0"
}

# Proxy management
proxies = []
proxy_cycle = None
running = False
rotation_thread = None

def donate(company_name="EPSAT", country="Bulgaria", war_id="55032"):
    """
    Send a donation request with customizable parameters
    
    Args:
        company_name (str): Name of the company (default: "EPSAT")
        country (str): Country name (default: "Bulgaria")
        war_id (str): War ID (default: "55032")
        
    Returns:
        dict: Dictionary containing status, status_code, and response/error
    """
    params = default_params.copy()
    params.update({
        "company_name": company_name,
        "country": country,
        "war_id": war_id
    })
    
    try:
        response = requests.get(
            api_url,
            params=params,
            headers=default_headers,
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
    """
    Add a proxy to the proxy list
    
    Args:
        proxy (str): Proxy address in format 'http://host:port' or 
                    'http://username:password@host:port'
    """
    if proxy not in proxies:
        proxies.append(proxy)
        global proxy_cycle
        proxy_cycle = cycle(proxies)
        return f"Proxy added: {proxy}"
    return f"Proxy already exists: {proxy}"

def clear_proxies():
    """Clear all proxies from the proxy list"""
    global proxies, proxy_cycle
    proxies = []
    proxy_cycle = None
    return "All proxies cleared"

def proxyrotate(requests_per_proxy=3, delay_between_rotations=20):
    """
    Rotate through proxies making requests
    
    Args:
        requests_per_proxy (int): Number of requests to make per proxy (default: 3)
        delay_between_rotations (int): Seconds to wait between full rotations (default: 20)
        
    Returns:
        threading.Thread: The rotation thread object
    """
    global running, proxy_cycle, rotation_thread
    
    if not proxies:
        raise ValueError("No proxies available. Add proxies using add_proxy()")
    
    if proxy_cycle is None:
        proxy_cycle = cycle(proxies)
    
    running = True
    
    def rotation_worker():
        while running:
            for proxy in proxies:
                if not running:
                    break
                
                proxy_config = {
                    'http': proxy,
                    'https': proxy
                }
                
                for i in range(requests_per_proxy):
                    if not running:
                        break
                    
                    try:
                        result = donate()
                        print(f"[Proxy: {proxy}] Request {i+1}/{requests_per_proxy}: {result['status']} (Status: {result.get('status_code', 'N/A')})")
                    except Exception as e:
                        print(f"[Proxy: {proxy}] Request {i+1}/{requests_per_proxy} failed: {str(e)}")
                    
                    time.sleep(1)  # Small delay between requests
            
            if running:
                print(f"Rotation complete. Waiting {delay_between_rotations} seconds...")
                for _ in range(delay_between_rotations):
                    if not running:
                        break
                    time.sleep(1)
    
    rotation_thread = threading.Thread(target=rotation_worker)
    rotation_thread.daemon = True
    rotation_thread.start()
    return rotation_thread

def stop_rotation():
    """Stop the proxy rotation"""
    global running
    running = False
    if rotation_thread and rotation_thread.is_alive():
        rotation_thread.join(timeout=2)
    return "Rotation stopped"

def get_proxy_list():
    """Get the current list of proxies"""
    return proxies.copy()

def set_default_param(key, value):
    """
    Set a default parameter value
    
    Args:
        key (str): Parameter key
        value (str): Parameter value
    """
    if key in default_params:
        default_params[key] = value
        return f"Updated {key}"
    else:
        raise KeyError(f"Invalid parameter key: {key}")

def set_default_header(key, value):
    """
    Set a default header value
    
    Args:
        key (str): Header key
        value (str): Header value
    """
    default_headers[key] = value
    return f"Updated {key}"

# Initialize proxy cycle if proxies exist
if proxies:
    proxy_cycle = cycle(proxies)