from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.db_user_info import DBUserInfo
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    *,
    include_last_used_time: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["includeLastUsedTime"] = include_last_used_time

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/users/db/{user_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, DBUserInfo, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = DBUserInfo.from_dict(response.json())

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
) -> Response[Union[Any, DBUserInfo, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_last_used_time: Union[Unset, bool] = False,
) -> Response[Union[Any, DBUserInfo, ErrorResponse]]:
    """get info relevant to user, e.g. username, roles

    Args:
        user_id (str):
        include_last_used_time (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DBUserInfo, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        include_last_used_time=include_last_used_time,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_last_used_time: Union[Unset, bool] = False,
) -> Optional[Union[Any, DBUserInfo, ErrorResponse]]:
    """get info relevant to user, e.g. username, roles

    Args:
        user_id (str):
        include_last_used_time (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DBUserInfo, ErrorResponse]
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        include_last_used_time=include_last_used_time,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_last_used_time: Union[Unset, bool] = False,
) -> Response[Union[Any, DBUserInfo, ErrorResponse]]:
    """get info relevant to user, e.g. username, roles

    Args:
        user_id (str):
        include_last_used_time (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DBUserInfo, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        include_last_used_time=include_last_used_time,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_last_used_time: Union[Unset, bool] = False,
) -> Optional[Union[Any, DBUserInfo, ErrorResponse]]:
    """get info relevant to user, e.g. username, roles

    Args:
        user_id (str):
        include_last_used_time (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DBUserInfo, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            include_last_used_time=include_last_used_time,
        )
    ).parsed
