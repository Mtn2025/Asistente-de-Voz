# Asistente de Voz AI

Sistema de asistente de voz con arquitectura hexagonal, integración con LLMs, STT/TTS y telefonía.

## 🚀 Quick Start

### Local Development (Docker Compose)

1. **Clonar repositorio:**
```bash
git clone https://github.com/Mtn2025/Asistente-de-Voz.git
cd Asistente-de-Voz
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus API keys
```

3. **Iniciar servicios:**
```bash
docker-compose up -d
```

4. **Verificar health:**
```bash
curl http://localhost:8000/api/system/health
```

5. **Ver logs:**
```bash
docker-compose logs -f app
```

### Deployment a Coolify

1. **Conectar repositorio en Coolify**
   - New Resource → Application
   - Source: GitHub
   - Repository: Mtn2025/Asistente-de-Voz
   - Branch: main

2. **Configurar ENV variables** (ver `.env.example`)

3. **Deploy**

## 📋 Variables de Entorno Requeridas

Ver archivo `.env.example` para lista completa.

**Críticas:**
- `POSTGRES_*`: Database credentials
- `REDIS_URL`: Redis connection
- `GROQ_API_KEY`: LLM service
- `AZURE_SPEECH_KEY`: STT/TTS service

**Opcionales:**
- `ELEVENLABS_API_KEY`: TTS alternativo
- `TWILIO_*`: Telefonía Twilio
- `TELNYX_*`: Telefonía Telnyx

## 🏗️ Arquitectura
```
app-nuevo/
├── domain/              # Lógica de negocio pura
├── application/         # Casos de uso y servicios
├── infrastructure/      # Adapters externos
└── interfaces/          # HTTP/WebSocket endpoints
```

Arquitectura Hexagonal (Ports & Adapters)

## 🔧 Desarrollo

### Requisitos
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### Instalación local (sin Docker)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Configurar .env
cp .env.example .env

# Iniciar
python main.py
```

## 📚 Documentación

- [Database Setup](DATABASE.md)
- API Docs: `http://localhost:8000/docs`

## 🐛 Troubleshooting

### Database connection failed
- Verificar que PostgreSQL está corriendo
- Verificar credenciales en `.env`

### Import errors
- Verificar que estás en el virtual environment
- `pip install -r requirements.txt`

### Port already in use
- Cambiar `PORT` en `.env`
- O detener servicio en ese puerto

## 📝 License

[Tu licencia aquí]
