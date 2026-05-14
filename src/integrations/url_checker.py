import time
from dataclasses import dataclass

import aiohttp


@dataclass(frozen=True)
class PingResult:
    is_available: bool
    status_code: int | None
    response_time: int
    error_type: str | None = None


async def ping_url(
    url: str,
    *,
    timeout: int = 10,  # noqa: ASYNC109
    expected_status: int = 200,
) -> PingResult:
    start = time.perf_counter()
    client_timeout = aiohttp.ClientTimeout(total=timeout)

    try:
        async with (
            aiohttp.ClientSession(timeout=client_timeout) as session,
            session.get(url) as response,
        ):
            await response.read()

            response_time = int((time.perf_counter() - start) * 1000)
            is_available = response.status == expected_status

            return PingResult(
                is_available=is_available,
                status_code=response.status,
                response_time=response_time,
                error_type=None if is_available else "unexpected_status",
            )

    except (TimeoutError, aiohttp.ServerTimeoutError):
        error_type = "timeout"
    except aiohttp.InvalidURL:
        error_type = "invalid_url"
    except aiohttp.ClientConnectorError:
        error_type = "connect_error"
    except aiohttp.ClientError:
        error_type = "client_error"
    except Exception:
        error_type = "unknown_error"

    return PingResult(
        is_available=False,
        status_code=None,
        response_time=int((time.perf_counter() - start) * 1000),
        error_type=error_type,
    )
