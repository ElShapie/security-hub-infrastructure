# Mapa propuesto de puertos

Adapta los números al modelo real. Antes de conectar, etiqueta físicamente ambos extremos del cable.

## Switch 1

| Puerto | Modo | VLAN | Equipo |
|---:|---|---|---|
| 1 | Trunk | 10,20,30,40,50,60; nativa 999 | Router/firewall |
| 2 | Access | 20 | Host Hub/NVR o VM host A |
| 3 | Access | 10 | Respaldo/administración |
| 4 | Trunk | 30,40,50,60; nativa 999 | Punto de acceso VLAN |
| 5–23 | Access/disabled | Según uso | Equipos autorizados |
| 24 | Trunk | 10,20,30,40,50,60; nativa 999 | Switch 2 puerto 24 |

## Switch 2

| Puerto | Modo | VLAN | Equipo |
|---:|---|---|---|
| 1–6 | Access | 30 | Dirección, RR. HH., Seguridad Física y Auditoría |
| 7–11 | Access | 60 | Laptops SOC |
| 12 | Access | 40 | Lector/controlador RFID |
| 13–14 | Access | 10 | Estaciones TI e IAM |
| 15–23 | Access/disabled | Según uso | Equipos autorizados |
| 24 | Trunk | 10,20,30,40,50,60; nativa 999 | Switch 1 puerto 24 |

No conectes dos enlaces entre switches sin agregación configurada en ambos extremos.
