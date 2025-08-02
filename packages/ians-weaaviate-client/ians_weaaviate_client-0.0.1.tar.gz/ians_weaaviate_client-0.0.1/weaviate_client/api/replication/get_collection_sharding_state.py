from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.replication_sharding_state_response import ReplicationShardingStateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["collection"] = collection

    params["shard"] = shard

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/replication/sharding-state",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]:
    if response.status_code == 200:
        response_200 = ReplicationShardingStateResponse.from_dict(response.json())

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
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
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
) -> Response[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]:
    """Get sharding state

     Fetches the current sharding state, including replica locations and statuses, for all collections or
    a specified collection. If a shard name is provided along with a collection, the state for that
    specific shard is returned.

    Args:
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]
    """

    kwargs = _get_kwargs(
        collection=collection,
        shard=shard,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]:
    """Get sharding state

     Fetches the current sharding state, including replica locations and statuses, for all collections or
    a specified collection. If a shard name is provided along with a collection, the state for that
    specific shard is returned.

    Args:
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationShardingStateResponse]
    """

    return sync_detailed(
        client=client,
        collection=collection,
        shard=shard,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]:
    """Get sharding state

     Fetches the current sharding state, including replica locations and statuses, for all collections or
    a specified collection. If a shard name is provided along with a collection, the state for that
    specific shard is returned.

    Args:
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]
    """

    kwargs = _get_kwargs(
        collection=collection,
        shard=shard,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    collection: Union[Unset, str] = UNSET,
    shard: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, ReplicationShardingStateResponse]]:
    """Get sharding state

     Fetches the current sharding state, including replica locations and statuses, for all collections or
    a specified collection. If a shard name is provided along with a collection, the state for that
    specific shard is returned.

    Args:
        collection (Union[Unset, str]):
        shard (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationShardingStateResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            collection=collection,
            shard=shard,
        )
    ).parsed
