from aiohttp import ClientSession

from flespi_sdk.exception import FlespiException


class FlespiSession:
    def __init__(self, session: ClientSession, operate_as: int):
        self.operate_as = operate_as
        self.session = session

    def get_headers(self):
        if self.operate_as:
            return {"X-Flespi-CID": str(self.operate_as)}
        raise ValueError("CID is not set. Please set the CID before using this method.")

    async def get_result(self, response):
        if response.status != 200:
            raise FlespiException(
                status_code=response.status, errors=(await response.json())["errors"]
            )
        response_json = await response.json()
        result = response_json["result"]
        return result
