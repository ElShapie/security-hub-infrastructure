# Lista de verificación integral

## Infraestructura

- [ ] Las VM tienen hora UTC sincronizada y direcciones reservadas.
- [ ] Los switches muestran un solo trunk entre ellos.
- [ ] Los puertos access están en la VLAN prevista.
- [ ] Dirección, RR. HH., Seguridad Física y Auditoría están en VLAN 30.
- [ ] TI e IAM están en VLAN 10.
- [ ] SOC está en VLAN 60.
- [ ] Lectores y cámaras están en VLAN 40, no las laptops de Seguridad Física.
- [ ] Invitados no alcanzan redes internas.
- [ ] El Hub responde por HTTPS con certificado confiable.
- [ ] Los puertos internos 8000, SQLite, Docker y RTSP no están publicados.

## Identidad y permisos

- [ ] OneLogin exige MFA.
- [ ] SCIM entrega un `externalId` único por empleado.
- [ ] TI puede cambiar el rol desde la interfaz.
- [ ] SOC no puede cambiar roles.
- [ ] `sin_acceso` bloquea la siguiente operación.
- [ ] Una cuenta desactivada en OneLogin queda bloqueada aunque tenga rol local.

## RFID/NFC

- [ ] Seguridad Física registra una tarjeta ficticia.
- [ ] La base muestra huella, no UID completo.
- [ ] Tarjeta activa y empleado activo producen `PERMITIDO`.
- [ ] Tarjeta bloqueada produce `DENEGADO`.
- [ ] Un UID desconocido produce `DENEGADO`.
- [ ] El lector sin token válido recibe 401.

## NVR

- [ ] Cada teléfono usa credencial local exclusiva.
- [ ] Frigate recibe ambos streams.
- [ ] SOC tiene consulta y no administración.
- [ ] La retención coincide con el ejercicio.
- [ ] CPU, RAM y disco tienen margen durante la grabación.

## Recuperación

- [ ] El respaldo está cifrado y tiene SHA-256.
- [ ] Se restauró en una VM de ensayo.
- [ ] `.env`, `CARD_PEPPER` y certificados privados no están en Git.
- [ ] Se registraron resultados reales sin inventar pruebas.
