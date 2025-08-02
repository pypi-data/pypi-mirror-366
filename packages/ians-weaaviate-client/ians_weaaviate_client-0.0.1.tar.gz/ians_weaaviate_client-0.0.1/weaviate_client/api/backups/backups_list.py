from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.backup_list_response_item import BackupListResponseItem
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    backend: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/backups/{backend}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, list["BackupListResponseItem"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_backup_list_response_item_data in _response_200:
            componentsschemas_backup_list_response_item = BackupListResponseItem.from_dict(
                componentsschemas_backup_list_response_item_data
            )

            response_200.append(componentsschemas_backup_list_response_item)

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
) -> Response[Union[Any, ErrorResponse, list["BackupListResponseItem"]]]:
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
) -> Response[Union[Any, ErrorResponse, list["BackupListResponseItem"]]]:
    """List backups in progress

     [Coming soon] List all backups in progress not implemented yet.

    Args:
        backend (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['BackupListResponseItem']]]
    """

    kwargs = _get_kwargs(
        backend=backend,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    backend: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, ErrorResponse, list["BackupListResponseItem"]]]:
    """List backups in progress

     [Coming soon] List all backups in progress not implemented yet.

    Args:
        backend (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['BackupListResponseItem']]
    """

    return sync_detailed(
        backend=backend,
        client=client,
    ).parsed


async def asyncio_detailed(
    backend: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, ErrorResponse, list["BackupListResponseItem"]]]:
    """List backups in progress

     [Coming soon] List all backups in progress not implemented yet.

    Args:
        backend (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['BackupListResponseItem']]]
    """

    kwargs = _get_kwargs(
        backend=backend,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    backend: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, ErrorResponse, list["BackupListResponseItem"]]]:
    """List backups in progress

     [Coming soon] List all backups in progress not implemented yet.

    Args:
        backend (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['BackupListResponseItem']]
    """

    return (
        await asyncio_detailed(
            backend=backend,
            client=client,
        )
    ).parsed
