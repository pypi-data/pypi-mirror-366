from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import Response, Unset


def _get_kwargs(
    class_name: str,
    tenant_name: str,
    *,
    consistency: Union[Unset, bool] = True,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(consistency, Unset):
        headers["consistency"] = "true" if consistency else "false"

    _kwargs: dict[str, Any] = {
        "method": "head",
        "url": f"/schema/{class_name}/tenants/{tenant_name}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    class_name: str,
    tenant_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    consistency: Union[Unset, bool] = True,
) -> Response[Union[Any, ErrorResponse]]:
    """Check whether a tenant exists

     Check if a tenant exists for a specific class

    Args:
        class_name (str):
        tenant_name (str):
        consistency (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        tenant_name=tenant_name,
        consistency=consistency,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    class_name: str,
    tenant_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    consistency: Union[Unset, bool] = True,
) -> Optional[Union[Any, ErrorResponse]]:
    """Check whether a tenant exists

     Check if a tenant exists for a specific class

    Args:
        class_name (str):
        tenant_name (str):
        consistency (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse]
    """

    return sync_detailed(
        class_name=class_name,
        tenant_name=tenant_name,
        client=client,
        consistency=consistency,
    ).parsed


async def asyncio_detailed(
    class_name: str,
    tenant_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    consistency: Union[Unset, bool] = True,
) -> Response[Union[Any, ErrorResponse]]:
    """Check whether a tenant exists

     Check if a tenant exists for a specific class

    Args:
        class_name (str):
        tenant_name (str):
        consistency (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        tenant_name=tenant_name,
        consistency=consistency,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    class_name: str,
    tenant_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    consistency: Union[Unset, bool] = True,
) -> Optional[Union[Any, ErrorResponse]]:
    """Check whether a tenant exists

     Check if a tenant exists for a specific class

    Args:
        class_name (str):
        tenant_name (str):
        consistency (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            class_name=class_name,
            tenant_name=tenant_name,
            client=client,
            consistency=consistency,
        )
    ).parsed
