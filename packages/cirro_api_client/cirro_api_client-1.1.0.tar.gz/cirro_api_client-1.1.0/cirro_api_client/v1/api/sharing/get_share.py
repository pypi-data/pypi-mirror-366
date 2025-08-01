from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.share_detail import ShareDetail
from ...types import Response


def _get_kwargs(
    project_id: str,
    share_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/projects/{project_id}/shares/{share_id}",
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[ShareDetail]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ShareDetail.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[ShareDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    share_id: str,
    *,
    client: Client,
) -> Response[ShareDetail]:
    """Get share

     Get details on a share that you've published or subscribed to

    Args:
        project_id (str):
        share_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ShareDetail]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        share_id=share_id,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    share_id: str,
    *,
    client: Client,
) -> Optional[ShareDetail]:
    """Get share

     Get details on a share that you've published or subscribed to

    Args:
        project_id (str):
        share_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ShareDetail
    """

    try:
        return sync_detailed(
            project_id=project_id,
            share_id=share_id,
            client=client,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    project_id: str,
    share_id: str,
    *,
    client: Client,
) -> Response[ShareDetail]:
    """Get share

     Get details on a share that you've published or subscribed to

    Args:
        project_id (str):
        share_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ShareDetail]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        share_id=share_id,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    share_id: str,
    *,
    client: Client,
) -> Optional[ShareDetail]:
    """Get share

     Get details on a share that you've published or subscribed to

    Args:
        project_id (str):
        share_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ShareDetail
    """

    try:
        return (
            await asyncio_detailed(
                project_id=project_id,
                share_id=share_id,
                client=client,
            )
        ).parsed
    except errors.NotFoundException:
        return None
