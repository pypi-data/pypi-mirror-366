from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.backup_restore_request import BackupRestoreRequest
from ...models.backup_restore_response import BackupRestoreResponse
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    backend: str,
    id: str,
    *,
    body: BackupRestoreRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/backups/{backend}/{id}/restore",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, BackupRestoreResponse, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = BackupRestoreResponse.from_dict(response.json())

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
) -> Response[Union[Any, BackupRestoreResponse, ErrorResponse]]:
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
    body: BackupRestoreRequest,
) -> Response[Union[Any, BackupRestoreResponse, ErrorResponse]]:
    """Start a restoration process

     Starts a process of restoring a backup for a set of collections. <br/><br/>Any backup can be
    restored to any machine, as long as the number of nodes between source and target are
    identical.<br/><br/>Requrements:<br/><br/>- None of the collections to be restored already exist on
    the target restoration node(s).<br/>- The node names of the backed-up collections' must match those
    of the target restoration node(s).

    Args:
        backend (str):
        id (str):
        body (BackupRestoreRequest): Request body for restoring a backup for a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BackupRestoreResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        backend=backend,
        id=id,
        body=body,
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
    body: BackupRestoreRequest,
) -> Optional[Union[Any, BackupRestoreResponse, ErrorResponse]]:
    """Start a restoration process

     Starts a process of restoring a backup for a set of collections. <br/><br/>Any backup can be
    restored to any machine, as long as the number of nodes between source and target are
    identical.<br/><br/>Requrements:<br/><br/>- None of the collections to be restored already exist on
    the target restoration node(s).<br/>- The node names of the backed-up collections' must match those
    of the target restoration node(s).

    Args:
        backend (str):
        id (str):
        body (BackupRestoreRequest): Request body for restoring a backup for a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BackupRestoreResponse, ErrorResponse]
    """

    return sync_detailed(
        backend=backend,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    backend: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: BackupRestoreRequest,
) -> Response[Union[Any, BackupRestoreResponse, ErrorResponse]]:
    """Start a restoration process

     Starts a process of restoring a backup for a set of collections. <br/><br/>Any backup can be
    restored to any machine, as long as the number of nodes between source and target are
    identical.<br/><br/>Requrements:<br/><br/>- None of the collections to be restored already exist on
    the target restoration node(s).<br/>- The node names of the backed-up collections' must match those
    of the target restoration node(s).

    Args:
        backend (str):
        id (str):
        body (BackupRestoreRequest): Request body for restoring a backup for a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BackupRestoreResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        backend=backend,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    backend: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: BackupRestoreRequest,
) -> Optional[Union[Any, BackupRestoreResponse, ErrorResponse]]:
    """Start a restoration process

     Starts a process of restoring a backup for a set of collections. <br/><br/>Any backup can be
    restored to any machine, as long as the number of nodes between source and target are
    identical.<br/><br/>Requrements:<br/><br/>- None of the collections to be restored already exist on
    the target restoration node(s).<br/>- The node names of the backed-up collections' must match those
    of the target restoration node(s).

    Args:
        backend (str):
        id (str):
        body (BackupRestoreRequest): Request body for restoring a backup for a set of classes

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BackupRestoreResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            backend=backend,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
