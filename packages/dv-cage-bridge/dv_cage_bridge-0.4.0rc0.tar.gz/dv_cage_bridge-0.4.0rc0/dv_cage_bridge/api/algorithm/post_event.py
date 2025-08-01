from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_event_body import PostEventBody
from ...models.post_event_response_200 import PostEventResponse200
from ...models.post_event_response_400 import PostEventResponse400
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PostEventBody,
    stream: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["stream"] = stream

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/event",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[PostEventResponse200, PostEventResponse400]]:
    if response.status_code == 200:
        response_200 = PostEventResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = PostEventResponse400.from_dict(response.json())

        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[PostEventResponse200, PostEventResponse400]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostEventBody,
    stream: Union[Unset, str] = UNSET,
) -> Response[Union[PostEventResponse200, PostEventResponse400]]:
    """Publish an event

     Publishes a new event in the redis queue.

    Args:
        stream (Union[Unset, str]):
        body (PostEventBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostEventResponse200, PostEventResponse400]]
    """

    kwargs = _get_kwargs(
        body=body,
        stream=stream,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostEventBody,
    stream: Union[Unset, str] = UNSET,
) -> Optional[Union[PostEventResponse200, PostEventResponse400]]:
    """Publish an event

     Publishes a new event in the redis queue.

    Args:
        stream (Union[Unset, str]):
        body (PostEventBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostEventResponse200, PostEventResponse400]
    """

    return sync_detailed(
        client=client,
        body=body,
        stream=stream,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostEventBody,
    stream: Union[Unset, str] = UNSET,
) -> Response[Union[PostEventResponse200, PostEventResponse400]]:
    """Publish an event

     Publishes a new event in the redis queue.

    Args:
        stream (Union[Unset, str]):
        body (PostEventBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PostEventResponse200, PostEventResponse400]]
    """

    kwargs = _get_kwargs(
        body=body,
        stream=stream,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PostEventBody,
    stream: Union[Unset, str] = UNSET,
) -> Optional[Union[PostEventResponse200, PostEventResponse400]]:
    """Publish an event

     Publishes a new event in the redis queue.

    Args:
        stream (Union[Unset, str]):
        body (PostEventBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PostEventResponse200, PostEventResponse400]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            stream=stream,
        )
    ).parsed
