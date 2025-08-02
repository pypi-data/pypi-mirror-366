from .api import ChargeAPI, WebHookAPI, SubAccountAPI


SANDBOX_URL = "https://api.woovi-sandbox.com/api/v1/"
PRODUCTION_URL = "https://api.openpix.com.br/api/v1/"


class OpenPix:
    def __init__(self, *, app_id: str, sandbox: bool = False) -> None:
        self._headers = {"Authorization": app_id}
        if sandbox:
            self._url = SANDBOX_URL
        else:
            self._url = PRODUCTION_URL

        self._charge = None
        self._sub_account = None
        self._webhook = None

    @property
    def charge(self) -> ChargeAPI:
        if self._charge:
            return self._charge
        self._charge = ChargeAPI(url=self._url, headers=self._headers)
        return self._charge

    @property
    def sub_account(self) -> SubAccountAPI:
        if self._sub_account:
            return self._sub_account
        self._sub_account = SubAccountAPI(url=self._url, headers=self._headers)
        return self._sub_account

    @property
    def webhook(self) -> WebHookAPI:
        if self._webhook:
            return self._webhook
        self._webhook = WebHookAPI(url=self._url, headers=self._headers)
        return self._webhook

    def __repr__(self) -> str:
        return f"OpenPix()"
