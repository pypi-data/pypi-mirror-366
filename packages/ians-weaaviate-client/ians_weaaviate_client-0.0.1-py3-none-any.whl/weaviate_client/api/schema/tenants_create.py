from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.tenant import Tenant
from ...types import Response


def _get_kwargs(
    class_name: str,
    *,
    body: list["Tenant"],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/schema/{class_name}/tenants",
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, list["Tenant"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Tenant.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
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
) -> Response[Union[Any, ErrorResponse, list["Tenant"]]]:
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
    body: list["Tenant"],
) -> Response[Union[Any, ErrorResponse, list["Tenant"]]]:
    """Create a new tenant

     Create a new tenant for a collection. Multi-tenancy must be enabled in the collection definition.

    Args:
        class_name (str):
        body (list['Tenant']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['Tenant']]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    class_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["Tenant"],
) -> Optional[Union[Any, ErrorResponse, list["Tenant"]]]:
    """Create a new tenant

     Create a new tenant for a collection. Multi-tenancy must be enabled in the collection definition.

    Args:
        class_name (str):
        body (list['Tenant']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['Tenant']]
    """

    return sync_detailed(
        class_name=class_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    class_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["Tenant"],
) -> Response[Union[Any, ErrorResponse, list["Tenant"]]]:
    """Create a new tenant

     Create a new tenant for a collection. Multi-tenancy must be enabled in the collection definition.

    Args:
        class_name (str):
        body (list['Tenant']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['Tenant']]]
    """

    kwargs = _get_kwargs(
        class_name=class_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    class_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["Tenant"],
) -> Optional[Union[Any, ErrorResponse, list["Tenant"]]]:
    """Create a new tenant

     Create a new tenant for a collection. Multi-tenancy must be enabled in the collection definition.

    Args:
        class_name (str):
        body (list['Tenant']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['Tenant']]
    """

    return (
        await asyncio_detailed(
            class_name=class_name,
            client=client,
            body=body,
        )
    ).parsed
