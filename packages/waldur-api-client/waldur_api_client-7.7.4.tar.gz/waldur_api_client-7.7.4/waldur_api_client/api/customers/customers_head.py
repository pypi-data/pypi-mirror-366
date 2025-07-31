from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["abbreviation"] = abbreviation

    params["agreement_number"] = agreement_number

    params["archived"] = archived

    params["backend_id"] = backend_id

    params["contact_details"] = contact_details

    params["name"] = name

    params["name_exact"] = name_exact

    params["native_name"] = native_name

    params["o"] = o

    params["organization_group_name"] = organization_group_name

    json_organization_group_uuid: Union[Unset, list[str]] = UNSET
    if not isinstance(organization_group_uuid, Unset):
        json_organization_group_uuid = []
        for organization_group_uuid_item_data in organization_group_uuid:
            organization_group_uuid_item = str(organization_group_uuid_item_data)
            json_organization_group_uuid.append(organization_group_uuid_item)

    params["organization_group_uuid"] = json_organization_group_uuid

    params["owned_by_current_user"] = owned_by_current_user

    params["page"] = page

    params["page_size"] = page_size

    params["query"] = query

    params["registration_code"] = registration_code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "head",
        "url": "/api/customers/",
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
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """To get a list of customers, run GET against /api/customers/ as authenticated user. Note that a user
    can
    only see connected customers:

    - customers that the user owns
    - customers that have a project where user has a role

    Staff also can filter customers by user UUID, for example /api/customers/?user_uuid=<UUID>

    Staff also can filter customers by exists accounting_start_date, for example:

    The first category:
    /api/customers/?accounting_is_running=True
        has accounting_start_date empty (i.e. accounting starts at once)
        has accounting_start_date in the past (i.e. has already started).

    Those that are not in the first:
    /api/customers/?accounting_is_running=False # exists accounting_start_date

    Args:
        abbreviation (Union[Unset, str]):
        agreement_number (Union[Unset, str]):
        archived (Union[Unset, bool]):
        backend_id (Union[Unset, str]):
        contact_details (Union[Unset, str]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        native_name (Union[Unset, str]):
        o (Union[Unset, str]):
        organization_group_name (Union[Unset, str]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        owned_by_current_user (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        registration_code (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        abbreviation=abbreviation,
        agreement_number=agreement_number,
        archived=archived,
        backend_id=backend_id,
        contact_details=contact_details,
        name=name,
        name_exact=name_exact,
        native_name=native_name,
        o=o,
        organization_group_name=organization_group_name,
        organization_group_uuid=organization_group_uuid,
        owned_by_current_user=owned_by_current_user,
        page=page,
        page_size=page_size,
        query=query,
        registration_code=registration_code,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """To get a list of customers, run GET against /api/customers/ as authenticated user. Note that a user
    can
    only see connected customers:

    - customers that the user owns
    - customers that have a project where user has a role

    Staff also can filter customers by user UUID, for example /api/customers/?user_uuid=<UUID>

    Staff also can filter customers by exists accounting_start_date, for example:

    The first category:
    /api/customers/?accounting_is_running=True
        has accounting_start_date empty (i.e. accounting starts at once)
        has accounting_start_date in the past (i.e. has already started).

    Those that are not in the first:
    /api/customers/?accounting_is_running=False # exists accounting_start_date

    Args:
        abbreviation (Union[Unset, str]):
        agreement_number (Union[Unset, str]):
        archived (Union[Unset, bool]):
        backend_id (Union[Unset, str]):
        contact_details (Union[Unset, str]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        native_name (Union[Unset, str]):
        o (Union[Unset, str]):
        organization_group_name (Union[Unset, str]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        owned_by_current_user (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        registration_code (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        abbreviation=abbreviation,
        agreement_number=agreement_number,
        archived=archived,
        backend_id=backend_id,
        contact_details=contact_details,
        name=name,
        name_exact=name_exact,
        native_name=native_name,
        o=o,
        organization_group_name=organization_group_name,
        organization_group_uuid=organization_group_uuid,
        owned_by_current_user=owned_by_current_user,
        page=page,
        page_size=page_size,
        query=query,
        registration_code=registration_code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
