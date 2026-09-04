# Sistema Automatizado de Control Financiero

> Pipeline ETL automatizado para la extracción, procesamiento, almacenamiento y visualización de movimientos financieros personales a partir de notificaciones bancarias por correo electrónico.

<img width="1365" height="425" alt="image" src="https://github.com/user-attachments/assets/042f28ea-9ca3-40af-88ee-56dbf88c99e1" />
<img width="1365" height="597" alt="image" src="https://github.com/user-attachments/assets/1db63339-d83c-4a6a-8245-7626181cbf76" />
<img width="1365" height="598" alt="image" src="https://github.com/user-attachments/assets/8430ad42-2433-4a74-88cb-c6a8d3d52a97" />


## Descripción del proyecto

Solución de ingeniería de datos y desarrollo backend orientada a automatizar y centralizar el control de gastos e ingresos personales a partir de notificaciones bancarias.

La aplicación elimina la captura manual de datos mediante un pipeline que se ejecuta diariamente en la nube, procesa el texto de los correos electrónicos con expresiones regulares optimizadas y almacena la información estructurada para su análisis en tiempo real.

## Arquitectura y stack tecnológico

| Capa | Tecnologías |
|---|---|
| Extracción y backend | Python, Gmail API / IMAP, expresiones regulares (`re`) |
| Base de datos | PostgreSQL / Supabase, SQL |
| Automatización (CI/CD) | GitHub Actions (ejecución programada vía cron) |
| Visualización (frontend) | Streamlit, Plotly, Pandas |
| Despliegue | Streamlit Community Cloud, GitHub Actions |

## Flujo del sistema (Pipeline ETL)

1. **Extraction** — Conexión segura vía Gmail API/IMAP para recuperar las notificaciones de transacciones recientes.
2. **Transformation** — Limpieza, normalización de formatos monetarios (COP) y parseo con regex adaptado por banco (Nequi, Bancolombia, Banco de Bogotá, Nu).
3. **Load** — Persistencia de los movimientos en Supabase, con prevención de duplicados.
4. **Visualization** — Dashboard interactivo en Streamlit con métricas, filtros dinámicos y categorización manual de comercios.

## Características principales

- Automatización total: ejecución diaria en la nube vía GitHub Actions, sin intervención manual.
- Multi-canal y multi-banco: parsers independientes por entidad financiera colombiana.
- Categorización inteligente y manual, con categorías personalizadas persistentes.
- Prevención de duplicados antes de insertar cada movimiento.
- Interfaz limpia, inspirada en estándares tipo Notion/Fintech, totalmente responsive.

## Estructura del repositorio

```
gastos-automatizados/
├── app/
│   └── streamlit_app.py           # Dashboard principal
├── data/
│   └── categorias_personalizadas.json
├── logs/                          # Logs de ejecución del pipeline
├── reports/                       # Reportes generados
├── src/
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base.py                # Clase base de los parsers
│   │   ├── nequi.py
│   │   ├── bancolombia.py
│   │   ├── banco_de_bogota.py
│   │   └── nu.py
│   ├── categorizador.py           # Lógica de categorización
│   ├── cuentas.py                 # Manejo de cuentas
│   ├── db.py                      # Conexión y carga a Supabase
│   ├── gmail_client.py            # Cliente Gmail API
│   └── main.py                    # Orquestador del pipeline
├── .github/workflows/
│   └── etl_cron.yml               # Automatización diaria
├── .env                           # Variables de entorno 
├── credentials.json               # Credenciales OAuth de Gmail 
├── requirements.txt
└── README.md
```

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Laura-Montana/gastos-automatizados.git
cd gastos-automatizados
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar el acceso a Gmail

El proyecto necesita acceso a la bandeja de entrada para leer las notificaciones bancarias. Hay dos piezas de configuración:

- **Gmail API (OAuth):** crear un proyecto en Google Cloud Console, habilitar la Gmail API, generar credenciales OAuth y descargar el archivo `credentials.json` en la raíz del proyecto. Mientras la app esté en modo de prueba, agregar tu correo como usuario de prueba en la pantalla de consentimiento OAuth.
- **Acceso IMAP:** habilitar IMAP en la configuración de Gmail y generar una contraseña de aplicación (requiere verificación en dos pasos activada) para usarla como `GMAIL_APP_PASSWORD`.

### 4. Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
GMAIL_USER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=tu_contraseña_de_aplicacion
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_anon_de_supabase
```

### 5. Ejecutar localmente

```bash
python src/main.py          # Corre el pipeline ETL una vez
streamlit run app/streamlit_app.py   # Levanta el dashboard
```

### 6. Automatización en la nube (opcional)

Para que el pipeline corra solo, sin depender de tu máquina local:

- **GitHub Actions:** el archivo `.github/workflows/extraccion_diaria.yml` define la ejecución programada (cron) del pipeline y debe tener configurados los mismos secretos del `.env` como *repository secrets*.
- **Streamlit Cloud:** conectar el repositorio a [Streamlit Community Cloud](https://streamlit.io/cloud) para desplegar el dashboard, configurando allí las mismas variables de entorno.

## Roadmap

- Soporte para más entidades bancarias colombianas
- Categorización automática con Machine Learning
- Notificaciones de gastos inusuales
- Exportación de reportes en PDF/Excel

## Autor

Laura — Estudiante de ingeniería de sistemas, Universidad Libre (Bogotá, Colombia)
