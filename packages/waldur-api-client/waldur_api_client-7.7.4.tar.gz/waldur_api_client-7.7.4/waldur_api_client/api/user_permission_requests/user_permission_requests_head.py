from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.user_permission_requests_head_o_item import UserPermissionRequestsHeadOItem
from ...models.user_permission_requests_head_state_item import UserPermissionRequestsHeadStateItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    created_by: Union[Unset, UUID] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    invitation: Union[Unset, UUID] = UNSET,
    o: Union[Unset, list[UserPermissionRequestsHeadOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[UserPermissionRequestsHeadStateItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_created_by: Union[Unset, str] = UNSET
    if not isinstance(created_by, Unset):
        json_created_by = str(created_by)
    params["created_by"] = json_created_by

    json_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(customer_uuid, Unset):
        json_customer_uuid = str(customer_uuid)
    params["customer_uuid"] = json_customer_uuid

    json_invitation: Union[Unset, str] = UNSET
    if not isinstance(invitation, Unset):
        json_invitation = str(invitation)
    params["invitation"] = json_invitation

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_state: Union[Unset, list[str]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "head",
        "url": "/api/user-permission-requests/",
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
    created_by: Union[Unset, UUID] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    invitation: Union[Unset, UUID] = UNSET,
    o: Union[Unset, list[UserPermissionRequestsHeadOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[UserPermissionRequestsHeadStateItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created_by (Union[Unset, UUID]):
        customer_uuid (Union[Unset, UUID]):
        invitation (Union[Unset, UUID]):
        o (Union[Unset, list[UserPermissionRequestsHeadOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        state (Union[Unset, list[UserPermissionRequestsHeadStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        created_by=created_by,
        customer_uuid=customer_uuid,
        invitation=invitation,
        o=o,
        page=page,
        page_size=page_size,
        state=state,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    created_by: Union[Unset, UUID] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    invitation: Union[Unset, UUID] = UNSET,
    o: Union[Unset, list[UserPermissionRequestsHeadOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    state: Union[Unset, list[UserPermissionRequestsHeadStateItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created_by (Union[Unset, UUID]):
        customer_uuid (Union[Unset, UUID]):
        invitation (Union[Unset, UUID]):
        o (Union[Unset, list[UserPermissionRequestsHeadOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        state (Union[Unset, list[UserPermissionRequestsHeadStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        created_by=created_by,
        customer_uuid=customer_uuid,
        invitation=invitation,
        o=o,
        page=page,
        page_size=page_size,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
