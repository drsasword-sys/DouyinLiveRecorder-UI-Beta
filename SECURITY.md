# Security

## Local trust boundary

The UI binds only to `127.0.0.1:8765`. Do not expose this port to a LAN or the
public internet. Requests accept only allowlisted Douyin/TikTok hosts and are
limited to 4 KB.

## Secrets

Never commit or share `config/config.ini`. It may contain cookies, notification
tokens, email credentials or platform passwords. Runtime config, URL lists,
logs, backups, downloads and release archives are ignored by Git.

## Reporting

Report vulnerabilities through a private GitHub security advisory after the new
repository is created. Do not include cookies, stream URLs containing tokens or
recorded media in a public issue.
