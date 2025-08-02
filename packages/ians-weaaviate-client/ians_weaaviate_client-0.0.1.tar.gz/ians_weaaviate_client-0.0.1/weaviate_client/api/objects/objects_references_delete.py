from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.single_ref import SingleRef
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID,
    property_name: str,
    *,
    body: SingleRef,
    tenant: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["tenant"] = tenant

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/objects/{id}/references/{property_name}",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
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
    id: UUID,
    property_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SingleRef,
    tenant: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse]]:
    """Delete a single reference from the list of references.

     Delete the single reference that is given in the body from the list of references that this property
    has. <br/><br/>**Note**: This endpoint is deprecated and will be removed in a future version. Use
    the `/objects/{className}/{id}/references/{propertyName}` endpoint instead.

    Args:
        id (UUID):
        property_name (str):
        tenant (Union[Unset, str]):
        body (SingleRef): Either set beacon (direct reference) or set class and schema (concept
            reference)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        property_name=property_name,
        body=body,
        tenant=tenant,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    property_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SingleRef,
    tenant: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse]]:
    """Delete a single reference from the list of references.

     Delete the single reference that is given in the body from the list of references that this property
    has. <br/><br/>**Note**: This endpoint is deprecated and will be removed in a future version. Use
    the `/objects/{className}/{id}/references/{propertyName}` endpoint instead.

    Args:
        id (UUID):
        property_name (str):
        tenant (Union[Unset, str]):
        body (SingleRef): Either set beacon (direct reference) or set class and schema (concept
            reference)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse]
    """

    return sync_detailed(
        id=id,
        property_name=property_name,
        client=client,
        body=body,
        tenant=tenant,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    property_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SingleRef,
    tenant: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse]]:
    """Delete a single reference from the list of references.

     Delete the single reference that is given in the body from the list of references that this property
    has. <br/><br/>**Note**: This endpoint is deprecated and will be removed in a future version. Use
    the `/objects/{className}/{id}/references/{propertyName}` endpoint instead.

    Args:
        id (UUID):
        property_name (str):
        tenant (Union[Unset, str]):
        body (SingleRef): Either set beacon (direct reference) or set class and schema (concept
            reference)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        property_name=property_name,
        body=body,
        tenant=tenant,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    property_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SingleRef,
    tenant: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse]]:
    """Delete a single reference from the list of references.

     Delete the single reference that is given in the body from the list of references that this property
    has. <br/><br/>**Note**: This endpoint is deprecated and will be removed in a future version. Use
    the `/objects/{className}/{id}/references/{propertyName}` endpoint instead.

    Args:
        id (UUID):
        property_name (str):
        tenant (Union[Unset, str]):
        body (SingleRef): Either set beacon (direct reference) or set class and schema (concept
            reference)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            id=id,
            property_name=property_name,
            client=client,
            body=body,
            tenant=tenant,
        )
    ).parsed
