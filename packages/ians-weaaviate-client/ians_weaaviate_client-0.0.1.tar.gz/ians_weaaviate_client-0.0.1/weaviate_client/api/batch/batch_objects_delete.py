from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.batch_delete import BatchDelete
from ...models.batch_delete_response import BatchDeleteResponse
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BatchDelete,
    consistency_level: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["consistency_level"] = consistency_level

    params["tenant"] = tenant

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/batch/objects",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, BatchDeleteResponse, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = BatchDeleteResponse.from_dict(response.json())

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
) -> Response[Union[Any, BatchDeleteResponse, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchDelete,
    consistency_level: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Response[Union[Any, BatchDeleteResponse, ErrorResponse]]:
    """Deletes Objects based on a match filter as a batch.

     Batch delete objects that match a particular filter. <br/><br/>The request body takes a single
    `where` filter and will delete all objects matched. <br/><br/>Note that there is a limit to the
    number of objects to be deleted at once using this filter, in order to protect against unexpected
    memory surges and very-long-running requests. The default limit is 10,000 and may be configured by
    setting the `QUERY_MAXIMUM_RESULTS` environment variable. <br/><br/>Objects are deleted in the same
    order that they would be returned in an equivalent Get query. To delete more objects than the limit,
    run the same query multiple times.

    Args:
        consistency_level (Union[Unset, str]):
        tenant (Union[Unset, str]):
        body (BatchDelete):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BatchDeleteResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        consistency_level=consistency_level,
        tenant=tenant,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchDelete,
    consistency_level: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, BatchDeleteResponse, ErrorResponse]]:
    """Deletes Objects based on a match filter as a batch.

     Batch delete objects that match a particular filter. <br/><br/>The request body takes a single
    `where` filter and will delete all objects matched. <br/><br/>Note that there is a limit to the
    number of objects to be deleted at once using this filter, in order to protect against unexpected
    memory surges and very-long-running requests. The default limit is 10,000 and may be configured by
    setting the `QUERY_MAXIMUM_RESULTS` environment variable. <br/><br/>Objects are deleted in the same
    order that they would be returned in an equivalent Get query. To delete more objects than the limit,
    run the same query multiple times.

    Args:
        consistency_level (Union[Unset, str]):
        tenant (Union[Unset, str]):
        body (BatchDelete):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BatchDeleteResponse, ErrorResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
        consistency_level=consistency_level,
        tenant=tenant,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchDelete,
    consistency_level: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Response[Union[Any, BatchDeleteResponse, ErrorResponse]]:
    """Deletes Objects based on a match filter as a batch.

     Batch delete objects that match a particular filter. <br/><br/>The request body takes a single
    `where` filter and will delete all objects matched. <br/><br/>Note that there is a limit to the
    number of objects to be deleted at once using this filter, in order to protect against unexpected
    memory surges and very-long-running requests. The default limit is 10,000 and may be configured by
    setting the `QUERY_MAXIMUM_RESULTS` environment variable. <br/><br/>Objects are deleted in the same
    order that they would be returned in an equivalent Get query. To delete more objects than the limit,
    run the same query multiple times.

    Args:
        consistency_level (Union[Unset, str]):
        tenant (Union[Unset, str]):
        body (BatchDelete):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BatchDeleteResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        consistency_level=consistency_level,
        tenant=tenant,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchDelete,
    consistency_level: Union[Unset, str] = UNSET,
    tenant: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, BatchDeleteResponse, ErrorResponse]]:
    """Deletes Objects based on a match filter as a batch.

     Batch delete objects that match a particular filter. <br/><br/>The request body takes a single
    `where` filter and will delete all objects matched. <br/><br/>Note that there is a limit to the
    number of objects to be deleted at once using this filter, in order to protect against unexpected
    memory surges and very-long-running requests. The default limit is 10,000 and may be configured by
    setting the `QUERY_MAXIMUM_RESULTS` environment variable. <br/><br/>Objects are deleted in the same
    order that they would be returned in an equivalent Get query. To delete more objects than the limit,
    run the same query multiple times.

    Args:
        consistency_level (Union[Unset, str]):
        tenant (Union[Unset, str]):
        body (BatchDelete):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BatchDeleteResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            consistency_level=consistency_level,
            tenant=tenant,
        )
    ).parsed
