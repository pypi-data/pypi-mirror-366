import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.promotions_campaigns_head_o_item import PromotionsCampaignsHeadOItem
from ...models.promotions_campaigns_head_state_item import PromotionsCampaignsHeadStateItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    discount_type: Union[Unset, str] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    o: Union[Unset, list[PromotionsCampaignsHeadOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    service_provider_uuid: Union[Unset, UUID] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[PromotionsCampaignsHeadStateItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["discount_type"] = discount_type

    json_end_date: Union[Unset, str] = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["end_date"] = json_end_date

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["offering"] = offering

    json_offering_uuid: Union[Unset, str] = UNSET
    if not isinstance(offering_uuid, Unset):
        json_offering_uuid = str(offering_uuid)
    params["offering_uuid"] = json_offering_uuid

    params["page"] = page

    params["page_size"] = page_size

    params["query"] = query

    json_service_provider_uuid: Union[Unset, str] = UNSET
    if not isinstance(service_provider_uuid, Unset):
        json_service_provider_uuid = str(service_provider_uuid)
    params["service_provider_uuid"] = json_service_provider_uuid

    json_start_date: Union[Unset, str] = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["start_date"] = json_start_date

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
        "url": "/api/promotions-campaigns/",
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
    discount_type: Union[Unset, str] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    o: Union[Unset, list[PromotionsCampaignsHeadOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    service_provider_uuid: Union[Unset, UUID] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[PromotionsCampaignsHeadStateItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        discount_type (Union[Unset, str]):
        end_date (Union[Unset, datetime.date]):
        o (Union[Unset, list[PromotionsCampaignsHeadOItem]]):
        offering (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        service_provider_uuid (Union[Unset, UUID]):
        start_date (Union[Unset, datetime.date]):
        state (Union[Unset, list[PromotionsCampaignsHeadStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        discount_type=discount_type,
        end_date=end_date,
        o=o,
        offering=offering,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        query=query,
        service_provider_uuid=service_provider_uuid,
        start_date=start_date,
        state=state,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    discount_type: Union[Unset, str] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    o: Union[Unset, list[PromotionsCampaignsHeadOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    service_provider_uuid: Union[Unset, UUID] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[PromotionsCampaignsHeadStateItem]] = UNSET,
) -> Response[Any]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        discount_type (Union[Unset, str]):
        end_date (Union[Unset, datetime.date]):
        o (Union[Unset, list[PromotionsCampaignsHeadOItem]]):
        offering (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        service_provider_uuid (Union[Unset, UUID]):
        start_date (Union[Unset, datetime.date]):
        state (Union[Unset, list[PromotionsCampaignsHeadStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        discount_type=discount_type,
        end_date=end_date,
        o=o,
        offering=offering,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        query=query,
        service_provider_uuid=service_provider_uuid,
        start_date=start_date,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
