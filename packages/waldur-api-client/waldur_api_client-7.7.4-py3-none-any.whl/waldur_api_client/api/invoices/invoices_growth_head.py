from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    accounting_is_running: Union[Unset, bool] = UNSET,
    accounting_mode: Union[Unset, str] = UNSET,
    customers_count: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["accounting_is_running"] = accounting_is_running

    params["accounting_mode"] = accounting_mode

    params["customers_count"] = customers_count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "head",
        "url": "/api/invoices/growth/",
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
    accounting_is_running: Union[Unset, bool] = UNSET,
    accounting_mode: Union[Unset, str] = UNSET,
    customers_count: Union[Unset, int] = UNSET,
) -> Response[Any]:
    """Analyze invoice trends over time by comparing monthly totals for major customers versus others over
    the past year.

    Args:
        accounting_is_running (Union[Unset, bool]):
        accounting_mode (Union[Unset, str]):
        customers_count (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        accounting_is_running=accounting_is_running,
        accounting_mode=accounting_mode,
        customers_count=customers_count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    accounting_is_running: Union[Unset, bool] = UNSET,
    accounting_mode: Union[Unset, str] = UNSET,
    customers_count: Union[Unset, int] = UNSET,
) -> Response[Any]:
    """Analyze invoice trends over time by comparing monthly totals for major customers versus others over
    the past year.

    Args:
        accounting_is_running (Union[Unset, bool]):
        accounting_mode (Union[Unset, str]):
        customers_count (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        accounting_is_running=accounting_is_running,
        accounting_mode=accounting_mode,
        customers_count=customers_count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
