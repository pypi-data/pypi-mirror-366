from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.replication_replicate_details_replica_response import ReplicationReplicateDetailsReplicaResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    target_node: Union[Unset, str] = UNSET,
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
    include_history: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["targetNode"] = target_node

    params["collection"] = collection

    params["shard"] = shard

    params["includeHistory"] = include_history

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/replication/replicate/list",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, list["ReplicationReplicateDetailsReplicaResponse"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ReplicationReplicateDetailsReplicaResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403
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
) -> Response[Union[Any, ErrorResponse, list["ReplicationReplicateDetailsReplicaResponse"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    target_node: Union[Unset, str] = UNSET,
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
    include_history: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ErrorResponse, list["ReplicationReplicateDetailsReplicaResponse"]]]:
    """List replication operations

     Retrieves a list of currently registered replication operations, optionally filtered by collection,
    shard, or node ID.

    Args:
        target_node (Union[Unset, str]):
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['ReplicationReplicateDetailsReplicaResponse']]]
    """

    kwargs = _get_kwargs(
        target_node=target_node,
        collection=collection,
        shard=shard,
        include_history=include_history,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    target_node: Union[Unset, str] = UNSET,
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
    include_history: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ErrorResponse, list["ReplicationReplicateDetailsReplicaResponse"]]]:
    """List replication operations

     Retrieves a list of currently registered replication operations, optionally filtered by collection,
    shard, or node ID.

    Args:
        target_node (Union[Unset, str]):
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['ReplicationReplicateDetailsReplicaResponse']]
    """

    return sync_detailed(
        client=client,
        target_node=target_node,
        collection=collection,
        shard=shard,
        include_history=include_history,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    target_node: Union[Unset, str] = UNSET,
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
    include_history: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ErrorResponse, list["ReplicationReplicateDetailsReplicaResponse"]]]:
    """List replication operations

     Retrieves a list of currently registered replication operations, optionally filtered by collection,
    shard, or node ID.

    Args:
        target_node (Union[Unset, str]):
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['ReplicationReplicateDetailsReplicaResponse']]]
    """

    kwargs = _get_kwargs(
        target_node=target_node,
        collection=collection,
        shard=shard,
        include_history=include_history,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    target_node: Union[Unset, str] = UNSET,
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
    include_history: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ErrorResponse, list["ReplicationReplicateDetailsReplicaResponse"]]]:
    """List replication operations

     Retrieves a list of currently registered replication operations, optionally filtered by collection,
    shard, or node ID.

    Args:
        target_node (Union[Unset, str]):
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):
        include_history (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['ReplicationReplicateDetailsReplicaResponse']]
    """

    return (
        await asyncio_detailed(
            client=client,
            target_node=target_node,
            collection=collection,
            shard=shard,
            include_history=include_history,
        )
    ).parsed
