from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.admin_announcements_head_o_item import AdminAnnouncementsHeadOItem
from ...models.admin_announcements_head_type_item import AdminAnnouncementsHeadTypeItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    description: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsHeadOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsHeadTypeItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["description"] = description

    params["is_active"] = is_active

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_type_: Union[Unset, list[str]] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = []
        for type_item_data in type_:
            type_item = type_item_data.value
            json_type_.append(type_item)

    params["type"] = json_type_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "head",
        "url": "/api/admin-announcements/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Any:
    if response.status_code == 200:
        return None
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    description: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsHeadOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsHeadTypeItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        description (Union[Unset, str]):
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[AdminAnnouncementsHeadOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        type_ (Union[Unset, list[AdminAnnouncementsHeadTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        description=description,
        is_active=is_active,
        o=o,
        page=page,
        page_size=page_size,
        type_=type_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    description: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsHeadOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsHeadTypeItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        description (Union[Unset, str]):
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[AdminAnnouncementsHeadOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        type_ (Union[Unset, list[AdminAnnouncementsHeadTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        description=description,
        is_active=is_active,
        o=o,
        page=page,
        page_size=page_size,
        type_=type_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
