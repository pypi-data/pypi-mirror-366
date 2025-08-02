from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.replication_replicate_force_delete_request import ReplicationReplicateForceDeleteRequest
from ...models.replication_replicate_force_delete_response import ReplicationReplicateForceDeleteResponse
from ...types import Response


def _get_kwargs(
    *,
    body: ReplicationReplicateForceDeleteRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/replication/replicate/force-delete",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]:
    if response.status_code == 200:
        response_200 = ReplicationReplicateForceDeleteResponse.from_dict(response.json())

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
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReplicationReplicateForceDeleteRequest,
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]:
    """Force delete replication operations

     USE AT OWN RISK! Synchronously force delete operations from the FSM. This will not perform any
    checks on which state the operation is in so may lead to data corruption or loss. It is recommended
    to first scale the number of replication engine workers to 0 before calling this endpoint to ensure
    no operations are in-flight.

    Args:
        body (ReplicationReplicateForceDeleteRequest): Specifies the parameters available when
            force deleting replication operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]
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
    body: ReplicationReplicateForceDeleteRequest,
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]:
    """Force delete replication operations

     USE AT OWN RISK! Synchronously force delete operations from the FSM. This will not perform any
    checks on which state the operation is in so may lead to data corruption or loss. It is recommended
    to first scale the number of replication engine workers to 0 before calling this endpoint to ensure
    no operations are in-flight.

    Args:
        body (ReplicationReplicateForceDeleteRequest): Specifies the parameters available when
            force deleting replication operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReplicationReplicateForceDeleteRequest,
) -> Response[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]:
    """Force delete replication operations

     USE AT OWN RISK! Synchronously force delete operations from the FSM. This will not perform any
    checks on which state the operation is in so may lead to data corruption or loss. It is recommended
    to first scale the number of replication engine workers to 0 before calling this endpoint to ensure
    no operations are in-flight.

    Args:
        body (ReplicationReplicateForceDeleteRequest): Specifies the parameters available when
            force deleting replication operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReplicationReplicateForceDeleteRequest,
) -> Optional[Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]]:
    """Force delete replication operations

     USE AT OWN RISK! Synchronously force delete operations from the FSM. This will not perform any
    checks on which state the operation is in so may lead to data corruption or loss. It is recommended
    to first scale the number of replication engine workers to 0 before calling this endpoint to ensure
    no operations are in-flight.

    Args:
        body (ReplicationReplicateForceDeleteRequest): Specifies the parameters available when
            force deleting replication operations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ReplicationReplicateForceDeleteResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
