import ipaddress
import json

with open("geoip_data.json") as f:
    geoip_data = json.load(f)

geoip_networks = [
    {
        "network": ipaddress.ip_network(entry["prefix"]),
        **entry
    } for entry in geoip_data
]

def lookup_ip(ip_address: str):
    ip = ipaddress.ip_address(ip_address)
    for entry in geoip_networks:
        if ip in entry["network"]:
            return {
                "ip": ip_address,
                "matched_prefix": entry["prefix"],
                "country": entry["country"],
                "region": entry["region"],
                "city": entry["city"],
                "service": entry["service"]
            }
    return None
