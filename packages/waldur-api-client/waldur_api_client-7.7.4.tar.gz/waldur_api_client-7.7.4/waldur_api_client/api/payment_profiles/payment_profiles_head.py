from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.payment_profiles_head_o_item import PaymentProfilesHeadOItem
from ...models.payment_profiles_head_payment_type_item import PaymentProfilesHeadPaymentTypeItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[PaymentProfilesHeadOItem]] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment_type: Union[Unset, list[PaymentProfilesHeadPaymentTypeItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["is_active"] = is_active

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["organization"] = organization

    json_organization_uuid: Union[Unset, str] = UNSET
    if not isinstance(organization_uuid, Unset):
        json_organization_uuid = str(organization_uuid)
    params["organization_uuid"] = json_organization_uuid

    params["page"] = page

    params["page_size"] = page_size

    json_payment_type: Union[Unset, list[str]] = UNSET
    if not isinstance(payment_type, Unset):
        json_payment_type = []
        for payment_type_item_data in payment_type:
            payment_type_item = payment_type_item_data.value
            json_payment_type.append(payment_type_item)

    params["payment_type"] = json_payment_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "head",
        "url": "/api/payment-profiles/",
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
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[PaymentProfilesHeadOItem]] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment_type: Union[Unset, list[PaymentProfilesHeadPaymentTypeItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[PaymentProfilesHeadOItem]]):
        organization (Union[Unset, str]):
        organization_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        payment_type (Union[Unset, list[PaymentProfilesHeadPaymentTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        is_active=is_active,
        o=o,
        organization=organization,
        organization_uuid=organization_uuid,
        page=page,
        page_size=page_size,
        payment_type=payment_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[PaymentProfilesHeadOItem]] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment_type: Union[Unset, list[PaymentProfilesHeadPaymentTypeItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[PaymentProfilesHeadOItem]]):
        organization (Union[Unset, str]):
        organization_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        payment_type (Union[Unset, list[PaymentProfilesHeadPaymentTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        is_active=is_active,
        o=o,
        organization=organization,
        organization_uuid=organization_uuid,
        page=page,
        page_size=page_size,
        payment_type=payment_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
