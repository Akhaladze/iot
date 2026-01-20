import requests
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MikroTikService:
    def __init__(self, ip, user, password):
        self.base_url = f"https://{ip}/rest"
        self.auth = (user, password)

    def _get(self, endpoint):
        """Helper to perform GET request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, auth=self.auth, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_dhcp_leases(self):
        """Fetch all entries from DHCP Server Lease via REST API"""
        return self._get("ip/dhcp-server/lease")

    def get_kid_control_devices(self):
        """Fetch Kid Control managed devices"""
        return self._get("ip/kid-control/device")

    def get_active_services(self):
        """Fetch active IP services (api, ftp, ssh, etc.)"""
        return self._get("ip/service")

    def get_wireless_registrations(self):
        """Fetch connected wireless clients"""
        return self._get("interface/wireless/registration-table")

    def get_arp_table(self):
        """Fetch ARP table entries"""
        return self._get("ip/arp")

    def get_firewall_rules(self):
        """Fetch Firewall Filter, NAT, Mangle rules and active Connections"""
        return {
            "filter": self._get("ip/firewall/filter"),
            "nat": self._get("ip/firewall/nat"),
            "mangle": self._get("ip/firewall/mangle"),
            "connections": self._get("ip/firewall/connection")
        }