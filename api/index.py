import sys
import os

# Tambahkan root project ke path agar package 'app' bisa diimport
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Vercel mencari variabel bernama 'app'
app = create_app()
