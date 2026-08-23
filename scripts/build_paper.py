#!/usr/bin/env python3
"""
Assemble the section files in paper/sections into one readable working paper.

The argument currently lives as one markdown file per section, which is good for
editing and bad for reading end to end. This stitches them into a single
document with a title page and a table of contents, so there is one artifact to
hand to a reader.

By default it writes a combined markdown file. If pandoc is installed, pass
--pdf or --html to also render those, and the script falls back to a plain note
if pandoc is missing rather than failing.

A deliberate design choice: the section order is an explicit list below, not a
filename sort. The sections directory has a numbering quirk (two files both
titled "6. Policy Recommendation"), and a silent alphabetical sort would either
drop one or place it wrong. The manifest names exactly what goes in and in what
order. Any .md file in the sections directory that is not in the manifest is
reported at the end so you can decide whether it belongs, rather than being
swept in or quietly ignored.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS_DIR = ROOT / "paper" / "sections"
DEFAULT_OUT = ROOT / "paper" / "kalshi_macro_policy.md"

TITLE = "Kalshi and the Institutionalization of Macro Prediction Markets"
SUBTITLE = (
    "An extension of Diercks, Katz and Wright (2026), "
    "\"Kalshi and the Rise of Macro Markets\" (FEDS 2026-010)"
)

# The canonical order. Edit this when sections are added, renamed, or resolved.
# Note the sections directory also contains 6_policy_recommendation.md, which
# looks like an earlier draft of 7_policy_recommendation.md (both are headed
# "6. Policy Recommendation"). Only one belongs in the final paper. This
# manifest uses the longer, more recent 7_policy_recommendation.md, the one the
# integration notes in docs/paper_integration_ideas.md refer to. If you decide
# the other is canonical, swap it here.
SECTION_ORDER = [
    "1_background.md",
    "2_replication.md",
    "3_manipulation_risk.md",
    "4_institutional_pathway.md",
    "5_polymarket_comparison.md",
    "6_macro_policy_implementation.md",
    "7_policy_recommendation.md",
]


def build_markdown() -> tuple[str, list[str]]:
    """Return the combined markdown text and any section files left out of it."""
    if not SECTIONS_DIR.is_dir():
        raise SystemExit(f"Sections directory not found: {SECTIONS_DIR}")

    parts = [
        f"# {TITLE}",
        "",
        f"*{SUBTITLE}*",
        "",
        f"Compiled {date.today().isoformat()} from paper/sections by scripts/build_paper.py.",
        "",
        "---",
        "",
    ]

    missing_from_disk = []
    for name in SECTION_ORDER:
        path = SECTIONS_DIR / name
        if not path.is_file():
            missing_from_disk.append(name)
            continue
        parts.append(path.read_text().rstrip())
        parts.append("")
        parts.append("---")
        parts.append("")

    if missing_from_disk:
        raise SystemExit(
            "These files are named in SECTION_ORDER but were not found: "
            f"{missing_from_disk}. Fix the manifest in scripts/build_paper.py."
        )

    on_disk = {p.name for p in SECTIONS_DIR.glob("*.md")}
    left_out = sorted(on_disk - set(SECTION_ORDER))
    return "\n".join(parts).rstrip() + "\n", left_out


def render_with_pandoc(md_path: Path, target: str) -> bool:
    """Render the combined markdown to pdf or html via pandoc. Returns success."""
    if shutil.which("pandoc") is None:
        print(
            f"pandoc is not installed, so the {target.upper()} was not built. "
            "Install pandoc (and a LaTeX engine for PDF) and re-run, or just use "
            f"the markdown at {md_path}.",
            file=sys.stderr,
        )
        return False

    out_path = md_path.with_suffix(f".{target}")
    cmd = ["pandoc", str(md_path), "-o", str(out_path), "--toc", "--standalone"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"pandoc failed to build the {target.upper()}: {exc}", file=sys.stderr)
        return False
    print(f"Wrote {out_path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Combined markdown output path.")
    parser.add_argument("--pdf", action="store_true", help="Also render a PDF (needs pandoc).")
    parser.add_argument("--html", action="store_true", help="Also render an HTML page (needs pandoc).")
    args = parser.parse_args()

    combined, left_out = build_markdown()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(combined)
    print(f"Wrote {args.out} ({len(SECTION_ORDER)} sections)")

    if args.pdf:
        render_with_pandoc(args.out, "pdf")
    if args.html:
        render_with_pandoc(args.out, "html")

    if left_out:
        print(
            "\nHeads up: these section files are on disk but not in the paper, "
            f"because they are not in SECTION_ORDER: {left_out}. "
            "If one of them belongs, add it to the manifest in scripts/build_paper.py."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
