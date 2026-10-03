# Mapa propuesto de puertos

Adapta los números al modelo real. Antes de conectar, etiqueta físicamente ambos extremos del cable.

## Switch 1

| Puerto | Modo | VLAN | Equipo |
|---:|---|---|---|
| 1 | Trunk | 10,20,30,40,50; nativa 999 | Router/firewall |
| 2 | Access | 20 | Host Hub/NVR o VM host A |
| 3 | Access | 10 | Respaldo/administración |
| 4 | Trunk | 30,40,50; nativa 999 | Punto de acceso VLAN |
| 5–23 | Access/disabled | Según uso | Equipos autorizados |
| 24 | Trunk | 10,20,30,40,50; nativa 999 | Switch 2 puerto 24 |

## Switch 2

| Puerto | Modo | VLAN | Equipo |
|---:|---|---|---|
| 1–8 | Access | 30 | Laptops SOC y áreas |
| 9 | Access | 40 | Lector/controlador RFID |
| 10 | Access | 10 | Estación TI |
| 11–23 | Access/disabled | Según uso | Equipos autorizados |
| 24 | Trunk | 10,20,30,40,50; nativa 999 | Switch 1 puerto 24 |

No conectes dos enlaces entre switches sin agregación configurada en ambos extremos.
