import json
from enum import StrEnum
from typing import Union

from crypticorn.auth import AuthClient, Configuration, Verify200Response
from crypticorn.auth.client.exceptions import ApiException
from crypticorn_utils.enums import BaseUrl
from crypticorn_utils.exceptions import (
    BaseError,
    ErrorLevel,
    ErrorType,
    ExceptionHandler,
)
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    SecurityScopes,
)
from typing_extensions import Annotated


class AuthErrorCodes(StrEnum):
    INVALID_API_KEY = "invalid_api_key"
    EXPIRED_API_KEY = "expired_api_key"
    INVALID_BEARER = "invalid_bearer"
    EXPIRED_BEARER = "expired_bearer"
    INVALID_BASIC_AUTH = "invalid_basic_auth"
    NO_CREDENTIALS = "no_credentials"
    INSUFFICIENT_SCOPES = "insufficient_scopes"
    UNKNOWN_ERROR = "unknown_error"


class AuthError(BaseError):
    INVALID_API_KEY = (
        AuthErrorCodes.INVALID_API_KEY,
        ErrorType.USER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    INVALID_BASIC_AUTH = (
        AuthErrorCodes.INVALID_BASIC_AUTH,
        ErrorType.USER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    INVALID_BEARER = (
        AuthErrorCodes.INVALID_BEARER,
        ErrorType.USER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    EXPIRED_API_KEY = (
        AuthErrorCodes.EXPIRED_API_KEY,
        ErrorType.USER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    EXPIRED_BEARER = (
        AuthErrorCodes.EXPIRED_BEARER,
        ErrorType.USER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    NO_CREDENTIALS = (
        AuthErrorCodes.NO_CREDENTIALS,
        ErrorType.USER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    INSUFFICIENT_SCOPES = (
        AuthErrorCodes.INSUFFICIENT_SCOPES,
        ErrorType.USER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_403_FORBIDDEN,
        status.WS_1008_POLICY_VIOLATION,
    )
    UNKNOWN_ERROR = (
        AuthErrorCodes.UNKNOWN_ERROR,
        ErrorType.SERVER_ERROR,
        ErrorLevel.ERROR,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.WS_1011_INTERNAL_ERROR,
    )


handler = ExceptionHandler(callback=AuthError.from_identifier)

AUTHENTICATE_HEADER = "WWW-Authenticate"
BEARER_AUTH_SCHEME = "Bearer"
APIKEY_AUTH_SCHEME = "X-API-Key"
BASIC_AUTH_SCHEME = "Basic"

# Auth Schemes
http_bearer = HTTPBearer(
    bearerFormat="JWT",
    auto_error=False,
    description="The JWT to use for authentication.",
)

apikey_header = APIKeyHeader(
    name=APIKEY_AUTH_SCHEME,
    auto_error=False,
    description="The API key to use for authentication.",
)

http_basic = HTTPBasic(
    scheme_name=BASIC_AUTH_SCHEME,
    auto_error=False,
    description="The username and password to use for authentication.",
)


# Auth Handler
class AuthHandler:
    """
    Middleware for verifying API requests. Verifies the validity of the authentication token, scopes, etc.

    :param base_url: The base URL of the API.
    :param api_version: The version of the API.
    """

    def __init__(
        self,
        base_url: BaseUrl = BaseUrl.PROD,
    ):
        self.url = f"{base_url}/v1/auth"
        self.client = AuthClient(Configuration(host=self.url), is_sync=False)

    async def _verify_api_key(self, api_key: str) -> Verify200Response:
        """
        Verifies the API key.
        """
        self.client.config.api_key = {"APIKeyHeader": api_key}
        return await self.client.login.verify()

    async def _verify_bearer(
        self, bearer: HTTPAuthorizationCredentials
    ) -> Verify200Response:
        """
        Verifies the bearer token.
        """
        self.client.config.access_token = bearer.credentials
        return await self.client.login.verify()

    async def _verify_basic(self, basic: HTTPBasicCredentials) -> Verify200Response:
        """
        Verifies the basic authentication credentials.
        """
        return await self.client.login.verify_basic_auth(basic.username, basic.password)

    async def _validate_scopes(
        self, api_scopes: list[str], user_scopes: list[str]
    ) -> None:
        """
        Checks if the required scopes are a subset of the user scopes.
        """
        if not set(api_scopes).issubset(user_scopes):
            raise handler.build_exception(
                AuthErrorCodes.INSUFFICIENT_SCOPES,
                "Insufficient scopes to access this resource (required: "
                + ", ".join(api_scopes)
                + ")",
            )

    async def _extract_message(self, e: ApiException) -> str:
        """
        Tries to extract the message from the body of the exception.
        """
        try:
            load = json.loads(e.body)
        except (json.JSONDecodeError, TypeError):
            return e.body
        else:
            common_keys = ["message"]
            for key in common_keys:
                if key in load:
                    return load[key]
            return load

    async def _handle_exception(self, e: Exception) -> HTTPException:
        """
        Handles exceptions and returns a HTTPException with the appropriate status code and detail.
        """
        if isinstance(e, ApiException):
            # handle the TRPC Zod errors from auth-service
            # Unfortunately, we cannot share the error messages defined in python/crypticorn/common/errors.py with the typescript client
            message = await self._extract_message(e)
            if message == "Invalid API key":
                error = AuthErrorCodes.INVALID_API_KEY
            elif message == "API key expired":
                error = AuthErrorCodes.EXPIRED_API_KEY
            elif message == "jwt expired":
                error = AuthErrorCodes.EXPIRED_BEARER
            elif message == "Invalid basic authentication credentials":
                error = AuthErrorCodes.INVALID_BASIC_AUTH
            else:
                message = "Invalid bearer token"
                error = (
                    AuthErrorCodes.INVALID_BEARER
                )  # jwt malformed, jwt not active (https://www.npmjs.com/package/jsonwebtoken#errors--codes)
            return handler.build_exception(error, message)

        elif isinstance(e, HTTPException):
            return e
        else:
            return handler.build_exception(AuthErrorCodes.UNKNOWN_ERROR, str(e))

    async def api_key_auth(
        self,
        api_key: Annotated[Union[str, None], Depends(apikey_header)] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the API key and checks the scopes.
        Use this function if you only want to allow access via the API key.
        This function is used for HTTP connections.
        """
        try:
            return await self.full_auth(
                bearer=None, api_key=api_key, basic=None, sec=sec
            )
        except HTTPException as e:
            raise handler.build_exception(
                e.detail.get("code"),
                e.detail.get("message"),
                headers={AUTHENTICATE_HEADER: APIKEY_AUTH_SCHEME},
            )

    async def bearer_auth(
        self,
        bearer: Annotated[
            Union[HTTPAuthorizationCredentials, None],
            Depends(http_bearer),
        ] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and checks the scopes.
        Use this function if you only want to allow access via the bearer token.
        This function is used for HTTP connections.
        """
        try:
            return await self.full_auth(
                bearer=bearer, api_key=None, basic=None, sec=sec
            )
        except HTTPException as e:
            raise handler.build_exception(
                e.detail.get("code"),
                e.detail.get("message"),
                headers={AUTHENTICATE_HEADER: BEARER_AUTH_SCHEME},
            )

    async def basic_auth(
        self,
        credentials: Annotated[Union[HTTPBasicCredentials, None], Depends(http_basic)],
    ) -> Verify200Response:
        """
        Verifies the basic authentication credentials. This authentication method should just be used for special cases like /admin/metrics, where JWT and API key authentication are not desired or not possible.
        """
        try:
            return await self.full_auth(
                basic=credentials, bearer=None, api_key=None, sec=None
            )
        except HTTPException as e:
            raise handler.build_exception(
                e.detail.get("code"),
                e.detail.get("message"),
                headers={AUTHENTICATE_HEADER: BASIC_AUTH_SCHEME},
            )

    async def combined_auth(
        self,
        bearer: Annotated[
            Union[HTTPAuthorizationCredentials, None], Depends(http_bearer)
        ] = None,
        api_key: Annotated[Union[str, None], Depends(apikey_header)] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and/or API key and checks the scopes.
        Returns early on the first successful verification, otherwise tries all available tokens.
        Use this function if you want to allow access via either the bearer token or the API key.
        This function is used for HTTP connections.
        """
        try:
            return await self.full_auth(
                basic=None, bearer=bearer, api_key=api_key, sec=sec
            )
        except HTTPException as e:
            raise handler.build_exception(
                e.detail.get("code"),
                e.detail.get("message"),
                headers={
                    AUTHENTICATE_HEADER: f"{BEARER_AUTH_SCHEME}, {APIKEY_AUTH_SCHEME}"
                },
            )

    async def full_auth(
        self,
        basic: Annotated[Union[HTTPBasicCredentials, None], Depends(http_basic)] = None,
        bearer: Annotated[
            Union[HTTPAuthorizationCredentials, None], Depends(http_bearer)
        ] = None,
        api_key: Annotated[Union[str, None], Depends(apikey_header)] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        IMPORTANT: combined_auth is sufficient for most use cases. This function adds basic auth to the mix, which is needed for external services like prometheus, but is not recommended for internal use.
        Verifies the bearer token, API key and basic authentication credentials and checks the scopes.
        Returns early on the first successful verification, otherwise tries all available tokens.
        Use this function if you want to allow access via either the bearer token, the API key or the basic authentication credentials.
        This function is used for HTTP connections.
        """
        tokens = [bearer, api_key, basic]
        last_error = None
        for token in tokens:
            try:
                if token is None:
                    continue
                res = None
                if isinstance(token, str):
                    res = await self._verify_api_key(token)
                elif isinstance(token, HTTPAuthorizationCredentials):
                    res = await self._verify_bearer(token)
                elif isinstance(token, HTTPBasicCredentials):
                    res = await self._verify_basic(token)
                if res is None:
                    continue
                if sec:
                    await self._validate_scopes(sec.scopes, res.scopes)
                return res

            except Exception as e:
                last_error = await self._handle_exception(e)
                continue

        if last_error:
            raise last_error
        else:
            raise handler.build_exception(
                AuthErrorCodes.NO_CREDENTIALS,
                "No credentials provided. Check the WWW-Authenticate header for the available authentication methods.",
                headers={
                    AUTHENTICATE_HEADER: f"{BEARER_AUTH_SCHEME}, {APIKEY_AUTH_SCHEME}, {BASIC_AUTH_SCHEME}"
                },
            )

    async def ws_api_key_auth(
        self,
        api_key: Annotated[Union[str, None], Query()] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the API key and checks the scopes.
        Use this function if you only want to allow access via the API key.
        This function is used for WebSocket connections.
        """
        return await self.api_key_auth(api_key=api_key, sec=sec)

    async def ws_bearer_auth(
        self,
        bearer: Annotated[Union[str, None], Query()] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and checks the scopes.
        Use this function if you only want to allow access via the bearer token.
        This function is used for WebSocket connections.
        """
        credentials = (
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=bearer)
            if bearer
            else None
        )
        return await self.bearer_auth(bearer=credentials, sec=sec)

    async def ws_combined_auth(
        self,
        bearer: Annotated[Union[str, None], Query()] = None,
        api_key: Annotated[Union[str, None], Query()] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and/or API key and checks the scopes.
        Use this function if you want to allow access via either the bearer token or the API key.
        This function is used for WebSocket connections.
        """
        credentials = (
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=bearer)
            if bearer
            else None
        )
        return await self.combined_auth(bearer=credentials, api_key=api_key, sec=sec)
