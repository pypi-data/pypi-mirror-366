from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.replication_replicate_details_replica_response import ReplicationReplicateDetailsReplicaResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID,
    *,
    include_history: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["includeHistory"] = include_history

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/replication/replicate/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]:
    if response.status_code == 200:
        response_200 = ReplicationReplicateDetailsReplicaResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 422:
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if response.status_code == 501:
        response_501 = ErrorResponse.from_dict(response.json())

        return response_501
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include_history: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]:
    """Retrieve a replication operation

     Fetches the current status and detailed information for a specific replication operation, identified
    by its unique ID. Optionally includes historical data of the operation's progress if requested.

    Args:
        id (UUID):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        include_history=include_history,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include_history: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]:
    """Retrieve a replication operation

     Fetches the current status and detailed information for a specific replication operation, identified
    by its unique ID. Optionally includes historical data of the operation's progress if requested.

    Args:
        id (UUID):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]
    """

    return sync_detailed(
        id=id,
        client=client,
        include_history=include_history,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include_history: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]:
    """Retrieve a replication operation

     Fetches the current status and detailed information for a specific replication operation, identified
    by its unique ID. Optionally includes historical data of the operation's progress if requested.

    Args:
        id (UUID):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        include_history=include_history,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include_history: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]]:
    """Retrieve a replication operation

     Fetches the current status and detailed information for a specific replication operation, identified
    by its unique ID. Optionally includes historical data of the operation's progress if requested.

    Args:
        id (UUID):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationReplicateDetailsReplicaResponse]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            include_history=include_history,
        )
    ).parsed
