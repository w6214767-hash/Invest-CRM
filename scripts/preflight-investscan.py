"""Read-only VPS inventory before an InvestScan release. No secret values are output."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import urllib.request


def command(args):
    try:
        run = subprocess.run(args, capture_output=True, text=True, timeout=10, check=False)
        return run.stdout if run.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def inspect():
    result = {'uid': os.getuid(), 'external_writes': 0}
    usage = shutil.disk_usage('/')
    result['disk_free_bytes'] = usage.free
    memory = Path('/proc/meminfo')
    result['memory_available_kib'] = None
    if memory.is_file():
        for line in memory.read_text().splitlines():
            if line.startswith('MemAvailable:'):
                result['memory_available_kib'] = int(line.split()[1])
    result['docker_available'] = command(['docker', 'info', '--format', '{{.ServerVersion}}']) is not None
    # Only names/images/status/ports; never docker inspect's environment section.
    containers = command(['docker', 'ps', '--format', '{{json .}}'])
    result['containers'] = None if containers is None else [
        {key: value.get(key) for key in ('Names', 'Image', 'Status', 'Ports')}
        for value in (json.loads(line) for line in containers.splitlines() if line)
    ]
    probe = socket.socket()
    probe.settimeout(2)
    result['port_8093_accepts_connections'] = probe.connect_ex(('127.0.0.1', 8093)) == 0
    probe.close()
    try:
        addresses = sorted({entry[4][0] for entry in socket.getaddrinfo('invest.ugsdom.ru', 443)})
        result['invest_dns'] = addresses
        result['dns_points_to_vps2'] = '72.56.242.5' in addresses
    except OSError:
        result['invest_dns'] = None
        result['dns_points_to_vps2'] = False
    result['authelia_configuration_present'] = Path('/etc/owner-hq/identity/config/configuration.yml').is_file()
    result['investscan_nginx_present'] = Path('/etc/nginx/sites-enabled/invest.ugsdom.ru').is_file()
    for name, url, keys in [
        ('hq', 'https://shtab.ugsdom.ru/health', ('ok', 'mode', 'release')),
        ('oidc', 'https://login.ugsdom.ru/.well-known/openid-configuration', ('issuer', 'code_challenge_methods_supported')),
    ]:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                body = json.load(response)
                result[name] = {'status': 'ok', **{key: body.get(key) for key in keys}}
        except Exception:
            result[name] = {'status': 'error'}
    # Facts only: these observations do not prove backup restore, rights or SSO readiness.
    return result


if __name__ == '__main__':
    print(json.dumps(inspect(), ensure_ascii=False, sort_keys=True))
