import enum
import os

from appodus_utils.exception.exceptions import InternalServerException
from httpx import AsyncClient
from starlette import status

from appodus_utils.sdk.appodus_sdk.communication.communication_client import CommunicationClient
from appodus_utils.sdk.appodus_sdk.contract_client import ContractClient
from appodus_utils.sdk.appodus_sdk.document_client import DocumentClient
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class ApiVersion(str, enum.Enum):
    V1 = "v1"


class AppodusClient:
    """
    This is a utility class that abstracts the various appodus utility services:
        [document_manager, contract_manager, communication_manager]
    """

    def __init__(self, client_id: str, client_secret: str, api_version: ApiVersion):
        self._http_client = AsyncClient(timeout=30.0)
        self._document_manager_url = None
        self._contract_manager_url = None
        self._communication_manager_url = None
        self._client_utils = AppodusClientUtils(
            client_id=client_id,
            client_secret=client_secret,
            api_version=api_version,
            http_client=self._http_client
        )

    async def require_document_manager(self):
        """
        Initialize self._document_manager_url

        :return:
        """
        try:
            self._document_manager_url = os.getenv('DOCUMENT_MANAGER_URL')

            if not self._document_manager_url:
                raise InternalServerException(message="Env value with key 'DOCUMENT_MANAGER_URL' not set.")

            response = await self._http_client.get(f"{self._document_manager_url}/health")
            response.raise_for_status()

            if response.status_code != status.HTTP_200_OK:
                raise InternalServerException(
                    message=f"The provided DOCUMENT_MANAGER_URL, '{self._document_manager_url}', is not reachable.")
        except InternalServerException as e:
            raise
        except Exception as e:
            raise InternalServerException(message="Unable to 'require_document_manager'")

    async def require_contract_manager(self):
        """
        Initialize self._contract_manager_url

        :return:
        """
        try:
            self._contract_manager_url = os.getenv('CONTRACT_MANAGER_URL')

            if not self._contract_manager_url:
                raise InternalServerException(message="Env value with key 'CONTRACT_MANAGER_URL' not set.")

            response = await self._http_client.get(f"{self._contract_manager_url}/health")
            response.raise_for_status()

            if response.status_code != status.HTTP_200_OK:
                raise InternalServerException(
                    message=f"The provided CONTRACT_MANAGER_URL, '{self._contract_manager_url}', is not reachable.")
        except InternalServerException as e:
            raise
        except Exception as e:
            raise InternalServerException(message="Unable to 'require_contract_manager'")

    async def require_communication_manager(self):
        """
        Initialize self._communication_manager_url

        :return:
        """
        try:
            self._communication_manager_url = os.getenv('COMMUNICATION_MANAGER_URL')

            if not self._communication_manager_url:
                raise InternalServerException(message="Env value with key 'COMMUNICATION_MANAGER_URL' not set.")

            response = await self._http_client.get(f"{self._communication_manager_url}/health")
            response.raise_for_status()

            if response.status_code != status.HTTP_200_OK:
                raise InternalServerException(
                    message=f"The provided COMMUNICATION_MANAGER_URL, '{self._communication_manager_url}', is not reachable.")
        except InternalServerException as e:
            raise
        except Exception as e:
            raise InternalServerException(message="Unable to 'require_communication_manager'")

    @property
    def communication(self) -> CommunicationClient:
        return CommunicationClient(
            communication_manager_url=self._communication_manager_url,
            client_utils=self._client_utils
        )

    @property
    def contract(self) -> ContractClient:
        return ContractClient(
            contract_manager_url=self._contract_manager_url,
            client_utils=self._client_utils
        )

    @property
    def document(self) -> DocumentClient:
        return DocumentClient(
            document_manager_url=self._document_manager_url,
            client_utils=self._client_utils
        )
