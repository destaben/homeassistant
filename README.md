# Home Assistant - Disaster Recovery Backup

Configuración completa de Home Assistant para restauración ante desastre total.

## 📋 Contenido del Repositorio

### Archivos principales

- **`docker-compose.yaml`** - Definición de servicios (Home Assistant, Nginx, Cloudflared, Zigbee2MQTT, Mosquitto)
- **`nginx.conf`** - Configuración del proxy reverso con filtrado de endpoints
- **`cloudflared/config.yml`** - Configuración del túnel Cloudflare
- **`.env.example`** - Template de variables de entorno
- **`.gitignore`** - Archivos a ignorar (secrets, bases de datos, logs)

### Directorio `homeassistant/`

**Configuración (restaurable):**
- `configuration.yaml` - Configuración base
- `automations.yaml` - Automaciones personalizadas
- `scripts.yaml` - Scripts personalizados
- `scenes.yaml` - Escenas
- `ui-lovelace.yaml` - Dashboard personalizado
- `blueprints/` - Blueprints personalizados
- `custom_components/` - Componentes instalados
- `www/` - Archivos estáticos personalizados

**NO incluido (se genera automáticamente):**
- Bases de datos (`*.db`, `*.db-wal`, `*.db-shm`)
- Logs (`home-assistant.log*`)
- Caché y archivos de sistema (`.storage/`, `.cloud/`, `deps/`)
- Archivos generados (`media/`, `tts/`, `backups/`)

### Directorio `mosquitto_config/`

- `mosquitto.conf` - Configuración de MQTT
- `mosquitto_certs.sh` - Script para generar certificados

## 🚀 Restauración desde cero

### 1. Clonar el repositorio
```bash
git clone https://github.com/destaben/homeassistant.git
cd homeassistant
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Edita .env y agrega tu CLOUDFLARE_TUNNEL_TOKEN
```

### 3. Configurar secretos (si los hay)
```bash
cp homeassistant/secrets.yaml.example homeassistant/secrets.yaml
# Edita y agrega tus credenciales
```

### 4. Actualizar configuración de Cloudflare
Edita `cloudflared/config.yml` y reemplaza `homeassistant.tu-dominio.com` con tu dominio

### 5. Construir e iniciar los contenedores
```bash
docker-compose up -d
```

### 6. Restaurar datos adicionales (si existen)
Si tienes backups de Home Assistant, restaura desde la interfaz:
1. Abre `http://localhost:8123`
2. Configuración → Sistema → Backups → Restaurar

## 📁 Estructura de directorios esperada

```
/home/bmax/homeassistant/
├── docker-compose.yaml
├── nginx.conf
├── .env
├── .env.example
├── .gitignore
├── cloudflared/
│   └── config.yml
├── homeassistant/
│   ├── configuration.yaml
│   ├── automations.yaml
│   ├── scripts.yaml
│   ├── scenes.yaml
│   ├── secrets.yaml (⚠️ no versionado)
│   ├── ui-lovelace.yaml
│   ├── blueprints/
│   ├── custom_components/
│   └── www/
├── mosquitto_config/
│   ├── mosquitto.conf
│   └── mosquitto_certs.sh
└── README.md (este archivo)
```

## 🔐 Seguridad

⚠️ **Importante:**
- Nunca subas `secrets.yaml` al repositorio
- Nunca subas `homeassistant/secrets.yaml`
- Usa variables de entorno para credenciales
- El repositorio debe ser **privado**

## 📝 Notas

- Las bases de datos de Home Assistant se crearán automáticamente en la primera ejecución
- Los certificados de Mosquitto se generarán automáticamente si no existen
- Si usas Zigbee2MQTT, la configuración está en `docker-compose.yaml`
- El proxy Nginx filtra automáticamente para exponer solo endpoints públicos necesarios

## 🔄 Actualizaciones

Después de cualquier cambio en la configuración:

```bash
git add .
git commit -m "Descripción del cambio"
git push
```

Solo se sincronizarán archivos de configuración. Los datos generados se ignoran automáticamente.

## ❓ Preguntas frecuentes

**P: ¿Por qué no se incluyen los backups?**
R: Los backups son grandes e innecesarios. Están protegidos dentro de Home Assistant.

**P: ¿Se restaurarán automáticamente mis dispositivos conectados?**
R: No. Algunos requerirán reconexión (Zigbee, Z-Wave, etc.). Los secrets y credenciales son necesarios.

**P: ¿Puedo usar esto en otra máquina?**
R: Sí, solo cambia:
- IP en `nginx.conf` (si es diferente)
- Variables en `.env`
- Dominio en `cloudflared/config.yml`
