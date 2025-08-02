from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.nodes_status_response import NodesStatusResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    class_name: str,
    *,
    shard_name: Union[Unset, str] = UNSET,
    output: Union[Unset, str] = "minimal",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["shardName"] = shard_name

    params["output"] = output

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/nodes/{class_name}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, NodesStatusResponse]]:
    if response.status_code == 200:
        response_200 = NodesStatusResponse.from_dict(response.json())

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
) -> Response[Union[Any, ErrorResponse, NodesStatusResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    class_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    shard_name: Union[Unset, str] = UNSET,
    output: Union[Unset, str] = "minimal",
) -> Response[Union[Any, ErrorResponse, NodesStatusResponse]]:
    """Node information for a collection.

     Returns node information for the nodes relevant to the collection.

    Args:
        class_name (str):
        shard_name (Union[Unset, str]):
        output (Union[Unset, str]):  Default: 'minimal'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, NodesStatusResponse]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        shard_name=shard_name,
        output=output,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    class_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    shard_name: Union[Unset, str] = UNSET,
    output: Union[Unset, str] = "minimal",
) -> Optional[Union[Any, ErrorResponse, NodesStatusResponse]]:
    """Node information for a collection.

     Returns node information for the nodes relevant to the collection.

    Args:
        class_name (str):
        shard_name (Union[Unset, str]):
        output (Union[Unset, str]):  Default: 'minimal'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, NodesStatusResponse]
    """

    return sync_detailed(
        class_name=class_name,
        client=client,
        shard_name=shard_name,
        output=output,
    ).parsed


async def asyncio_detailed(
    class_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    shard_name: Union[Unset, str] = UNSET,
    output: Union[Unset, str] = "minimal",
) -> Response[Union[Any, ErrorResponse, NodesStatusResponse]]:
    """Node information for a collection.

     Returns node information for the nodes relevant to the collection.

    Args:
        class_name (str):
        shard_name (Union[Unset, str]):
        output (Union[Unset, str]):  Default: 'minimal'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, NodesStatusResponse]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        shard_name=shard_name,
        output=output,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    class_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    shard_name: Union[Unset, str] = UNSET,
    output: Union[Unset, str] = "minimal",
) -> Optional[Union[Any, ErrorResponse, NodesStatusResponse]]:
    """Node information for a collection.

     Returns node information for the nodes relevant to the collection.

    Args:
        class_name (str):
        shard_name (Union[Unset, str]):
        output (Union[Unset, str]):  Default: 'minimal'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, NodesStatusResponse]
    """

    return (
        await asyncio_detailed(
            class_name=class_name,
            client=client,
            shard_name=shard_name,
            output=output,
        )
    ).parsed
