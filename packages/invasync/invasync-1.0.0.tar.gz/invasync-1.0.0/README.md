# InvaSync

Synchronize your [flashed invaders](https://www.space-invaders.com/flashinvaders) to your [MySpaceInvaderMap](https://invaders.code-rhapsodie.com) easily!

## Installation

```sh
uv tool install .
```

## Usage

1. Create a `users.json` file:

```json
{
  "your_name": {
    "flash_uid": "YOUR FLASH UID",
    "map_token": "YOUR INVADER MAP PHPSESSID"
  }
}
```

2. Run InvaSync:

```sh
invasync -u users.json
```

3. Enjoy!

## Automatic updates

The following code will schedule a cron job running everyday at 6 pm:

```crontab
0 18 * * * /home/USER/.local/bin/invasync -u /path/to/user.json
```
