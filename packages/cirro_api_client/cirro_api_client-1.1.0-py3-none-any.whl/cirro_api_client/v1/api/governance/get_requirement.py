from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.governance_requirement import GovernanceRequirement
from ...types import Response


def _get_kwargs(
    requirement_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/governance/requirements/{requirement_id}",
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[GovernanceRequirement]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GovernanceRequirement.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[GovernanceRequirement]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    requirement_id: str,
    *,
    client: Client,
) -> Response[GovernanceRequirement]:
    """Get a requirement

     Retrieve a governance requirement

    Args:
        requirement_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GovernanceRequirement]
    """

    kwargs = _get_kwargs(
        requirement_id=requirement_id,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    requirement_id: str,
    *,
    client: Client,
) -> Optional[GovernanceRequirement]:
    """Get a requirement

     Retrieve a governance requirement

    Args:
        requirement_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GovernanceRequirement
    """

    try:
        return sync_detailed(
            requirement_id=requirement_id,
            client=client,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    requirement_id: str,
    *,
    client: Client,
) -> Response[GovernanceRequirement]:
    """Get a requirement

     Retrieve a governance requirement

    Args:
        requirement_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GovernanceRequirement]
    """

    kwargs = _get_kwargs(
        requirement_id=requirement_id,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    requirement_id: str,
    *,
    client: Client,
) -> Optional[GovernanceRequirement]:
    """Get a requirement

     Retrieve a governance requirement

    Args:
        requirement_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GovernanceRequirement
    """

    try:
        return (
            await asyncio_detailed(
                requirement_id=requirement_id,
                client=client,
            )
        ).parsed
    except errors.NotFoundException:
        return None
