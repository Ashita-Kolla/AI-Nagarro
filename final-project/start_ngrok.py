import time
from pyngrok import ngrok

# Open a HTTP tunnel on the default port 80
# <NgrokTunnel: "https://<public_sub>.ngrok.io" -> "http://localhost:80">
http_tunnel = ngrok.connect(5000, bind_tls=True)

print(f"NGROK_URL: {http_tunnel.public_url}")

# Keep the script running
while True:
    time.sleep(1)
