"""Cliente HTTP comum com retry controlado e proteção de origem."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def target_url(base_url: str, path: str) -> str:
    base = urlparse(base_url)
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    parsed = urlparse(url)
    if parsed.scheme != base.scheme or parsed.hostname != base.hostname or parsed.port != base.port:
        raise ValueError(f"Endpoint fora da origem autorizada: {path}")
    return url


def assert_same_origin_response(base_url: str, response: requests.Response) -> None:
    """Garante que nenhum salto de redirecionamento saiu da origem autorizada.

    ``target_url`` só valida a URL inicial da requisição; como os testers seguem
    redirecionamentos por padrão, um alvo comprometido ou malicioso poderia usar um
    3xx para desviar a chamada para outra origem (inclusive interna) sem que nenhuma
    checagem posterior perceba. Esta função revalida toda a cadeia (`response.history`
    + resposta final) contra o esquema/host/porta autorizados.
    """
    base = urlparse(base_url)
    for hop in [*response.history, response]:
        parsed = urlparse(hop.url)
        if parsed.scheme != base.scheme or parsed.hostname != base.hostname or parsed.port != base.port:
            raise ValueError(f"Redirecionamento saiu da origem autorizada: {hop.url}")


def create_session(config: dict[str, Any], headers: dict[str, str] | None = None) -> requests.Session:
    retries = max(0, int(config.get("general", {}).get("retry_attempts", 0)))
    policy = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=0.2,
        status_forcelist=(429, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=policy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    if headers:
        session.headers.update(headers)
    return session

