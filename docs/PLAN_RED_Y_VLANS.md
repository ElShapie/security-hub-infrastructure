# Plan de red y VLAN

## Decisión antes de conectar

Confirma los modelos exactos del router, los dos switches y el punto de acceso. Para aplicar este diseño deben soportar VLAN IEEE 802.1Q, puertos access/trunk y reglas entre redes. Dos switches no crean segmentación por sí solos.

Si alguno no es administrable, usa el escenario plano al final de esta guía. No configures etiquetas VLAN en un solo extremo: puede dejar equipos incomunicados.

## VLAN objetivo

| VLAN | Nombre | Subred | Gateway | Equipos |
|---:|---|---|---|---|
| 10 | Administración | `10.31.10.0/24` | `10.31.10.1` | TI, consola del hipervisor y respaldo |
| 20 | Servidores | `10.31.20.0/24` | `10.31.20.1` | Security Hub y NVR |
| 30 | Usuarios | `10.31.30.0/24` | `10.31.30.1` | Laptops de áreas y SOC |
| 40 | Cámaras e IoT | `10.31.40.0/24` | `10.31.40.1` | Teléfonos-cámara y lector RFID |
| 50 | Invitados | `10.31.50.0/24` | `10.31.50.1` | Equipos sin participación operativa |
| 999 | Nativa sin uso | Sin DHCP | Sin gateway | Troncales; no conectar clientes |

Direcciones reservadas:

| Equipo | Dirección |
|---|---|
| `VM-HUB-01` | `10.31.20.20` |
| `VM-NVR-01` | `10.31.20.21` |
| `VM-RESPALDO-01` | `10.31.10.22` |
| Cámara entrada | `10.31.40.31` |
| Cámara interior | `10.31.40.32` |
| Lector/controlador | `10.31.40.40` |

Usa reservas DHCP cuando sea posible. Si la red real usa estas subredes, TI debe elegir otras y actualizar todos los documentos y archivos privados.

## Reglas entre VLAN

La política inicial es denegar tráfico entre VLAN y abrir únicamente lo necesario.

| Origen | Destino | Permitir | Motivo |
|---|---|---|---|
| Administración | Servidores | HTTPS, SSH solo TI | Administración y soporte |
| Usuarios | Hub | TCP 443 | Interfaz operativa |
| SOC autorizado | NVR | TCP 8971 | Consulta de video |
| Lector RFID | Hub | TCP 443 | Decisión de acceso |
| NVR | Cámaras | Puertos RTSP/HTTP configurados | Captura de video |
| Cámaras | NVR | Respuestas establecidas | Transmisión iniciada por NVR |
| Servidores | Internet | DNS, NTP y HTTPS | OneLogin, actualizaciones y hora |
| Cámaras/IoT | Internet | Denegado, salvo necesidad comprobada | Reducir exposición |
| Invitados | Redes internas | Denegado | Aislamiento |
| Invitados | Internet | DNS, HTTP/HTTPS | Navegación básica |

No publiques SQLite, RTSP, SSH, Docker ni el puerto interno 8000. Caddy es el único punto HTTPS del Hub.

## Configuración de troncales

- Router hacia Switch 1: trunk, VLAN 10/20/30/40/50 etiquetadas, VLAN nativa 999.
- Switch 1 hacia Switch 2: un solo trunk con las mismas VLAN.
- No conectes un segundo cable entre switches salvo que ambos estén configurados para LACP; de lo contrario puede crearse un bucle.
- Puertos de clientes: access/untagged en una sola VLAN.
- Deshabilita puertos sin uso o colócalos en VLAN 999 sin DHCP.
- Activa protección contra bucles y BPDU guard si el equipo la ofrece y el equipo conoce su funcionamiento.

## Punto de acceso

El diseño completo requiere SSID separados y VLAN:

| SSID | VLAN | Uso |
|---|---:|---|
| `LAB-USUARIOS` | 30 | Laptops participantes |
| `LAB-CAMARAS` | 40 | Teléfonos usados como cámaras |
| `LAB-INVITADOS` | 50 | Equipos fuera del escenario |

Activa aislamiento de clientes en Invitados. En Cámaras, no actives aislamiento si impide que el NVR alcance los teléfonos. Usa claves distintas y no publiques la contraseña de administración del AP.

## Escenario sin VLAN

Si los switches o router son básicos:

1. Usa una sola red `10.31.0.0/24` con reservas DHCP.
2. Mantén NVR y Hub en VM separadas.
3. Aplica UFW en ambas VM y permite solo los puertos y direcciones necesarias.
4. Usa una red Wi-Fi dedicada para la práctica, sin datos personales.
5. No conectes invitados.
6. Mantén Frigate sin publicación a Internet.
7. Declara en el informe: “segmentación lógica propuesta, no aplicada por limitación del hardware”.

Este escenario reduce aislamiento y no debe presentarse como equivalente a VLAN reales.

## Verificación

Desde cada segmento comprueba la matriz:

```bash
ping -c 3 DIRECCION_GATEWAY
curl -I https://security-hub.lab/health
nc -vz 10.31.20.20 443
nc -vz 10.31.20.21 8971
```

Prueba también lo que debe fallar. Una laptop de Invitados no debe alcanzar Hub, NVR, cámaras ni administración. Guarda resultados y hora, sin capturar secretos.
