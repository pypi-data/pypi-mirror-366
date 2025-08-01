from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.entity_type import EntityType
from ...models.paginated_response_discussion import PaginatedResponseDiscussion
from ...models.sort_order import SortOrder
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    entity_type: EntityType,
    entity_id: str,
    next_token: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 5000,
    order: Union[None, SortOrder, Unset] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_entity_type = entity_type.value
    params["entityType"] = json_entity_type

    params["entityId"] = entity_id

    json_next_token: Union[None, Unset, str]
    if isinstance(next_token, Unset):
        json_next_token = UNSET
    else:
        json_next_token = next_token
    params["nextToken"] = json_next_token

    params["limit"] = limit

    json_order: Union[None, Unset, str]
    if isinstance(order, Unset):
        json_order = UNSET
    elif isinstance(order, SortOrder):
        json_order = order.value
    else:
        json_order = order
    params["order"] = json_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/discussions",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[PaginatedResponseDiscussion]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PaginatedResponseDiscussion.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[PaginatedResponseDiscussion]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entity_type: EntityType,
    entity_id: str,
    next_token: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 5000,
    order: Union[None, SortOrder, Unset] = UNSET,
) -> Response[PaginatedResponseDiscussion]:
    """Get discussions for an entity

     Retrieves a paginated list of discussions for a specific entity type and ID

    Args:
        entity_type (EntityType):
        entity_id (str):
        next_token (Union[None, Unset, str]):
        limit (Union[Unset, int]):  Default: 5000.
        order (Union[None, SortOrder, Unset]):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedResponseDiscussion]
    """

    kwargs = _get_kwargs(
        entity_type=entity_type,
        entity_id=entity_id,
        next_token=next_token,
        limit=limit,
        order=order,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    entity_type: EntityType,
    entity_id: str,
    next_token: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 5000,
    order: Union[None, SortOrder, Unset] = UNSET,
) -> Optional[PaginatedResponseDiscussion]:
    """Get discussions for an entity

     Retrieves a paginated list of discussions for a specific entity type and ID

    Args:
        entity_type (EntityType):
        entity_id (str):
        next_token (Union[None, Unset, str]):
        limit (Union[Unset, int]):  Default: 5000.
        order (Union[None, SortOrder, Unset]):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedResponseDiscussion
    """

    try:
        return sync_detailed(
            client=client,
            entity_type=entity_type,
            entity_id=entity_id,
            next_token=next_token,
            limit=limit,
            order=order,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    *,
    client: Client,
    entity_type: EntityType,
    entity_id: str,
    next_token: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 5000,
    order: Union[None, SortOrder, Unset] = UNSET,
) -> Response[PaginatedResponseDiscussion]:
    """Get discussions for an entity

     Retrieves a paginated list of discussions for a specific entity type and ID

    Args:
        entity_type (EntityType):
        entity_id (str):
        next_token (Union[None, Unset, str]):
        limit (Union[Unset, int]):  Default: 5000.
        order (Union[None, SortOrder, Unset]):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedResponseDiscussion]
    """

    kwargs = _get_kwargs(
        entity_type=entity_type,
        entity_id=entity_id,
        next_token=next_token,
        limit=limit,
        order=order,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    entity_type: EntityType,
    entity_id: str,
    next_token: Union[None, Unset, str] = UNSET,
    limit: Union[Unset, int] = 5000,
    order: Union[None, SortOrder, Unset] = UNSET,
) -> Optional[PaginatedResponseDiscussion]:
    """Get discussions for an entity

     Retrieves a paginated list of discussions for a specific entity type and ID

    Args:
        entity_type (EntityType):
        entity_id (str):
        next_token (Union[None, Unset, str]):
        limit (Union[Unset, int]):  Default: 5000.
        order (Union[None, SortOrder, Unset]):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedResponseDiscussion
    """

    try:
        return (
            await asyncio_detailed(
                client=client,
                entity_type=entity_type,
                entity_id=entity_id,
                next_token=next_token,
                limit=limit,
                order=order,
            )
        ).parsed
    except errors.NotFoundException:
        return None
