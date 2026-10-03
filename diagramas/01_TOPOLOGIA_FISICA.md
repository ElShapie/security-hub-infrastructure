# Topología física

```mermaid
flowchart TB
    INTERNET((Internet)) --> ROUTER[Router / firewall<br/>Inter-VLAN + DHCP + ACL]
    ROUTER == "Trunk 802.1Q<br/>VLAN 10,20,30,40,50" ==> SW1[Switch administrable 1]
    SW1 == "Un solo trunk 802.1Q" ==> SW2[Switch administrable 2]

    SW1 -->|Access VLAN 20| HOST1[Host de virtualización A]
    HOST1 --> HUB[VM-HUB-01]
    HOST1 --> NVR[VM-NVR-01]
    SW1 -->|Access VLAN 10| BACKUP[VM-RESPALDO-01]
    SW1 -->|Trunk al AP| AP[Punto de acceso<br/>SSID por VLAN]

    AP -->|SSID LAB-CAMARAS / VLAN 40| CAM1[Teléfono cámara 1]
    AP -->|SSID LAB-CAMARAS / VLAN 40| CAM2[Teléfono cámara 2]
    AP -->|SSID LAB-USUARIOS / VLAN 30| LAPW[Laptops Wi-Fi]

    SW2 -->|Access VLAN 30| SOC[Laptops SOC / áreas]
    SW2 -->|Access VLAN 40| RFID[Laptop o controlador RFID]
    SW2 -->|Access VLAN 10| TI[Estación TI]
```

Usa un solo enlace entre switches. Si Hub y NVR están en hosts físicos distintos, conecta cada host a un puerto access VLAN 20. Si el hipervisor transporta varias VLAN, su puerto debe ser trunk y esa configuración debe documentarse por separado.
