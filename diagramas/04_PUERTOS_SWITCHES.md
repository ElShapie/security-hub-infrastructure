# Mapa propuesto de puertos

Adapta los números al modelo real. Antes de conectar, etiqueta físicamente ambos extremos del cable.

## Switch principal (`SW-CORE-01`)

| Puerto | Modo | VLAN | Equipo |
|---:|---|---|---|
| Gi0/1 | Trunk | 10,20,30,40,50,60; nativa 999 | Router/firewall |
| Gi0/2 | Trunk | 10,20,30,40,50,60; nativa 999 | `SW-ACCESS-01` Gi0/1 |
| Fa0/1–3 | Access | 20 | Infraestructura, Hub y NVR |
| Fa0/4 | Access | 10 | Respaldo/administración |
| Fa0/5 | Trunk | 30,40,50,60; nativa 999 | Punto de acceso VLAN |
| Fa0/6–12 | Access | 10 | TI |
| Fa0/13–18 | Access | 10 | IAM |
| Fa0/19–23 | Access | 60 | SOC |
| Fa0/24 | Disabled | 999 | Reserva apagada |

## Switch de acceso (`SW-ACCESS-01`)

| Puerto | Modo | VLAN | Equipo |
|---:|---|---|---|
| Gi0/1 | Trunk | 10,20,30,40,50,60; nativa 999 | `SW-CORE-01` Gi0/2 |
| Fa0/1–3 | Access | 30 | Dirección |
| Fa0/4–7 | Access | 30 | RRHH |
| Fa0/8–13 | Access | 30 | Seguridad Física |
| Fa0/14–16 | Access | 30 | Auditoría |
| Fa0/17–18 | Disabled | 999 | Reserva apagada |
| Fa0/19 | Access | 40 | Lector/controlador RFID |
| Fa0/20–24 | Disabled | 999 | Reserva apagada |

No conectes dos enlaces entre switches sin agregación configurada en ambos extremos.

La tabla de rosetas, patch panel y etiquetas se consulta en la [topología interactiva](../packet-tracer/topologia-interactiva/index.html). Los puestos con más de un rol usan una sola conexión física y cambian permisos en OneLogin y el Hub; no se les crea un segundo cable por tener dos responsabilidades.
