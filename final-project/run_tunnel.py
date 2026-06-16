from backend.app import app
from flask_cloudflared import run_with_cloudflared

run_with_cloudflared(app)

if __name__ == '__main__':
    app.run(port=5000)
