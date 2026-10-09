"""Create fresh installation secrets locally; never prints credential values."""
from pathlib import Path
import getpass
import os
import secrets

root=Path(__file__).resolve().parent
if os.name=='posix' and os.geteuid() not in (0,1000):
    raise SystemExit('Run with sudo so Docker user1000 can access its private files.')
for name in ['data','browser-data']:
    target=root/name
    target.mkdir(mode=0o700,exist_ok=True)
    if os.name=='posix':
        os.chmod(target,0o700);os.chown(target,1000,1000)
for name in ['api-key','browser-bridge.key']:
    target=root/'data'/name
    if not target.exists():
        descriptor=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(descriptor,'w') as handle:handle.write(secrets.token_hex(32))
    if os.name=='posix':
        os.chmod(target,0o600);os.chown(target,1000,1000)
admin=root/'data/admin-password'
if not admin.exists():
    password=getpass.getpass('Eigenes Admin-Passwort (Enter = eigener API-Key): ')
    if password:
        if any(character in password for character in '\r\n\0') or password!=password.strip():
            raise SystemExit('Invalid password characters; run again.')
        descriptor=os.open(admin,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(descriptor,'w') as handle:handle.write(password)
if admin.exists() and os.name=='posix':
    os.chmod(admin,0o600);os.chown(admin,1000,1000)
print('Fresh private keys ready in data/. No credential values printed.')
