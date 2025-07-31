import sys
import argparse
from flespi_sdk.modules.subaccounts.account import Account
from flespi_sdk import token_login, realm_login


async def get_account(prog: str = sys.argv[0]) -> Account:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="CLI for Flespi SDK",
        epilog=f"Examples:\n  {prog} <token>\n  {prog} <realm> <username> <password>",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "args",
        nargs="+",
        help=(
            "Arguments for login:\n"
            "  - Provide 1 argument: <token>\n"
            "  - Provide 3 arguments: <realm> <username> <password>"
        ),
    )

    args = parser.parse_args()

    account: Account | None = None
    if len(args.args) == 1:
        token = args.args[0]
        try:
            account = await token_login(token)
        except Exception as e:
            if account:
                await account.stop()
            raise e
        return account
    elif len(args.args) == 3:
        realm, username, password = args.args
        try:
            account = await realm_login(realm, username, password)
        except Exception as e:
            if account:
                await account.stop()
            raise e
        return account
    else:
        parser.error(
            "Invalid number of arguments. Provide 1 argument (token) or 3 arguments (realm, username, password)."
        )
