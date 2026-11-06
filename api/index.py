"""Vercel / Render Production ASGI Entry Point for SwitchGuard & CampusHire Relay."""

from __future__ import annotations
import os
import sys

# Add project root and campushire-relay to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CAMPUSHIRE_ROOT = os.path.join(PROJECT_ROOT, "campushire-relay")
if os.path.exists(CAMPUSHIRE_ROOT) and CAMPUSHIRE_ROOT not in sys.path:
    sys.path.insert(0, CAMPUSHIRE_ROOT)

from switch_agent.server import app

# Mount the CampusHire Relay application under /campushire
try:
    from campushire.server import app as campushire_app
    app.mount("/campushire", campushire_app)
except Exception as e:
    print(f"[Vercel Startup] Campushire mount deferred: {e}")

# Expose app for Vercel (@vercel/python looks for 'app')
handler = app
