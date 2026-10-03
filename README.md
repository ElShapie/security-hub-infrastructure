# Security Hub Infrastructure

Repositorio privado para desplegar la infraestructura operativa del laboratorio. Contiene el Security Hub, NVR Frigate, integración RFID/NFC, máquinas virtuales, red y VLAN. Está separado del dashboard DPO y no comparte su base de datos.

## Orden de implementación

1. Leer [arquitectura y requisitos](docs/SERVIDORES_OPERATIVOS.md).
2. Confirmar si router, switches y punto de acceso admiten VLAN 802.1Q.
3. Aplicar el [plan de red y VLAN](docs/PLAN_RED_Y_VLANS.md).
4. Seguir [levantamiento de máquinas](docs/LEVANTAR_MAQUINAS_PASO_A_PASO.md).
5. Configurar OneLogin, SCIM y los roles del Hub.
6. Configurar Frigate y los teléfonos.
7. Conectar RFID/NFC y validar una tarjeta ficticia.
8. Seguir la [guía de la interfaz](docs/GUIA_INTERFAZ_SECURITY_HUB.md).
9. Ejecutar la [lista de verificación](docs/PRUEBA_INTEGRAL.md).

## Componentes

| Carpeta | Contenido |
|---|---|
| `hub/` | Aplicación Flask, Caddy HTTPS, SQLite, OIDC, SCIM y RBAC |
| `nvr/` | Frigate y configuración de cámaras de ejemplo |
| `rfid/` | Lector, registro local y envío de eventos al Hub |
| `diagramas/` | Topología física, VLAN y flujos, editables en Mermaid |
| `docs/` | Instalación, operación, direccionamiento, ACL y pruebas |
| `scripts/` | Preparación segura del runtime fuera del repositorio |

## Preparar una copia operativa

```bash
python3 scripts/preparar_runtime.py --destino "$HOME/security-hub-runtime"
```

Los secretos se generan en el runtime. Este repositorio no debe contener `.env`, bases de datos, UID reales, correos reales, grabaciones, certificados privados ni nombres de la institución.

## Diagramas

- [Topología física](diagramas/01_TOPOLOGIA_FISICA.md)
- [Segmentación VLAN](diagramas/02_VLANS_Y_SUBREDES.md)
- [Flujos permitidos](diagramas/03_FLUJOS_DE_SEGURIDAD.md)
- [Puertos de los switches](diagramas/04_PUERTOS_SWITCHES.md)

Los diagramas muestran el diseño objetivo con equipos administrables. Si el hardware no soporta VLAN, usa el escenario alternativo documentado y declara esa limitación en la presentación.
