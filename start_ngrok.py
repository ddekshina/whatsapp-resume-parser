import ngrok
import os
from dotenv import load_dotenv

load_dotenv()

# Set up ngrok
authtoken = os.getenv('NGROK_AUTHTOKEN')
listener = ngrok.forward(5000, authtoken=authtoken)

print(f"🌐 Public URL: {listener.url()}")
print(f"📱 Use this URL for WhatsApp webhook: {listener.url()}/webhook")
print("Press Ctrl+C to stop...")

try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping ngrok...")
