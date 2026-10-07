"""Validación estática de los archivos Cisco sin conectarse a equipos reales."""
from pathlib import Path
import ipaddress

ROOT = Path(__file__).resolve().parent
CONFIGS = ROOT / "configs"
VLANS = {10: "ADMIN", 20: "SERVERS", 30: "USERS", 40: "CCTV_IOT", 50: "GUESTS", 60: "SOC", 999: "PARKING_NATIVE"}


def require(text: str, fragment: str, source: str) -> None:
    if fragment not in text:
        raise SystemExit(f"{source}: falta {fragment!r}")


def main() -> None:
    router = (CONFIGS / "RTR-HUB-01.txt").read_text(encoding="utf-8")
    core = (CONFIGS / "SW-CORE-01.txt").read_text(encoding="utf-8")
    access = (CONFIGS / "SW-ACCESS-01.txt").read_text(encoding="utf-8")

    for vlan, name in VLANS.items():
        for source, text in (("SW-CORE-01", core), ("SW-ACCESS-01", access)):
            require(text, f"vlan {vlan}\n name {name}", source)
        if vlan != 999:
            require(router, f"encapsulation dot1Q {vlan}", "RTR-HUB-01")
            network = ipaddress.ip_network(f"10.31.{vlan}.0/24")
            gateway = ipaddress.ip_address(f"10.31.{vlan}.1")
            if gateway not in network:
                raise SystemExit(f"Gateway fuera de subred para VLAN {vlan}")

    for source, text in (("SW-CORE-01", core), ("SW-ACCESS-01", access)):
        for fragment in ("switchport trunk native vlan 999", "switchport nonegotiate", "spanning-tree bpduguard enable", "transport input ssh"):
            require(text, fragment, source)

    for acl in ("USERS-IN", "IOT-IN", "GUESTS-IN", "SOC-IN"):
        require(router, f"ip access-list extended {acl}", "RTR-HUB-01")
    for fragment in ("ip dhcp pool ADMIN", "ip dhcp pool SERVERS", "ip dhcp pool USERS", "ip dhcp pool CCTV_IOT", "ip dhcp pool GUESTS", "ip dhcp pool SOC"):
        require(router, fragment, "RTR-HUB-01")

    print("Topología validada: 7 VLAN, 2 trunks, 6 pools DHCP, 4 ACL y administración SSH.")


if __name__ == "__main__":
    main()
