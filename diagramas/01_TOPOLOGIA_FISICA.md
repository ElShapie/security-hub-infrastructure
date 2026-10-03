# Topología física

```mermaid
flowchart TB
    INTERNET((Internet)) --> ROUTER[Router / firewall<br/>Inter-VLAN + DHCP + ACL]
    ROUTER == "Trunk 802.1Q<br/>VLAN 10,20,30,40,50,60" ==> SW1[Switch administrable 1]
    SW1 == "Un solo trunk 802.1Q" ==> SW2[Switch administrable 2]

    SW1 -->|Access VLAN 20| HOST1[Host de virtualización A]
    HOST1 --> HUB[VM-HUB-01]
    HOST1 --> NVR[VM-NVR-01]
    SW1 -->|Access VLAN 10| BACKUP[VM-RESPALDO-01]
    SW1 -->|Trunk al AP| AP[Punto de acceso<br/>SSID por VLAN]

    AP -->|SSID LAB-CAMARAS / VLAN 40| CAM1[Teléfono cámara 1]
    AP -->|SSID LAB-CAMARAS / VLAN 40| CAM2[Teléfono cámara 2]
    AP -->|SSID LAB-USUARIOS / VLAN 30| LAPW[Dirección, RR. HH.<br/>Seguridad Física y Auditoría]
    AP -->|SSID LAB-SOC / VLAN 60| SOCW[SOC por Wi-Fi]

    SW2 -->|Access VLAN 30| AREAS[Dirección / RR. HH.<br/>Seguridad Física / Auditoría]
    SW2 -->|Access VLAN 60| SOC[Laptops SOC]
    SW2 -->|Access VLAN 40| RFID[Controlador RFID/NFC]
    SW2 -->|Access VLAN 10| TI[TI e IAM]
```

Usa un solo enlace entre switches. Si Hub y NVR están en hosts físicos distintos, conecta cada host a un puerto access VLAN 20. Si el hipervisor transporta varias VLAN, su puerto debe ser trunk y esa configuración debe documentarse por separado.
