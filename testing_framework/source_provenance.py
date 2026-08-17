"""Detecção heurística de sinais de autoria automatizada em código-fonte."""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import re
from typing import Iterable


TEXT_SUFFIXES = {
    ".c", ".cc", ".conf", ".cpp", ".cs", ".css", ".go", ".h", ".hpp",
    ".html", ".ini", ".java", ".js", ".json", ".jsx", ".kt", ".kts",
    ".md", ".php", ".properties", ".py", ".rb", ".rs", ".scala", ".sh",
    ".sql", ".swift", ".toml", ".ts", ".tsx", ".txt", ".vue", ".xml",
    ".yaml", ".yml",
}


def _decoded(*values: str) -> list[str]:
    return [bytes.fromhex(value).decode("utf-8") for value in values]


TOOL_NAMES = _decoded(
    "63686174677074", "636f646578", "636f70696c6f74", "636c61756465",
    "67656d696e69", "6f70656e6169", "637572736f72", "77696e6473757266",
    "6169646572",
)

EXPLICIT_MARKERS = _decoded(
    "617320616e206169206c616e6775616765206d6f64656c",
    "67656e657261746564206279206169",
    "61692d67656e65726174656420636f6465",
    "636f64652067656e657261746564206279206169",
    "67657261646f20706f72206961",
    "63c3b36469676f2067657261646f20706f72206961",
    "63726961646f20636f6d206961",
    "646573656e766f6c7669646f20636f6d206961",
)

ARTIFACT_NAMES = {
    value.casefold()
    for value in _decoded(
        "2e637572736f7272756c6573", "2e77696e647375727672756c6573",
        "636c617564652e6d64", "636c617564652e6c6f63616c2e6d64",
        "2e61696465722e636f6e662e796d6c", "636f70696c6f742d696e737472756374696f6e732e6d64",
        "2e637572736f7269676e6f7265", "2e637572736f72696e646578696e6769676e6f7265",
        "67656d696e692e6d64", "6167656e74732e6d64",
    )
}

AUTHORSHIP_WORDS = re.compile(
    r"\b(?:generated|written|created|authored|produced|assisted|gerado|escrito|criado|produzido|desenvolvido|assistido)\b",
    re.IGNORECASE,
)
TRAILER = re.compile(r"\bco-authored-by\s*:", re.IGNORECASE)
GENERIC_AUTHORSHIP = re.compile(
    bytes.fromhex(
        "5c62283f3a67656e6572617465647c7772697474656e7c637265617465647c617574686f7265647c70726f64756365647c61737369737465647c646576656c6f7065647c67657261646f7c6573637269746f7c63726961646f7c70726f64757a69646f7c646573656e766f6c7669646f7c61737369737469646f295c622e7b302c34387d5c62283f3a61697c69617c6172746966696369616c20696e74656c6c6967656e63657c696e74656c6967c3aa6e636961206172746966696369616c295c62"
    ).decode("utf-8"),
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProvenanceSignal:
    path: Path
    line: int
    kind: str
    confidence: str
    excerpt: str


def _matches_any(relative: str, patterns: Iterable[str]) -> bool:
    normalized = relative.replace("\\", "/")
    return any(fnmatch(normalized, pattern.replace("\\", "/")) for pattern in patterns)


def _artifact_signal(path: Path, root: Path) -> ProvenanceSignal | None:
    relative = path.relative_to(root)
    normalized = relative.as_posix().casefold()
    if path.name.casefold() in ARTIFACT_NAMES or normalized.endswith(".github/copilot-instructions.md"):
        return ProvenanceSignal(path, 1, "arquivo de configuração de assistente", "high", relative.as_posix())
    return None


def scan_source_provenance(
    root: Path,
    files: Iterable[Path],
    *,
    exclude: Iterable[str] = (),
    allowlist: Iterable[str] = (),
    max_file_bytes: int = 1_000_000,
    max_signals: int = 100,
) -> tuple[list[ProvenanceSignal], int]:
    """Procura assinaturas explícitas e artefatos; não determina autoria por estilo."""
    if max_signals <= 0:
        return [], 0
    signals: list[ProvenanceSignal] = []
    scanned = 0
    lowered_tools = tuple(name.casefold() for name in TOOL_NAMES)
    lowered_markers = tuple(marker.casefold() for marker in EXPLICIT_MARKERS)

    for path in files:
        relative = path.relative_to(root).as_posix()
        if _matches_any(relative, exclude) or _matches_any(relative, allowlist):
            continue
        artifact = _artifact_signal(path, root)
        if artifact:
            signals.append(artifact)
            if len(signals) >= max_signals:
                break
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > max_file_bytes:
                continue
            content = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in content:
            continue
        text = content.decode("utf-8", errors="replace")
        scanned += 1
        for number, line in enumerate(text.splitlines(), start=1):
            folded = line.casefold()
            explicit = next((marker for marker in lowered_markers if marker in folded), None)
            tool = next((name for name in lowered_tools if name in folded), None)
            if explicit:
                kind, confidence = "declaração explícita de autoria automatizada", "high"
            elif tool and (AUTHORSHIP_WORDS.search(line) or TRAILER.search(line)):
                kind, confidence = "ferramenta associada a termo de autoria", "high"
            elif GENERIC_AUTHORSHIP.search(line):
                kind, confidence = "termo genérico associado a autoria automatizada", "medium"
            else:
                continue
            excerpt = line.strip()[:240]
            signals.append(ProvenanceSignal(path, number, kind, confidence, excerpt))
            if len(signals) >= max_signals:
                return signals, scanned
    return signals, scanned
