# Diligencias de infraestructura por área

La infraestructura se coordina con las guías sanitizadas del proyecto. Los nombres no se escriben en este repositorio; se usan identificadores `EMP`.

- `EMP-010` coordina TI, cambios de red y máquinas virtuales.
- `EMP-001` entrega plano de cableado estructurado, etiquetas, tabla switch-puerto-VLAN y pruebas.
- `EMP-009` configura enlaces, VLAN y conectividad.
- `EMP-008` revisa topología y pruebas permitidas/denegadas.
- `EMP-011` opera VM-HUB, HTTPS, respaldos y recuperación.
- `EMP-013` realiza soporte y reúne evidencia técnica.
- `EMP-024`, `EMP-026`, `EMP-027`, `EMP-028`, `EMP-032` y `EMP-033` implementan RFID, cámaras, NVR y correlación con SOC.
- `EMP-019` a `EMP-023` validan monitoreo y respuesta.
- `EMP-014` a `EMP-018`, junto con `EMP-012`, validan identidades, OneLogin, Microsoft 365 y permisos.

Cada cambio debe incluir: solicitante EMP, aprobador EMP, equipo, puerto/VLAN, fecha, resultado esperado, prueba ejecutada, evidencia y reversión. No incluir contraseñas, tokens, UID completos, datos reales ni archivos de entorno.

Las áreas se ubican así: Dirección, RRHH y Auditoría en VLAN 30; TI e IAM administran desde VLAN 10; servidores en VLAN 20; cámaras y lector en VLAN 40; invitados en VLAN 50; SOC en VLAN 60; VLAN 999 queda nativa sin uso.
