from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.alias import Alias
from ...models.aliases_update_body import AliasesUpdateBody
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    alias_name: str,
    *,
    body: AliasesUpdateBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/aliases/{alias_name}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Alias, Any, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = Alias.from_dict(response.json())

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
) -> Response[Union[Alias, Any, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    alias_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AliasesUpdateBody,
) -> Response[Union[Alias, Any, ErrorResponse]]:
    """Update an alias

     Update an existing alias to point to a different collection (class). This allows you to redirect an
    alias from one collection to another without changing the alias name.

    Args:
        alias_name (str):
        body (AliasesUpdateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Alias, Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        alias_name=alias_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    alias_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AliasesUpdateBody,
) -> Optional[Union[Alias, Any, ErrorResponse]]:
    """Update an alias

     Update an existing alias to point to a different collection (class). This allows you to redirect an
    alias from one collection to another without changing the alias name.

    Args:
        alias_name (str):
        body (AliasesUpdateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Alias, Any, ErrorResponse]
    """

    return sync_detailed(
        alias_name=alias_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    alias_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AliasesUpdateBody,
) -> Response[Union[Alias, Any, ErrorResponse]]:
    """Update an alias

     Update an existing alias to point to a different collection (class). This allows you to redirect an
    alias from one collection to another without changing the alias name.

    Args:
        alias_name (str):
        body (AliasesUpdateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Alias, Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        alias_name=alias_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    alias_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AliasesUpdateBody,
) -> Optional[Union[Alias, Any, ErrorResponse]]:
    """Update an alias

     Update an existing alias to point to a different collection (class). This allows you to redirect an
    alias from one collection to another without changing the alias name.

    Args:
        alias_name (str):
        body (AliasesUpdateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Alias, Any, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            alias_name=alias_name,
            client=client,
            body=body,
        )
    ).parsed
