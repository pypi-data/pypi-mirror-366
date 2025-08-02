from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.backup_create_status_response import BackupCreateStatusResponse
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    backend: str,
    id: str,
    *,
    bucket: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["bucket"] = bucket

    params["path"] = path

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/backups/{backend}/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, BackupCreateStatusResponse, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = BackupCreateStatusResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
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
) -> Response[Union[Any, BackupCreateStatusResponse, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    backend: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bucket: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
) -> Response[Union[Any, BackupCreateStatusResponse, ErrorResponse]]:
    """Get backup process status

     Returns status of backup creation attempt for a set of collections. <br/><br/>All client
    implementations have a `wait for completion` option which will poll the backup status in the
    background and only return once the backup has completed (successfully or unsuccessfully). If you
    set the `wait for completion` option to false, you can also check the status yourself using this
    endpoint.

    Args:
        backend (str):
        id (str):
        bucket (Union[Unset, str]):
        path (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BackupCreateStatusResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        backend=backend,
        id=id,
        bucket=bucket,
        path=path,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    backend: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bucket: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, BackupCreateStatusResponse, ErrorResponse]]:
    """Get backup process status

     Returns status of backup creation attempt for a set of collections. <br/><br/>All client
    implementations have a `wait for completion` option which will poll the backup status in the
    background and only return once the backup has completed (successfully or unsuccessfully). If you
    set the `wait for completion` option to false, you can also check the status yourself using this
    endpoint.

    Args:
        backend (str):
        id (str):
        bucket (Union[Unset, str]):
        path (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BackupCreateStatusResponse, ErrorResponse]
    """

    return sync_detailed(
        backend=backend,
        id=id,
        client=client,
        bucket=bucket,
        path=path,
    ).parsed


async def asyncio_detailed(
    backend: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bucket: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
) -> Response[Union[Any, BackupCreateStatusResponse, ErrorResponse]]:
    """Get backup process status

     Returns status of backup creation attempt for a set of collections. <br/><br/>All client
    implementations have a `wait for completion` option which will poll the backup status in the
    background and only return once the backup has completed (successfully or unsuccessfully). If you
    set the `wait for completion` option to false, you can also check the status yourself using this
    endpoint.

    Args:
        backend (str):
        id (str):
        bucket (Union[Unset, str]):
        path (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BackupCreateStatusResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        backend=backend,
        id=id,
        bucket=bucket,
        path=path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    backend: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bucket: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, BackupCreateStatusResponse, ErrorResponse]]:
    """Get backup process status

     Returns status of backup creation attempt for a set of collections. <br/><br/>All client
    implementations have a `wait for completion` option which will poll the backup status in the
    background and only return once the backup has completed (successfully or unsuccessfully). If you
    set the `wait for completion` option to false, you can also check the status yourself using this
    endpoint.

    Args:
        backend (str):
        id (str):
        bucket (Union[Unset, str]):
        path (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BackupCreateStatusResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            backend=backend,
            id=id,
            client=client,
            bucket=bucket,
            path=path,
        )
    ).parsed
