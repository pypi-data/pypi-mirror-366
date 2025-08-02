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
    id: UUID,
    *,
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["consistency_level"] = consistency_level

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/objects/{id}",
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
    if response.status_code == 400:
        response_400 = cast(Any, None)
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
) -> Response[Union[Any, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse]]:
    """Update an Object based on its UUID (using patch semantics).

     Update an object based on its UUID (using patch semantics). This method supports json-merge style
    patch semantics (RFC 7396). Provided meta-data and schema values are validated. LastUpdateTime is
    set to the time this function is called. <br/><br/>**Note**: This endpoint is deprecated and will be
    removed in a future version. Use the `/objects/{className}/{id}` endpoint instead.

    Args:
        id (UUID):
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        consistency_level=consistency_level,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse]]:
    """Update an Object based on its UUID (using patch semantics).

     Update an object based on its UUID (using patch semantics). This method supports json-merge style
    patch semantics (RFC 7396). Provided meta-data and schema values are validated. LastUpdateTime is
    set to the time this function is called. <br/><br/>**Note**: This endpoint is deprecated and will be
    removed in a future version. Use the `/objects/{className}/{id}` endpoint instead.

    Args:
        id (UUID):
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse]
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
        consistency_level=consistency_level,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse]]:
    """Update an Object based on its UUID (using patch semantics).

     Update an object based on its UUID (using patch semantics). This method supports json-merge style
    patch semantics (RFC 7396). Provided meta-data and schema values are validated. LastUpdateTime is
    set to the time this function is called. <br/><br/>**Note**: This endpoint is deprecated and will be
    removed in a future version. Use the `/objects/{className}/{id}` endpoint instead.

    Args:
        id (UUID):
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        consistency_level=consistency_level,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse]]:
    """Update an Object based on its UUID (using patch semantics).

     Update an object based on its UUID (using patch semantics). This method supports json-merge style
    patch semantics (RFC 7396). Provided meta-data and schema values are validated. LastUpdateTime is
    set to the time this function is called. <br/><br/>**Note**: This endpoint is deprecated and will be
    removed in a future version. Use the `/objects/{className}/{id}` endpoint instead.

    Args:
        id (UUID):
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
            consistency_level=consistency_level,
        )
    ).parsed
