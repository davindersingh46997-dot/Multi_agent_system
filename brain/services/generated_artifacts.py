from io import BytesIO
import re

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Preformatted, SimpleDocTemplate

from brain.schemas.generated_files import OutputFormat


MEDIA_TYPES = {
    OutputFormat.PYTHON: "text/x-python; charset=utf-8",
    OutputFormat.JAVASCRIPT: "text/javascript; charset=utf-8",
    OutputFormat.TYPESCRIPT: "text/typescript; charset=utf-8",
    OutputFormat.HTML: "text/html; charset=utf-8",
    OutputFormat.CSS: "text/css; charset=utf-8",
    OutputFormat.JAVA: "text/x-java-source; charset=utf-8",
    OutputFormat.CPP: "text/x-c++src; charset=utf-8",
    OutputFormat.JSON: "application/json; charset=utf-8",
    OutputFormat.MARKDOWN: "text/markdown; charset=utf-8",
    OutputFormat.TEXT: "text/plain; charset=utf-8",
}


def remove_code_fence(content: str) -> str:
    lines = content.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return content.strip()


def safe_filename(suggestion: str | None, generation_id: int, output_format: OutputFormat) -> str:
    stem = (suggestion or "").strip().rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    stem = stem.rsplit(".", 1)[0] if "." in stem else stem
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_-")[:64]
    if not stem:
        stem = f"generated_{generation_id}"
    return f"{stem}.{output_format.value}"


def make_artifact(content: str, output_format: OutputFormat) -> tuple[bytes, str]:
    if output_format == OutputFormat.PDF:
        output = BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=landscape(letter),
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        code_style = ParagraphStyle(
            "GeneratedCode",
            fontName="Courier",
            fontSize=8,
            leading=10,
        )
        document.build([Preformatted(content, code_style, maxLineLength=110)])
        return output.getvalue(), "application/pdf"
    return content.encode("utf-8"), MEDIA_TYPES[output_format]
