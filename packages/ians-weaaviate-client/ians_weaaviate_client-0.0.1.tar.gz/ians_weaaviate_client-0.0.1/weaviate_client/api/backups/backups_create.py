from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.backup_create_request import BackupCreateRequest
from ...models.backup_create_response import BackupCreateResponse
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    backend: str,
    *,
    body: BackupCreateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/backups/{backend}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, BackupCreateResponse, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = BackupCreateResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403
    if response.status_code == 422:
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, BackupCreateResponse, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    backend: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: BackupCreateRequest,
) -> Response[Union[Any, BackupCreateResponse, ErrorResponse]]:
    """Start a backup process

     Start creating a backup for a set of collections. <br/><br/>Notes: <br/>- Weaviate uses gzip
    compression by default. <br/>- Weaviate stays usable while a backup process is ongoing.

    Args:
        backend (str):
        body (BackupCreateRequest): Request body for creating a backup of a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BackupCreateResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        backend=backend,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    backend: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: BackupCreateRequest,
) -> Optional[Union[Any, BackupCreateResponse, ErrorResponse]]:
    """Start a backup process

     Start creating a backup for a set of collections. <br/><br/>Notes: <br/>- Weaviate uses gzip
    compression by default. <br/>- Weaviate stays usable while a backup process is ongoing.

    Args:
        backend (str):
        body (BackupCreateRequest): Request body for creating a backup of a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BackupCreateResponse, ErrorResponse]
    """

    return sync_detailed(
        backend=backend,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    backend: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: BackupCreateRequest,
) -> Response[Union[Any, BackupCreateResponse, ErrorResponse]]:
    """Start a backup process

     Start creating a backup for a set of collections. <br/><br/>Notes: <br/>- Weaviate uses gzip
    compression by default. <br/>- Weaviate stays usable while a backup process is ongoing.

    Args:
        backend (str):
        body (BackupCreateRequest): Request body for creating a backup of a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BackupCreateResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        backend=backend,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    backend: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: BackupCreateRequest,
) -> Optional[Union[Any, BackupCreateResponse, ErrorResponse]]:
    """Start a backup process

     Start creating a backup for a set of collections. <br/><br/>Notes: <br/>- Weaviate uses gzip
    compression by default. <br/>- Weaviate stays usable while a backup process is ongoing.

    Args:
        backend (str):
        body (BackupCreateRequest): Request body for creating a backup of a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BackupCreateResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            backend=backend,
            client=client,
            body=body,
        )
    ).parsed
