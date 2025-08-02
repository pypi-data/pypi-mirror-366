from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.replication_replicate_replica_request import ReplicationReplicateReplicaRequest
from ...models.replication_replicate_replica_response import ReplicationReplicateReplicaResponse
from ...types import Response


def _get_kwargs(
    *,
    body: ReplicationReplicateReplicaRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/replication/replicate",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]:
    if response.status_code == 200:
        response_200 = ReplicationReplicateReplicaResponse.from_dict(response.json())

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
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReplicationReplicateReplicaRequest,
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]:
    """Initiate a replica movement

     Begins an asynchronous operation to move or copy a specific shard replica from its current node to a
    designated target node. The operation involves copying data, synchronizing, and potentially
    decommissioning the source replica.

    Args:
        body (ReplicationReplicateReplicaRequest): Specifies the parameters required to initiate a
            shard replica movement operation between two nodes for a given collection and shard. This
            request defines the source and target node, the collection and type of transfer.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReplicationReplicateReplicaRequest,
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]:
    """Initiate a replica movement

     Begins an asynchronous operation to move or copy a specific shard replica from its current node to a
    designated target node. The operation involves copying data, synchronizing, and potentially
    decommissioning the source replica.

    Args:
        body (ReplicationReplicateReplicaRequest): Specifies the parameters required to initiate a
            shard replica movement operation between two nodes for a given collection and shard. This
            request defines the source and target node, the collection and type of transfer.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReplicationReplicateReplicaRequest,
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]:
    """Initiate a replica movement

     Begins an asynchronous operation to move or copy a specific shard replica from its current node to a
    designated target node. The operation involves copying data, synchronizing, and potentially
    decommissioning the source replica.

    Args:
        body (ReplicationReplicateReplicaRequest): Specifies the parameters required to initiate a
            shard replica movement operation between two nodes for a given collection and shard. This
            request defines the source and target node, the collection and type of transfer.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReplicationReplicateReplicaRequest,
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]]:
    """Initiate a replica movement

     Begins an asynchronous operation to move or copy a specific shard replica from its current node to a
    designated target node. The operation involves copying data, synchronizing, and potentially
    decommissioning the source replica.

    Args:
        body (ReplicationReplicateReplicaRequest): Specifies the parameters required to initiate a
            shard replica movement operation between two nodes for a given collection and shard. This
            request defines the source and target node, the collection and type of transfer.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationReplicateReplicaResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
