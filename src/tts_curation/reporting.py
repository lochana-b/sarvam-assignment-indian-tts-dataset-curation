from __future__ import annotations

from pathlib import Path

from weasyprint import HTML


def markdown_to_pdf(input_path: str | Path, output_path: str | Path) -> None:
    try:
        import markdown
    except ImportError as exc:
        raise RuntimeError("Install markdown to build PDF reports: pip install markdown") from exc

    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = markdown.markdown(
        input_path.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "toc"],
    )
    document = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.45; color: #1f2933; }}
        h1, h2, h3 {{ color: #102a43; }}
        table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
        th, td {{ border: 1px solid #bcccdc; padding: 6px 8px; vertical-align: top; }}
        th {{ background: #f0f4f8; }}
        code {{ background: #f0f4f8; padding: 1px 3px; }}
      </style>
    </head>
    <body>{html}</body>
    </html>
    """
    HTML(string=document, base_url=str(input_path.parent)).write_pdf(str(output_path))

