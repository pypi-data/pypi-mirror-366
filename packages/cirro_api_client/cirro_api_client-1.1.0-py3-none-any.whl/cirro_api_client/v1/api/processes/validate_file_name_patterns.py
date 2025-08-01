from http import HTTPStatus
from typing import Any, Dict, List, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.file_name_match import FileNameMatch
from ...models.validate_file_name_patterns_request import ValidateFileNamePatternsRequest
from ...types import Response


def _get_kwargs(
    process_id: str,
    *,
    body: ValidateFileNamePatternsRequest,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/processes/{process_id}/validate-files:test",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[List["FileNameMatch"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = FileNameMatch.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[List["FileNameMatch"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileNamePatternsRequest,
) -> Response[List["FileNameMatch"]]:
    """Validate file name patterns

     Checks the input file names with the patterns for testing regex matching

    Args:
        process_id (str):
        body (ValidateFileNamePatternsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['FileNameMatch']]
    """

    kwargs = _get_kwargs(
        process_id=process_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileNamePatternsRequest,
) -> Optional[List["FileNameMatch"]]:
    """Validate file name patterns

     Checks the input file names with the patterns for testing regex matching

    Args:
        process_id (str):
        body (ValidateFileNamePatternsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['FileNameMatch']
    """

    try:
        return sync_detailed(
            process_id=process_id,
            client=client,
            body=body,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileNamePatternsRequest,
) -> Response[List["FileNameMatch"]]:
    """Validate file name patterns

     Checks the input file names with the patterns for testing regex matching

    Args:
        process_id (str):
        body (ValidateFileNamePatternsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['FileNameMatch']]
    """

    kwargs = _get_kwargs(
        process_id=process_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileNamePatternsRequest,
) -> Optional[List["FileNameMatch"]]:
    """Validate file name patterns

     Checks the input file names with the patterns for testing regex matching

    Args:
        process_id (str):
        body (ValidateFileNamePatternsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['FileNameMatch']
    """

    try:
        return (
            await asyncio_detailed(
                process_id=process_id,
                client=client,
                body=body,
            )
        ).parsed
    except errors.NotFoundException:
        return None
