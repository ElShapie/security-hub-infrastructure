# ACL y flujos autorizados

La política es negar el movimiento lateral y abrir únicamente los servicios del laboratorio.

| Origen | Destino | Servicio | Resultado |
|---|---|---|---|
| Administración | Servidores | ICMP, HTTPS, SSH | Permitido |
| Usuarios | VM-HUB-01 | ICMP de prueba y HTTPS | Permitido |
| Usuarios | NVR, cámaras, switches | Cualquier otro | Denegado |
| SOC | VM-HUB-01 | HTTPS | Permitido |
| SOC | VM-NVR-01 | HTTPS/8971 | Permitido |
| SOC | Cámaras | ICMP/HTTP de diagnóstico | Permitido |
| RFID | VM-HUB-01 | HTTPS | Permitido |
| Cámaras/IoT | Redes de usuarios | Cualquier servicio | Denegado |
| Invitados | Redes `10.31.0.0/16` | Cualquier servicio | Denegado |
| Invitados | Nube simulada | IP | Permitido |

## Límite de la simulación

Las ACL clásicas de un router Cisco son sin estado. Las configuraciones permiten respuestas TCP con la palabra `established` y respuestas ICMP necesarias para las pruebas. En el escenario real se recomienda un firewall con seguimiento de estado y política de denegación predeterminada.

Packet Tracer no ejecuta OneLogin, Frigate ni el Security Hub real. Los servidores y puertos representan esos flujos; la comprobación completa se realiza después en las máquinas virtuales.

