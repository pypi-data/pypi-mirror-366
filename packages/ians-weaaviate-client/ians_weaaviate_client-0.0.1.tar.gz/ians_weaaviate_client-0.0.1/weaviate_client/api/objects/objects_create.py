from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.object_ import Object
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["consistency_level"] = consistency_level

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/objects",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, Object]]:
    """Create a new object.

     Create a new object. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note: Use
    `/batch` for importing many objects**: <br/>If you plan on importing a large number of objects, it's
    much more efficient to use the `/batch` endpoint. Otherwise, sending multiple single requests
    sequentially would incur a large performance penalty. <br/><br/>**Note: idempotence of `/objects`**:
    <br/>POST /objects will fail if an id is provided which already exists in the class. To update an
    existing object with the objects endpoint, use the PUT or PATCH method.

    Args:
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, Object]]
    """

    kwargs = _get_kwargs(
        body=body,
        consistency_level=consistency_level,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, Object]]:
    """Create a new object.

     Create a new object. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note: Use
    `/batch` for importing many objects**: <br/>If you plan on importing a large number of objects, it's
    much more efficient to use the `/batch` endpoint. Otherwise, sending multiple single requests
    sequentially would incur a large performance penalty. <br/><br/>**Note: idempotence of `/objects`**:
    <br/>POST /objects will fail if an id is provided which already exists in the class. To update an
    existing object with the objects endpoint, use the PUT or PATCH method.

    Args:
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, Object]
    """

    return sync_detailed(
        client=client,
        body=body,
        consistency_level=consistency_level,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, Object]]:
    """Create a new object.

     Create a new object. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note: Use
    `/batch` for importing many objects**: <br/>If you plan on importing a large number of objects, it's
    much more efficient to use the `/batch` endpoint. Otherwise, sending multiple single requests
    sequentially would incur a large performance penalty. <br/><br/>**Note: idempotence of `/objects`**:
    <br/>POST /objects will fail if an id is provided which already exists in the class. To update an
    existing object with the objects endpoint, use the PUT or PATCH method.

    Args:
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, Object]]
    """

    kwargs = _get_kwargs(
        body=body,
        consistency_level=consistency_level,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Object,
    consistency_level: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, Object]]:
    """Create a new object.

     Create a new object. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note: Use
    `/batch` for importing many objects**: <br/>If you plan on importing a large number of objects, it's
    much more efficient to use the `/batch` endpoint. Otherwise, sending multiple single requests
    sequentially would incur a large performance penalty. <br/><br/>**Note: idempotence of `/objects`**:
    <br/>POST /objects will fail if an id is provided which already exists in the class. To update an
    existing object with the objects endpoint, use the PUT or PATCH method.

    Args:
        consistency_level (Union[Unset, str]):
        body (Object):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, Object]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            consistency_level=consistency_level,
        )
    ).parsed
