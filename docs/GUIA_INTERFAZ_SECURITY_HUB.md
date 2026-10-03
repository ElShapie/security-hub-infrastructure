# Guía de la interfaz gráfica del Security Hub

## Cómo se aplican los permisos

Sí, los permisos funcionan por usuario. Cada persona tiene cuatro datos relacionados:

1. OneLogin autentica su correo y MFA.
2. SCIM crea o actualiza su cuenta en el Hub.
3. `externalId` representa el número único de empleado, por ejemplo `LAB-021`.
4. El Hub calcula un rol efectivo y revisa ese rol en el servidor antes de cada operación.

Ocultar un botón no constituye seguridad. Aunque alguien construya una petición manual, el servidor vuelve a comprobar el permiso. Un cambio hecho por TI se aplica inmediatamente a las siguientes consultas y escrituras de una sesión abierta.

## Roles disponibles

| Rol | Funciones permitidas |
|---|---|
| `admin` | Todas las funciones del Hub |
| `ti` | Cambiar roles, registrar tarjetas, administrar infraestructura, mantenimiento y registros |
| `seguridad_fisica` | Registrar, vincular, activar y bloquear tarjetas; consultar accesos |
| `soc` | Consultar eventos y abrir incidentes |
| `auditor` | Consultar estado, eventos y Hub SOC sin modificar operación |
| `mantenimiento` | Consultar y ejecutar mantenimiento controlado |
| `consulta` | Ver el resumen sin administrar |
| `sin_acceso` | No puede abrir la consola |

`active=false` siempre bloquea al empleado. Un rol local no puede reactivar una identidad deshabilitada en OneLogin.

## Pantalla de acceso

La URL inicial muestra “Continuar con OneLogin”. No existen contraseñas locales del Hub. OneLogin autentica y devuelve la identidad; el Hub acepta el acceso solo si esa cuenta ya fue aprovisionada mediante SCIM y está activa.

## Resumen

La pantalla principal muestra:

- Identidades activas.
- Servicios disponibles frente al total.
- Accesos físicos denegados durante el día.
- Incidentes abiertos.
- Inventario de servidores, lectores, cámaras, NVR y red.
- Últimos eventos RFID/NFC.
- Incidentes recientes.

TI y Administración ven el formulario “Registrar servicio”. SOC y Administración ven el formulario “Abrir incidente”. La API vuelve a validar el rol aunque el formulario no aparezca.

## Cambiar permisos por número de empleado

Solo `admin` y `ti` pueden hacerlo:

1. Abre “Personas y tarjetas”.
2. Localiza el número de empleado. Si aparece `SIN-NÚMERO`, corrige el atributo `externalId` en OneLogin antes de continuar.
3. Revisa que la cuenta y el estado correspondan a la solicitud autorizada.
4. Selecciona el nuevo rol en “Rol efectivo”.
5. Pulsa “Aplicar”.
6. Pide al empleado que actualice la página y pruebe únicamente su función.
7. Revisa la bitácora para confirmar quién realizó el cambio.

El cambio se almacena como una excepción local separada del rol inicial enviado por SCIM. Esto evita que una sincronización ordinaria de OneLogin revierta accidentalmente el permiso decidido por TI. La baja o desactivación de OneLogin conserva prioridad y bloquea el acceso.

Para retirar todo acceso, selecciona `sin_acceso`. Para una baja definitiva, RR. HH. solicita la desactivación en OneLogin; SCIM desactiva la cuenta y las tarjetas dejan de autorizarse.

## Registrar una tarjeta RFID/NFC

Los roles `admin`, `ti` y `seguridad_fisica` pueden hacerlo:

1. Abre “Personas y tarjetas”.
2. Coloca la tarjeta en el lector de registro y copia el UID entregado por la herramienta local.
3. Escribe el UID en “UID leído por el dispositivo”.
4. Asigna una etiqueta genérica, por ejemplo `TARJETA-021`. No escribas el nombre de la persona.
5. Selecciona el número de empleado activo.
6. Pulsa “Registrar y vincular”.
7. Comprueba que aparece una huella de 12 caracteres, no el UID completo.
8. Presenta la tarjeta ante el lector de puerta y revisa el evento en el resumen o SOC.

El servidor normaliza el UID y calcula HMAC-SHA-256 con `CARD_PEPPER`. La base de datos almacena esa huella, no el UID. Cambiar o perder `CARD_PEPPER` impide reconocer todas las tarjetas existentes; debe incluirse en el respaldo privado de configuración.

Una tarjeta no autoriza por sí sola. Para permitir acceso deben cumplirse las tres condiciones:

- La tarjeta está registrada y activa.
- El empleado vinculado está activo.
- El lector consulta al Hub usando el token de dispositivos correcto.

## Bloquear o reactivar una tarjeta

1. Busca la etiqueta o huella en “Tarjetas vinculadas”.
2. Pulsa “Bloquear”.
3. Comprueba que el estado cambia a `bloqueada`.
4. Vuelve a presentar la tarjeta; el evento debe ser `DENEGADO`.
5. Si la tarjeta vuelve a estar bajo control autorizado, pulsa “Activar”.

No elimines registros para simular una baja. Bloquear conserva la trazabilidad. Cuando SCIM elimina una identidad, el Hub bloquea sus tarjetas antes de retirar el usuario.

## Funcionamiento del lector

El endpoint recomendado es:

```text
POST /api/v1/access/check
Authorization: Bearer DEVICE_TOKEN
Content-Type: application/json
```

Ejemplo de cuerpo ficticio:

```json
{
  "uid": "A1B2C3D4",
  "reader": "PUERTA-PRINCIPAL",
  "movement": "ENTRADA"
}
```

El Hub responde con `allowed`, el número de empleado cuando corresponde, el motivo y el identificador del evento. El lector abre la puerta simulada únicamente si `allowed` es `true`. Nunca debe decidir basándose solo en un UID guardado en el navegador.

## Flujo de alta recomendado

1. RR. HH. crea la solicitud con el número de empleado y área.
2. Dirección o el responsable aprueba.
3. IAM crea la identidad en OneLogin y exige MFA.
4. SCIM envía `userName`, `externalId`, `title` y `active`.
5. TI verifica el número y asigna el rol efectivo.
6. Seguridad Física vincula la tarjeta si el puesto la necesita.
7. El empleado prueba OneLogin, la función asignada y el acceso físico.
8. Auditoría conserva únicamente evidencias saneadas.

## Flujo de baja recomendado

1. RR. HH. registra la baja autorizada.
2. IAM desactiva la identidad en OneLogin.
3. SCIM envía `active=false` o elimina la cuenta.
4. El Hub deniega la sesión y las tarjetas vinculadas.
5. Seguridad Física recupera y bloquea la tarjeta.
6. SOC revisa intentos posteriores a la baja.
7. Auditoría verifica la trazabilidad.

## Errores comunes

| Síntoma | Revisión |
|---|---|
| El empleado no aparece | Revisar asignación y aprovisionamiento SCIM en OneLogin |
| Aparece `SIN-NÚMERO` | Mapear `externalId` y sincronizar otra vez |
| El cambio de rol devuelve 403 | La cuenta operadora no tiene rol `ti` o `admin` |
| La tarjeta duplicada devuelve 400 | Ese UID ya está registrado; buscar su huella y bloquear o reasignar mediante el procedimiento autorizado |
| La tarjeta válida se deniega | Revisar tarjeta activa, empleado activo, `CARD_PEPPER` y hora del servidor |
| El lector recibe 401 | `DEVICE_TOKEN` no coincide o no se envió como Bearer |
| OneLogin entra y vuelve 403 | Usuario no aprovisionado, inactivo, sin rol o sujeto OIDC no coincidente |

## Auditoría y datos

Los cambios de rol, vínculos de tarjeta, bloqueos e intentos denegados generan eventos con hora UTC y actor. No incluyas nombres en las etiquetas. El número de empleado es el identificador operativo común entre IAM, RFID y SOC. Las grabaciones siguen en Frigate y los registros de cumplimiento siguen en el dashboard DPO; no deben copiarse automáticamente al Hub.
