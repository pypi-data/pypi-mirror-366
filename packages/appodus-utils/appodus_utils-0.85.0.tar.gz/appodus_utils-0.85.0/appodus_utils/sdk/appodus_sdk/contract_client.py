from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class ContractClient:
    def __init__(self, contract_manager_url: str, client_utils: AppodusClientUtils):
        self._client_utils = client_utils
        self._contract_manager_url = contract_manager_url
