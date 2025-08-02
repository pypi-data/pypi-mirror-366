from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.graph_ql_query import GraphQLQuery
from ...models.graph_ql_response import GraphQLResponse
from ...types import Response


def _get_kwargs(
    *,
    body: list["GraphQLQuery"],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/graphql/batch",
    }

    _kwargs["json"] = []
    for componentsschemas_graph_ql_queries_item_data in body:
        componentsschemas_graph_ql_queries_item = componentsschemas_graph_ql_queries_item_data.to_dict()
        _kwargs["json"].append(componentsschemas_graph_ql_queries_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, list["GraphQLResponse"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_graph_ql_responses_item_data in _response_200:
            componentsschemas_graph_ql_responses_item = GraphQLResponse.from_dict(
                componentsschemas_graph_ql_responses_item_data
            )

            response_200.append(componentsschemas_graph_ql_responses_item)

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
) -> Response[Union[Any, ErrorResponse, list["GraphQLResponse"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["GraphQLQuery"],
) -> Response[Union[Any, ErrorResponse, list["GraphQLResponse"]]]:
    """Get a response based on GraphQL.

     Perform a batched GraphQL query

    Args:
        body (list['GraphQLQuery']): A list of GraphQL queries.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['GraphQLResponse']]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["GraphQLQuery"],
) -> Optional[Union[Any, ErrorResponse, list["GraphQLResponse"]]]:
    """Get a response based on GraphQL.

     Perform a batched GraphQL query

    Args:
        body (list['GraphQLQuery']): A list of GraphQL queries.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['GraphQLResponse']]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["GraphQLQuery"],
) -> Response[Union[Any, ErrorResponse, list["GraphQLResponse"]]]:
    """Get a response based on GraphQL.

     Perform a batched GraphQL query

    Args:
        body (list['GraphQLQuery']): A list of GraphQL queries.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, list['GraphQLResponse']]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["GraphQLQuery"],
) -> Optional[Union[Any, ErrorResponse, list["GraphQLResponse"]]]:
    """Get a response based on GraphQL.

     Perform a batched GraphQL query

    Args:
        body (list['GraphQLQuery']): A list of GraphQL queries.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, list['GraphQLResponse']]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
