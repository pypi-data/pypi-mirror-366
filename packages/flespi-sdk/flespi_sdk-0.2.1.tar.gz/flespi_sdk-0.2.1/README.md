# Install

```
pip install flespi-sdk

```

# Usage

```python
from flespi_sdk.account import Account

# log into account
account = Account()
await account.set_token("<flespi-token>")
# or
# await account.realm_login("<realm-public-id>", "<realm-username>", "<realm-password>")

# use account

print("Metadata", await account.metadata.get())
print("Direct subaccount IDs", [subaccount.id for subaccount in await account.subaccounts.list()])
print("Flespi API counters", await account.mqtt.list("flespi/state/platform/customer/counters/api/#"))

```

# Examples

### Read emails from MQTT for all subaccounts (master token required)

```python
from flespi_sdk.cli import get_account


async def main():
    account = None
    try:
        account = await get_account()
        subaccounts = await account.subaccounts.list()
        for subaccount in subaccounts:
            name = await subaccount.metadata.get_value("sys_user_config.title")
            mqtt_msg = await subaccount.mqtt.get("flespi/state/platform/customer/email")
            email = mqtt_msg["payload"]
            print(f"Subaccount ID: {subaccount.id}, Name: {name}, Email: {email}")
    except Exception as e:
        print("Error:", e)
    finally:
        if account:
            await account.stop()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

```

### Manipulate realms and users

```python
acc = Account()
await acc.set_token(acc_token)

realms = await acc.realms.list(selector="all")
for realm in realms:
    print(realm.id, await realm.get_name(), await realm.metadata.get())
    users = await realm.users.list()
    for user in users:
        print(user.id, await user.get_name(), await user.metadata.get())

realm = await acc.realms.get(22644)
user = await realm.users.get(90287)
await user.metadata.set_value("test-metadata-key", "123")
print(await user.metadata.get())
await user.metadata.delete_value("test-metadata-key")
print(await user.metadata.get())
await user.update_password("newpassword123456789")
```
