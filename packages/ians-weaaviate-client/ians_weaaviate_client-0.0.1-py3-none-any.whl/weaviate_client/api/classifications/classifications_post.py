from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.classification import Classification
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    *,
    body: Classification,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/classifications/",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Classification, ErrorResponse]]:
    if response.status_code == 201:
        response_201 = Classification.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, Classification, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Classification,
) -> Response[Union[Any, Classification, ErrorResponse]]:
    """Starts a classification.

     Trigger a classification based on the specified params. Classifications will run in the background,
    use GET /classifications/<id> to retrieve the status of your classification.

    Args:
        body (Classification): Manage classifications, trigger them and view status of past
            classifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Classification, ErrorResponse]]
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
    body: Classification,
) -> Optional[Union[Any, Classification, ErrorResponse]]:
    """Starts a classification.

     Trigger a classification based on the specified params. Classifications will run in the background,
    use GET /classifications/<id> to retrieve the status of your classification.

    Args:
        body (Classification): Manage classifications, trigger them and view status of past
            classifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Classification, ErrorResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Classification,
) -> Response[Union[Any, Classification, ErrorResponse]]:
    """Starts a classification.

     Trigger a classification based on the specified params. Classifications will run in the background,
    use GET /classifications/<id> to retrieve the status of your classification.

    Args:
        body (Classification): Manage classifications, trigger them and view status of past
            classifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Classification, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Classification,
) -> Optional[Union[Any, Classification, ErrorResponse]]:
    """Starts a classification.

     Trigger a classification based on the specified params. Classifications will run in the background,
    use GET /classifications/<id> to retrieve the status of your classification.

    Args:
        body (Classification): Manage classifications, trigger them and view status of past
            classifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Classification, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
