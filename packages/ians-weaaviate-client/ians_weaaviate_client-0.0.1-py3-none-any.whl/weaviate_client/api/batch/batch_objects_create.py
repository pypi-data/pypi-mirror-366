from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.batch_objects_create_body import BatchObjectsCreateBody
from ...models.error_response import ErrorResponse
from ...models.objects_get_response import ObjectsGetResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BatchObjectsCreateBody,
    consistency_level: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["consistency_level"] = consistency_level

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/batch/objects",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, list["ObjectsGetResponse"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ObjectsGetResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[Any, ErrorResponse, list["ObjectsGetResponse"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchObjectsCreateBody,
    consistency_level: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, list["ObjectsGetResponse"]]]:
    """Creates new Objects based on a Object template as a batch.

     Create new objects in bulk. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note:
    idempotence of `/batch/objects`**: <br/>`POST /batch/objects` is idempotent, and will overwrite any
    existing object given the same id.

    Args:
        consistency_level (Union[Unset, str]):
        body (BatchObjectsCreateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['ObjectsGetResponse']]]
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
    body: BatchObjectsCreateBody,
    consistency_level: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, list["ObjectsGetResponse"]]]:
    """Creates new Objects based on a Object template as a batch.

     Create new objects in bulk. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note:
    idempotence of `/batch/objects`**: <br/>`POST /batch/objects` is idempotent, and will overwrite any
    existing object given the same id.

    Args:
        consistency_level (Union[Unset, str]):
        body (BatchObjectsCreateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['ObjectsGetResponse']]
    """

    return sync_detailed(
        client=client,
        body=body,
        consistency_level=consistency_level,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchObjectsCreateBody,
    consistency_level: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorResponse, list["ObjectsGetResponse"]]]:
    """Creates new Objects based on a Object template as a batch.

     Create new objects in bulk. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note:
    idempotence of `/batch/objects`**: <br/>`POST /batch/objects` is idempotent, and will overwrite any
    existing object given the same id.

    Args:
        consistency_level (Union[Unset, str]):
        body (BatchObjectsCreateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['ObjectsGetResponse']]]
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
    body: BatchObjectsCreateBody,
    consistency_level: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorResponse, list["ObjectsGetResponse"]]]:
    """Creates new Objects based on a Object template as a batch.

     Create new objects in bulk. <br/><br/>Meta-data and schema values are validated. <br/><br/>**Note:
    idempotence of `/batch/objects`**: <br/>`POST /batch/objects` is idempotent, and will overwrite any
    existing object given the same id.

    Args:
        consistency_level (Union[Unset, str]):
        body (BatchObjectsCreateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['ObjectsGetResponse']]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            consistency_level=consistency_level,
        )
    ).parsed
