"""Fujitsu General API Client."""
import asyncio
import logging
import socket
import os
import json
from typing import Any

import aiohttp
import async_timeout

from .exceptions import FGLairGeneralException
from .utils import isBlank

TIMEOUT = 10

HEADER_CONTENT_TYPE = "Content-Type"
HEADER_VALUE_CONTENT_TYPE = "application/json"
HEADER_AUTHORIZATION = "Authorization"


_LOGGER: logging.Logger = logging.getLogger(__package__)


def api_headers(access_token: str | None = None) -> dict[str, str]:
    headers = {HEADER_CONTENT_TYPE: HEADER_VALUE_CONTENT_TYPE}
    if access_token:
        headers[HEADER_AUTHORIZATION] = "auth_token " + access_token
    return headers


class FGLairApiClient:
    def __init__(
        self,
        username: str,
        password: str,
        region: str,
        tokenpath: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """FGLairApiClient API Client."""
        self._username = username
        self._password = password
        self._region = region
        self._tokenpath = tokenpath
        self._session = session

        if region == "eu":
            self._SIGNIN_BODY = '{"user":{"email":"%s","password":"%s","application":{"app_id":"FGLair-eu-id","app_secret":"FGLair-eu-gpFbVBRoiJ8E3QWJ-QRULLL3j3U"}}}'
            self._API_GET_ACCESS_TOKEN_URL = (
                "https://user-field-eu.aylanetworks.com/users/sign_in.json"
            )
            API_BASE_URL = "https://ads-field-eu.aylanetworks.com/apiv1/"
        elif region == "cn":
            self._SIGNIN_BODY = '{"user":{"email":"%s","password":"%s","application":{"app_id":"FGLairField-cn-id","app_secret":"FGLairField-cn-zezg7Y60YpAvy3HPwxvWLnd4Oh4"}}}'
            self._API_GET_ACCESS_TOKEN_URL = (
                "https://user-field.ayla.com.cn/users/sign_in.json"
            )
            API_BASE_URL = "https://ads-field.ayla.com.cn/apiv1/"
        else:
            self._SIGNIN_BODY = '{\r\n    "user": {\r\n        "email": "%s",\r\n        "application": {\r\n            "app_id": "CJIOSP-id",\r\n            "app_secret": "CJIOSP-Vb8MQL_lFiYQ7DKjN0eCFXznKZE"\r\n        },\r\n        "password": "%s"\r\n    }\r\n}'
            self._API_GET_ACCESS_TOKEN_URL = (
                "https://user-field.aylanetworks.com/users/sign_in.json"
            )
            API_BASE_URL = "https://ads-field.aylanetworks.com/apiv1/"

        self._API_GET_PROPERTIES_URL = API_BASE_URL + "dsns/{DSN}/properties.json"
        self._API_SET_PROPERTIES_URL = (
            API_BASE_URL + "properties/{property}/datapoints.json"
        )
        self._API_GET_DEVICES_URL = API_BASE_URL + "devices.json"
        self._ACCESS_TOKEN_FILE = tokenpath
        self._ACCESS_TOKEN_STR = None

    async def _async_read_token(self, access_token_file: str = "") -> str:
        if isBlank(access_token_file):
            access_token_file = self._ACCESS_TOKEN_FILE
        if (
            os.path.exists(access_token_file)
            and os.stat(access_token_file).st_size != 0
        ):
            f = open(access_token_file, "r", encoding="utf-8")
            access_token_file_content = f.read()

            # now = int(time.time())

            access_token: str = json.loads(access_token_file_content)["access_token"]
            # refresh_token = access_token_file_content.json()['refresh_token']
            # expires_in = access_token_file_content.json()['expires_in']
            # auth_time = int(access_token_file_content.json()['time'])
            return access_token
        else:
            return await self.async_authenticate()

    async def _async_get_devices(self, access_token: str | None = None) -> Any:
        token_valid = await self._async_check_token_validity(access_token)
        if not token_valid:
            # Token invalid requesting authentication
            access_token = await self.async_authenticate()
        response_json = await self.api_wrapper(
            "get", self._API_GET_DEVICES_URL, access_token=access_token
        )
        return response_json

    async def async_get_devices_dsn(self) -> list[str]:
        devices = await self._async_get_devices()
        devices_dsn: list[str] = []
        for device in devices:
            devices_dsn.append(device["device"]["dsn"])
        return devices_dsn

    async def async_get_device_property(self, property_code: int) -> Any:
        access_token = await self._async_read_token()
        token_valid = await self._async_check_token_validity(access_token)
        if not token_valid:
            access_token = await self.async_authenticate()

        response = await self.api_wrapper(
            "get", self._API_SET_PROPERTIES_URL.format(property=property_code)
        )

        return response.json()

    async def async_get_device_properties(self, dsn: str) -> Any:
        access_token = await self._async_read_token()
        token_valid = await self._async_check_token_validity(access_token)
        if not token_valid:
            access_token = await self.async_authenticate()

        response = await self.api_wrapper(
            "get",
            url=self._API_GET_PROPERTIES_URL.format(DSN=dsn),
            access_token=access_token,
        )

        return response

    async def async_set_device_property(self, property_code: int, value: Any) -> Any:
        access_token = await self._async_read_token()
        if not await self._async_check_token_validity(access_token):
            access_token = await self.async_authenticate()

        json_data: str = '{"datapoint": {"value": "' + str(value) + '" } }'
        response = await self.api_wrapper(
            "post",
            url=self._API_SET_PROPERTIES_URL.format(property=property_code),
            json_data=json_data,
            access_token=access_token,
        )
        return response

    async def _async_check_token_validity(
        self, access_token: str | None = None
    ) -> bool:
        if not access_token:
            return False
        try:
            response = await self.api_wrapper(
                method="get", url=self._API_GET_DEVICES_URL, access_token=access_token
            )
            if not response:
                return True
            else:
                return False
        except FGLairGeneralException:
            return False

    async def async_authenticate(self) -> str:
        response = await self.api_wrapper(
            "post",
            url=self._API_GET_ACCESS_TOKEN_URL,
            json_data=self._SIGNIN_BODY % (self._username, self._password),
        )

        access_token = response.get("access_token")
        # refresh_token = response.json()['refresh_token']
        # expires_in = response.json()['expires_in']

        with open(self._ACCESS_TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(response, f)

        self._ACCESS_TOKEN_STR = access_token

        return str(access_token)

    async def api_wrapper(
        self,
        method: str,
        url: str,
        json_data: str = "",
        access_token: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            if not headers:
                headers = api_headers(access_token=access_token)
            loop = asyncio.get_event_loop()
            now = loop.time()
            async with async_timeout.timeout(now + TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    json_response = await response.json()
                    return json_response

                elif method == "post":
                    response = await self._session.post(
                        url, headers=headers, data=json_data
                    )
                    json_response = await response.json()
                    return json_response

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )
            raise FGLairGeneralException() from exception
        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
            raise FGLairGeneralException() from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
            raise FGLairGeneralException() from exception
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
            raise FGLairGeneralException() from exception
