from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.object_ import Object
from ...types import UNSET, Response, Unset


def _get_kwargs(
    class_name: str,
    id: UUID,
    *,
    include: Union[Unset, str] = UNSET,
    consistency_level: Union[Unset, str] = UNSET,
    node_name: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include"] = include

    params["consistency_level"] = consistency_level

    params["node_name"] = node_name

    params["tenant"] = tenant

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/objects/{class_name}/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, Object]]:
    if response.status_code == 200:
        response_200 = Object.from_dict(response.json())

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
        response_404 = cast(Any, None)
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
) -> Response[Union[Any, ErrorResponse, Object]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    class_name: str,
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include: Union[Unset, str] = UNSET,
    consistency_level: Union[Unset, str] = UNSET,
    node_name: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, Object]]:
    """Get a specific Object based on its class and UUID. Also available as Websocket bus.

     Get a data object based on its collection and UUID.

    Args:
        class_name (str):
        id (UUID):
        include (Union[Unset, str]):
        consistency_level (Union[Unset, str]):
        node_name (Union[Unset, str]):
        tenant (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, Object]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        id=id,
        include=include,
        consistency_level=consistency_level,
        node_name=node_name,
        tenant=tenant,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    class_name: str,
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include: Union[Unset, str] = UNSET,
    consistency_level: Union[Unset, str] = UNSET,
    node_name: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, Object]]:
    """Get a specific Object based on its class and UUID. Also available as Websocket bus.

     Get a data object based on its collection and UUID.

    Args:
        class_name (str):
        id (UUID):
        include (Union[Unset, str]):
        consistency_level (Union[Unset, str]):
        node_name (Union[Unset, str]):
        tenant (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, Object]
    """

    return sync_detailed(
        class_name=class_name,
        id=id,
        client=client,
        include=include,
        consistency_level=consistency_level,
        node_name=node_name,
        tenant=tenant,
    ).parsed


async def asyncio_detailed(
    class_name: str,
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include: Union[Unset, str] = UNSET,
    consistency_level: Union[Unset, str] = UNSET,
    node_name: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, Object]]:
    """Get a specific Object based on its class and UUID. Also available as Websocket bus.

     Get a data object based on its collection and UUID.

    Args:
        class_name (str):
        id (UUID):
        include (Union[Unset, str]):
        consistency_level (Union[Unset, str]):
        node_name (Union[Unset, str]):
        tenant (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, Object]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        id=id,
        include=include,
        consistency_level=consistency_level,
        node_name=node_name,
        tenant=tenant,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    class_name: str,
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    include: Union[Unset, str] = UNSET,
    consistency_level: Union[Unset, str] = UNSET,
    node_name: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, Object]]:
    """Get a specific Object based on its class and UUID. Also available as Websocket bus.

     Get a data object based on its collection and UUID.

    Args:
        class_name (str):
        id (UUID):
        include (Union[Unset, str]):
        consistency_level (Union[Unset, str]):
        node_name (Union[Unset, str]):
        tenant (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, Object]
    """

    return (
        await asyncio_detailed(
            class_name=class_name,
            id=id,
            client=client,
            include=include,
            consistency_level=consistency_level,
            node_name=node_name,
            tenant=tenant,
        )
    ).parsed
