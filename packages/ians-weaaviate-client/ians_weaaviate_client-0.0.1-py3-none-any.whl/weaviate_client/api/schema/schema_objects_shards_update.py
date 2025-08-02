from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.shard_status import ShardStatus
from ...types import Response


def _get_kwargs(
    class_name: str,
    shard_name: str,
    *,
    body: ShardStatus,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/schema/{class_name}/shards/{shard_name}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, ShardStatus]]:
    if response.status_code == 200:
        response_200 = ShardStatus.from_dict(response.json())

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
) -> Response[Union[Any, ErrorResponse, ShardStatus]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    class_name: str,
    shard_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ShardStatus,
) -> Response[Union[Any, ErrorResponse, ShardStatus]]:
    """Update a shard status.

     Update a shard status for a collection. For example, a shard may have been marked as `READONLY`
    because its disk was full. After providing more disk space, use this endpoint to set the shard
    status to `READY` again. There is also a convenience function in each client to set the status of
    all shards of a collection.

    Args:
        class_name (str):
        shard_name (str):
        body (ShardStatus): The status of a single shard

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ShardStatus]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        shard_name=shard_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    class_name: str,
    shard_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ShardStatus,
) -> Optional[Union[Any, ErrorResponse, ShardStatus]]:
    """Update a shard status.

     Update a shard status for a collection. For example, a shard may have been marked as `READONLY`
    because its disk was full. After providing more disk space, use this endpoint to set the shard
    status to `READY` again. There is also a convenience function in each client to set the status of
    all shards of a collection.

    Args:
        class_name (str):
        shard_name (str):
        body (ShardStatus): The status of a single shard

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ShardStatus]
    """

    return sync_detailed(
        class_name=class_name,
        shard_name=shard_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    class_name: str,
    shard_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ShardStatus,
) -> Response[Union[Any, ErrorResponse, ShardStatus]]:
    """Update a shard status.

     Update a shard status for a collection. For example, a shard may have been marked as `READONLY`
    because its disk was full. After providing more disk space, use this endpoint to set the shard
    status to `READY` again. There is also a convenience function in each client to set the status of
    all shards of a collection.

    Args:
        class_name (str):
        shard_name (str):
        body (ShardStatus): The status of a single shard

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ShardStatus]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        shard_name=shard_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    class_name: str,
    shard_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ShardStatus,
) -> Optional[Union[Any, ErrorResponse, ShardStatus]]:
    """Update a shard status.

     Update a shard status for a collection. For example, a shard may have been marked as `READONLY`
    because its disk was full. After providing more disk space, use this endpoint to set the shard
    status to `READY` again. There is also a convenience function in each client to set the status of
    all shards of a collection.

    Args:
        class_name (str):
        shard_name (str):
        body (ShardStatus): The status of a single shard

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ShardStatus]
    """

    return (
        await asyncio_detailed(
            class_name=class_name,
            shard_name=shard_name,
            client=client,
            body=body,
        )
    ).parsed
