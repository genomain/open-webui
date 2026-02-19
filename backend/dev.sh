export CORS_ALLOW_ORIGIN="http://localhost:5173;http://localhost:8080"
export GENOMAIN_KLARTEXT_BASEURL=""
export GENOMAIN_KLARTEXT_API_KEY=""
export WEBUI_JWT_SECRET_KEY=""
export WEBUI_SECRET_KEY=""
PORT="${PORT:-8080}"
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
