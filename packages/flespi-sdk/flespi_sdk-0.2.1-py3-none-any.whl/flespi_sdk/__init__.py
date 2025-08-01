from aiohttp import ClientSession

from flespi_sdk.modules.subaccounts.account import Account
from flespi_sdk.exception import FlespiException


async def token_login(token: str) -> Account:
    async with ClientSession("https://flespi.io") as session:
        async with session.get(
            "/platform/customer",
            params=dict(fields="id,name,metadata"),
            headers=dict(Authorization=f"FlespiToken {token}"),
        ) as response:
            if response.status != 200:
                raise FlespiException(
                    status_code=response.status,
                    errors=(await response.json())["errors"],
                )
            response_json = await response.json()
            result = response_json["result"]
            return Account(
                item=result[0],
                session=ClientSession(
                    "https://flespi.io",
                    headers=dict(Authorization=f"FlespiToken {token}"),
                ),
            )


async def realm_login(
    realm_public_id: str,
    realm_username: str,
    realm_password: str,
) -> Account:
    """
    Login to a realm and set the Authorization header for subsequent requests.
    :param realm_public_id: Public ID of the realm.
    :param realm_username: Username for the realm.
    :param realm_password: Password for the realm.
    :raises Exception: If the login fails.
    """
    if not realm_public_id or not realm_username or not realm_password:
        raise ValueError("All parameters are required")

    async with ClientSession("https://flespi.io") as session:
        async with session.post(
            f"/realm/{realm_public_id}/login",
            json={"username": realm_username, "password": realm_password},
        ) as response:
            if response.status != 200:
                raise Exception("Login failed")
            response_json = await response.json()

            token = response_json["result"][0]["token"]

            return await token_login(token)
