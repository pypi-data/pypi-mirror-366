import requests
import time
from itertools import cycle
import threading

class ESES:
    def __init__(self):
        # Default configuration
        self.api_url = "http://52.24.104.170:8086/RestSimulator"
        self.default_params = {
            "Operation": "postDonation",
            "available_patriotism": "0",
            "company_id": "4456964",
            "donation_sum": "100000000000",
            "donation_type": "0",
            "sender_company_id": "4456964",
            "user_id": "3CE57CF11AFA43A1ABB7DB10431C2234",
            "version_code": "22"
        }

        self.default_headers = {
            "Host": "52.24.104.170:8086",
            "Connection": "Keep-Alive",
            "User-Agent": "android-async-http",
            "Accept-Encoding": "gzip",
            "Content-Length": "0"
        }

        # Proxy management
        self.proxies = []
        self.proxy_cycle = None
        self.running = False
        self.rotation_thread = None
        self.current_donation_params = {}

    def donate(self, company_name, country, war_id):
        """
        Send a donation request with required parameters
        
        Args:
            company_name (str): Name of the company (required)
            country (str): Country name (required)
            war_id (str): War ID (required)
            
        Returns:
            dict: Dictionary containing status, status_code, and response/error
        """
        if not all([company_name, country, war_id]):
            raise ValueError("company_name, country, and war_id are all required parameters")

        # Store the current donation parameters
        self.current_donation_params = {
            "company_name": company_name,
            "country": country,
            "war_id": war_id
        }

        params = self.default_params.copy()
        params.update(self.current_donation_params)
        
        try:
            response = requests.get(
                self.api_url,
                params=params,
                headers=self.default_headers,
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

    def add_proxy(self, proxy):
        """
        Add a proxy to the proxy list (format: ip:port)
        
        Args:
            proxy (str): Proxy address in format 'ip:port'
        """
        # Validate proxy format
        if ":" not in proxy:
            raise ValueError("Proxy must be in format ip:port")
        
        # Convert to http://ip:port format
        formatted_proxy = f"http://{proxy}"
        
        if formatted_proxy not in self.proxies:
            self.proxies.append(formatted_proxy)
            self.proxy_cycle = cycle(self.proxies)
            return f"Proxy added: {proxy}"
        return f"Proxy already exists: {proxy}"

    def clear_proxies(self):
        """Clear all proxies from the proxy list"""
        self.proxies = []
        self.proxy_cycle = None
        return "All proxies cleared"

    def rotateproxy(self, requests_per_proxy=None, delay_after_rotation=None):
        """
        Rotate through proxies making requests using current donation parameters
        
        Args:
            requests_per_proxy (int): Number of requests to make per proxy (required)
            delay_after_rotation (int): Seconds to wait after using all proxies (required)
            
        Returns:
            threading.Thread: The rotation thread object
        """
        # Validate required parameters
        if requests_per_proxy is None:
            raise ValueError("requests_per_proxy is required")
        if delay_after_rotation is None:
            raise ValueError("delay_after_rotation is required")
            
        if not self.current_donation_params:
            raise ValueError("No donation parameters set. Call donate() first")
            
        if not self.proxies:
            raise ValueError("No proxies available. Add proxies using add_proxy()")
        
        if self.proxy_cycle is None:
            self.proxy_cycle = cycle(self.proxies)
        
        self.running = True
        
        def rotation_worker():
            while self.running:
                for proxy in self.proxies:
                    if not self.running:
                        break
                    
                    for i in range(requests_per_proxy):
                        if not self.running:
                            break
                        
                        try:
                            result = self.donate(
                                self.current_donation_params["company_name"],
                                self.current_donation_params["country"],
                                self.current_donation_params["war_id"]
                            )
                            print(f"[Proxy: {proxy}] Request {i+1}/{requests_per_proxy}: {result['status']} (Status: {result.get('status_code', 'N/A')})")
                        except Exception as e:
                            print(f"[Proxy: {proxy}] Request {i+1}/{requests_per_proxy} failed: {str(e)}")
                        
                        time.sleep(1)
                
                if self.running:
                    print(f"Rotation complete. Waiting {delay_after_rotation} seconds...")
                    for _ in range(delay_after_rotation):
                        if not self.running:
                            break
                        time.sleep(1)
        
        self.rotation_thread = threading.Thread(target=rotation_worker)
        self.rotation_thread.daemon = True
        self.rotation_thread.start()
        return self.rotation_thread

    def stop_rotation(self):
        """Stop the proxy rotation"""
        self.running = False
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)
        return "Rotation stopped"

    def get_proxy_list(self):
        """Get the current list of proxies (in ip:port format)"""
        return [p.replace("http://", "") for p in self.proxies]

    def set_default_param(self, key, value):
        """
        Set a default parameter value
        
        Args:
            key (str): Parameter key
            value (str): Parameter value
        """
        if key in self.default_params:
            self.default_params[key] = value
            return f"Updated {key}"
        else:
            raise KeyError(f"Invalid parameter key: {key}")

    def set_default_header(self, key, value):
        """
        Set a default header value
        
        Args:
            key (str): Header key
            value (str): Header value
        """
        self.default_headers[key] = value
        return f"Updated {key}"

# Create a module-level instance for the simple interface
eses = ESES()