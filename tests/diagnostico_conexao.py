#!/usr/bin/env python3
"""Diagnóstico rápido de conexão com TimescaleDB"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import socket
from config.local_settings import TIMESCALE_HOST, TIMESCALE_PORT

print("=" * 60)
print("🔍 DIAGNÓSTICO DE CONEXÃO - TIMESCALE CLOUD")
print("=" * 60)
print(f"Host: {TIMESCALE_HOST}")
print(f"Porta: {TIMESCALE_PORT}")

# Teste 1: Resolução DNS
print("\n1️⃣ Testando DNS...")
try:
    ip = socket.gethostbyname(TIMESCALE_HOST)
    print(f"   ✅ Host resolvido: {TIMESCALE_HOST} -> {ip}")
except socket.gaierror as e:
    print(f"   ❌ Falha DNS: {e}")
    print("   💡 Verifique se o host está correto no Timescale Cloud Console")

# Teste 2: Porta TCP
print(f"\n2️⃣ Testando porta {TIMESCALE_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex((TIMESCALE_HOST, TIMESCALE_PORT))
if result == 0:
    print(f"   ✅ Porta {TIMESCALE_PORT} está aberta e aceitando conexões")
else:
    print(f"   ❌ Porta {TIMESCALE_PORT} não está acessível (erro: {result})")
    print("   💡 Possíveis causas:")
    print("      - Firewall bloqueando (verifique IPs permitidos no Timescale Cloud)")
    print("      - Serviço pausado (verifique Console do Timescale Cloud)")
    print("      - VPN necessária?")
sock.close()

print("\n" + "=" * 60)
