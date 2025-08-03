import argparse
import asyncio
import json
from pathlib import Path

import httpx

FLASH_GALLERY_ENDPOINT = "https://api.space-invaders.com/flashinvaders_v3_pas_trop_predictif/api/gallery?uid="
MAP_RESTORE_ENDPOINT = "https://invaders.code-rhapsodie.com/restore"


class User:
    def __init__(self, name: str, flash_uid: str, map_token: str) -> None:
        self.name = name
        self.flash_uid = flash_uid
        self.map_token = map_token

    async def run(self, client: httpx.AsyncClient) -> None:
        try:
            await self._get_csrf_token(client)
            await self._get_invaders(client)
            await self._update_map(client)
            print(f"[+] [{self.name}] - Updated user's map")
        except IndexError:
            print(f"[!] [{self.name}] - Bad map token")
        except Exception as e:  # noqa: BLE001
            print(f"[!] [{self.name}] - {e}")

    async def _get_csrf_token(self, client: httpx.AsyncClient) -> None:
        print(f"[+] [{self.name}] - Fetching CSRF token")
        response = await client.get(
            MAP_RESTORE_ENDPOINT,
            cookies={"PHPSESSID": self.map_token},
        )
        html_text = response.text
        self.csrf_token = html_text.split('csrf-protection" value="')[1].split('"')[0]

    async def _get_invaders(self, client: httpx.AsyncClient) -> None:
        print(f"[+] [{self.name}] - Fetching flashed invaders")
        response = await client.get(f"{FLASH_GALLERY_ENDPOINT}{self.flash_uid}")
        data: dict = response.json()
        self.invaders_payload = (
            "[" + ",".join([f'"{invader_id}"' for invader_id in data["invaders"]]) + "]"
        )

    async def _update_map(self, client: httpx.AsyncClient) -> None:
        print(f"[+] [{self.name}] - Updating map")
        await client.post(
            MAP_RESTORE_ENDPOINT,
            data={
                "restore[_token]": self.csrf_token,
            },
            files={
                "restore[file]": (
                    "invaders.txt",
                    self.invaders_payload.encode("utf-8"),
                    "text/plain",
                ),
            },
            cookies={"PHPSESSID": self.map_token},
        )


def load_json(users_json: Path) -> list[User]:
    with users_json.open("r") as file:
        data = json.load(file)
        return [
            User(
                name=name,
                flash_uid=data["flash_uid"],
                map_token=data["map_token"],
            )
            for name, data in data.items()
        ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invaders synchronizer")
    parser.add_argument(
        "-u",
        "--users",
        type=Path,
        required=True,
        help="Path to the JSON users file",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    users = load_json(args.users)
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[user.run(client) for user in users])


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
