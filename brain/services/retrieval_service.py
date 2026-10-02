from collections import Counter
import hashlib
import math
import os
from pathlib import Path
import re
from sqlalchemy.orm import Session

from brain.models.project import Project, ProjectChunk


IGNORED_DIRECTORIES = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "dist",
    "build", "__pycache__", ".next", ".idea", ".vscode", "coverage",
}
IGNORED_SUFFIXES = {".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".npy", ".db"}
MAX_SOURCE_BYTES = 512_000
LINES_PER_CHUNK = 100


def _tokens(text: str) -> list[str]:
    split_identifiers = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    split_identifiers = re.sub(r"[_\-.]+", " ", split_identifiers)
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{1,}", split_identifiers.lower())


def _is_indexable(path: Path) -> bool:
    name = path.name.lower()
    if name == ".env" or name.startswith(".env."):
        return False
    if name in {"id_rsa", "id_ed25519", "credentials", "secrets.json"}:
        return False
    if path.suffix.lower() in IGNORED_SUFFIXES:
        return False
    return not path.is_symlink()


def _source_files(root: Path):
    for current, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(
            directory for directory in directories
            if directory not in IGNORED_DIRECTORIES
            and not (Path(current) / directory).is_symlink()
        )
        for filename in sorted(filenames):
            path = Path(current) / filename
            if _is_indexable(path):
                yield path


def index_project(db: Session, project: Project, root: Path) -> int:
    db.query(ProjectChunk).filter(ProjectChunk.project_id == project.id).delete()
    chunk_count = 0
    for file_path in _source_files(root):
        try:
            if file_path.stat().st_size > MAX_SOURCE_BYTES:
                continue
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        lines = source.splitlines()
        relative_path = file_path.relative_to(root).as_posix()
        for chunk_index, start in enumerate(range(0, len(lines), LINES_PER_CHUNK)):
            chunk_lines = lines[start : start + LINES_PER_CHUNK]
            content = "\n".join(chunk_lines)
            if not content.strip():
                continue
            db.add(ProjectChunk(
                project_id=project.id,
                relative_path=relative_path,
                chunk_index=chunk_index,
                start_line=start + 1,
                end_line=start + len(chunk_lines),
                content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                content=content,
            ))
            chunk_count += 1
    db.flush()
    return chunk_count


def retrieve(db: Session, project_id: int, query: str, limit: int = 8) -> list[dict[str, object]]:
    query_terms = set(_tokens(query))
    if not query_terms:
        return []

    chunks = db.query(ProjectChunk).filter(ProjectChunk.project_id == project_id).all()
    if not chunks:
        return []

    tokenized = [_tokens(chunk.content) for chunk in chunks]
    document_frequency: Counter[str] = Counter()
    for terms in tokenized:
        document_frequency.update(set(terms))
    average_length = max(1.0, sum(map(len, tokenized)) / len(tokenized))
    scored: list[tuple[float, ProjectChunk]] = []

    for chunk, terms in zip(chunks, tokenized):
        frequencies = Counter(terms)
        length = len(terms)
        score = 0.0
        for term in query_terms:
            frequency = frequencies[term]
            if not frequency:
                continue
            inverse_frequency = math.log1p(
                (len(chunks) - document_frequency[term] + 0.5)
                / (document_frequency[term] + 0.5)
            )
            normalization = frequency + 1.2 * (0.25 + 0.75 * length / average_length)
            score += inverse_frequency * frequency * 2.2 / normalization
        if score:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {
            "path": chunk.relative_path,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "score": round(score, 4),
            "content": chunk.content,
            "content_hash": chunk.content_hash,
        }
        for score, chunk in scored[:limit]
    ]


def format_evidence(results: list[dict[str, object]]) -> str:
    if not results:
        return "No matching indexed project source was found. Use the workspace tools to inspect files."
    return "\n\n".join(
        f"[Evidence: {item['path']}:{item['start_line']}-{item['end_line']} "
        f"score={item['score']} hash={item['content_hash']}]\n{item['content']}"
        for item in results
    )