#!/usr/bin/env python3
"""
News front page generator for make.fun news-image-20261118.
Draws a 1024x1024 newspaper-style infographic using PIL.
Falls back to copying a bundled entry.png if PIL is unavailable.
"""

import os
import sys
import shutil
from pathlib import Path


def draw_with_pil(output_path: Path) -> None:
    """Draw the newspaper front page using PIL."""
    from PIL import Image, ImageDraw, ImageFont

    # Constants
    WIDTH, HEIGHT = 1024, 1024
    MARGIN = 48
    BG_COLOR = "#f7f3ea"
    TEXT_COLOR = "#111111"
    ACCENT_COLOR = "#8b1a1a"
    RULE_COLOR = "#8b1a1a"

    # Fonts
    FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
    SERIF_REGULAR = FONT_DIR / "LiberationSerif-Regular.ttf"
    SERIF_BOLD = FONT_DIR / "LiberationSerif-Bold.ttf"
    SANS_REGULAR = FONT_DIR / "LiberationSans-Regular.ttf"
    SANS_BOLD = FONT_DIR / "LiberationSans-Bold.ttf"

    # Verify fonts exist
    for f in [SERIF_REGULAR, SERIF_BOLD, SANS_REGULAR, SANS_BOLD]:
        if not f.exists():
            raise FileNotFoundError(f"Font not found: {f}")

    # Create image
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Font sizes
    MASTHEAD_SIZE = 72
    DATE_SIZE = 28
    TAG_SIZE = 18
    LEAD_HEADLINE_SIZE = 42
    GRID_HEADLINE_SIZE = 30
    BODY_SIZE = 19
    FOOTER_SIZE = 16
    TOMORROW_SIZE = 16

    # Load fonts
    masthead_font = ImageFont.truetype(str(SERIF_BOLD), MASTHEAD_SIZE)
    date_font = ImageFont.truetype(str(SERIF_REGULAR), DATE_SIZE)
    tag_font = ImageFont.truetype(str(SANS_BOLD), TAG_SIZE)
    lead_headline_font = ImageFont.truetype(str(SERIF_BOLD), LEAD_HEADLINE_SIZE)
    grid_headline_font = ImageFont.truetype(str(SERIF_BOLD), GRID_HEADLINE_SIZE)
    body_font = ImageFont.truetype(str(SANS_REGULAR), BODY_SIZE)
    footer_font = ImageFont.truetype(str(SANS_REGULAR), FOOTER_SIZE)
    tomorrow_font = ImageFont.truetype(str(SANS_BOLD), TOMORROW_SIZE)

    # Helper functions
    def text_width(font, text):
        return draw.textlength(text, font=font)

    def text_bbox(font, text):
        return draw.textbbox((0, 0), text, font=font)

    def wrap_text(text, font, max_width):
        """Wrap text to fit within max_width. Returns list of lines."""
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if text_width(font, test_line) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def draw_text_block(x, y, lines, font, color=TEXT_COLOR, line_spacing=1.2):
        """Draw multiple lines of text. Returns (next_y, max_line_height)."""
        if not lines:
            return y, 0
        bbox = text_bbox(font, "Ag")
        line_height = bbox[3] - bbox[1]
        spacing = int(line_height * line_spacing)
        max_w = 0
        for i, line in enumerate(lines):
            draw.text((x, y + i * spacing), line, font=font, fill=color)
            w = text_width(font, line)
            if w > max_w:
                max_w = w
        return y + len(lines) * spacing, max_w

    # ============================================================
    # 1. MASTHEAD
    # ============================================================
    y = MARGIN

    # "THE WORLD IN ONE PAGE"
    masthead_text = "THE WORLD IN ONE PAGE"
    masthead_w = text_width(masthead_font, masthead_text)
    masthead_x = (WIDTH - masthead_w) // 2
    draw.text((masthead_x, y), masthead_text, font=masthead_font, fill=TEXT_COLOR)
    masthead_bbox = text_bbox(masthead_font, masthead_text)
    masthead_h = masthead_bbox[3] - masthead_bbox[1]
    y += masthead_h + 8

    # Thin rule under masthead text
    rule_y = y
    draw.line([(MARGIN, rule_y), (WIDTH - MARGIN, rule_y)], fill=RULE_COLOR, width=1)
    y += 10

    # Date
    date_text = "WEDNESDAY, 18 NOVEMBER 2026"
    date_w = text_width(date_font, date_text)
    date_x = (WIDTH - date_w) // 2
    draw.text((date_x, y), date_text, font=date_font, fill=TEXT_COLOR)
    date_bbox = text_bbox(date_font, date_text)
    date_h = date_bbox[3] - date_bbox[1]
    y += date_h + 8

    # Double rule under masthead block
    double_rule_y1 = y
    double_rule_y2 = y + 3
    draw.line([(MARGIN, double_rule_y1), (WIDTH - MARGIN, double_rule_y1)], fill=RULE_COLOR, width=1)
    draw.line([(MARGIN, double_rule_y2), (WIDTH - MARGIN, double_rule_y2)], fill=RULE_COLOR, width=1)
    y = double_rule_y2 + 16

    masthead_bottom = y

    # ============================================================
    # 2. LEAD STORY (top half, full width)
    # ============================================================
    lead_x = MARGIN
    lead_max_width = WIDTH - 2 * MARGIN

    # Region tag: "MIDDLE EAST"
    lead_tag = "MIDDLE EAST"
    draw.text((lead_x, y), lead_tag, font=tag_font, fill=ACCENT_COLOR)
    tag_bbox = text_bbox(tag_font, lead_tag)
    tag_bottom = y + (tag_bbox[3] - tag_bbox[1])
    tag_rule_y = tag_bottom + 6  # At least 4px gap below tag text
    draw.line([(lead_x, tag_rule_y), (lead_x + text_width(tag_font, lead_tag), tag_rule_y)], fill=ACCENT_COLOR, width=2)
    # Assert: rule y > tag_bottom + 4
    assert tag_rule_y > tag_bottom + 4, f"Lead tag rule strikes through text: rule_y={tag_rule_y}, tag_bottom={tag_bottom}"

    y = tag_rule_y + 12

    # Headline: "IRAN STRIKES US RADAR BASE IN BAHRAIN"
    lead_headline = "IRAN STRIKES US RADAR BASE IN BAHRAIN"
    headline_lines = wrap_text(lead_headline, lead_headline_font, lead_max_width)
    y, _ = draw_text_block(lead_x, y, headline_lines, lead_headline_font, TEXT_COLOR, line_spacing=1.15)
    headline_bottom = y

    # Add minimum 12px gap before summary
    y += 12

    # Summary (2 lines)
    lead_summary = ("Iran's Revolutionary Guards claimed a drone strike on a US radar system "
                    "at Sheikh Isa Air Base — the third strike on Bahrain in five days — "
                    "as US–Iran tensions rise.")
    summary_lines = wrap_text(lead_summary, body_font, lead_max_width)
    # Ensure at least 2 lines, but don't force more than wrapped
    if len(summary_lines) < 2:
        # This shouldn't happen with the given text, but handle gracefully
        pass

    # Assert: at least 12px gap between headline bottom and summary top
    summary_top = y
    assert summary_top - headline_bottom >= 12, f"Insufficient gap: summary_top={summary_top}, headline_bottom={headline_bottom}, gap={summary_top - headline_bottom}"

    y, _ = draw_text_block(lead_x, y, summary_lines[:2], body_font, TEXT_COLOR, line_spacing=1.3)
    lead_bottom = y

    # Graphic element: stylized radar dish / drone silhouette
    # Draw in the right portion of the lead area, below the tag
    graphic_x = WIDTH - MARGIN - 180
    graphic_y = tag_rule_y + 20
    graphic_size = 160

    # Radar dish: arc + center line + dots
    # Dish arc
    draw.arc([graphic_x, graphic_y, graphic_x + graphic_size, graphic_y + graphic_size],
             start=30, end=150, fill=ACCENT_COLOR, width=3)
    # Center spike
    cx = graphic_x + graphic_size // 2
    cy = graphic_y + graphic_size // 2
    draw.line([(cx, cy), (cx, graphic_y + graphic_size + 20)], fill=ACCENT_COLOR, width=2)
    # Signal arcs
    for r in [30, 55, 80]:
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=30, end=150, fill=ACCENT_COLOR, width=1)
    # Drone silhouette (small, top-right of radar)
    drone_x = graphic_x + graphic_size + 10
    drone_y = graphic_y - 10
    # Body
    draw.ellipse([drone_x, drone_y, drone_x + 24, drone_y + 8], fill=ACCENT_COLOR)
    # Wings
    draw.line([(drone_x + 12, drone_y + 4), (drone_x - 15, drone_y - 8)], fill=ACCENT_COLOR, width=2)
    draw.line([(drone_x + 12, drone_y + 4), (drone_x - 15, drone_y + 16)], fill=ACCENT_COLOR, width=2)
    draw.line([(drone_x + 12, drone_y + 4), (drone_x + 35, drone_y - 8)], fill=ACCENT_COLOR, width=2)
    draw.line([(drone_x + 12, drone_y + 4), (drone_x + 35, drone_y + 16)], fill=ACCENT_COLOR, width=2)

    lead_area_bottom = max(lead_bottom, graphic_y + graphic_size + 30)

    # ============================================================
    # 3. FOUR GRID BLOCKS (2x2)
    # ============================================================
    grid_top = lead_area_bottom + 24
    col_width = (WIDTH - 2 * MARGIN - 24) // 2  # 24px gutter
    row_height = (HEIGHT - grid_top - MARGIN - 80) // 2  # Leave room for footer

    grid_data = [
        {
            "tag": "ASIA-PACIFIC",
            "headline": "QUAD LEADERS MEET IN MANILA",
            "summary": "Trump, Modi, Takaichi and Albanese met; Modi proposed free e-visas for ASEAN tourists, and Trump called Modi a 'tough man'."
        },
        {
            "tag": "MARKETS",
            "headline": "NVIDIA BEATS ESTIMATES WITHOUT HUANG",
            "summary": "Nvidia beat earnings in its first report without Jensen Huang; the board says it will not reinstate him, though he is said to be ready to return."
        },
        {
            "tag": "WORLD",
            "headline": "RUSSIAN MILITARY PLANE CRASHES IN SIBERIA",
            "summary": "A Russian military transport plane crashed in Siberia, killing 19 people on board."
        },
        {
            "tag": "HEALTH",
            "headline": "US LOSES ITS MEASLES-FREE STATUS",
            "summary": "The United States lost its measles-free status as cases and deaths continue to mount."
        }
    ]

    for idx, block in enumerate(grid_data):
        col = idx % 2
        row = idx // 2
        x = MARGIN + col * (col_width + 24)
        y = grid_top + row * (row_height + 16)

        # Region tag
        draw.text((x, y), block["tag"], font=tag_font, fill=ACCENT_COLOR)
        tag_bbox = text_bbox(tag_font, block["tag"])
        tag_bottom = y + (tag_bbox[3] - tag_bbox[1])
        tag_rule_y = tag_bottom + 6
        draw.line([(x, tag_rule_y), (x + text_width(tag_font, block["tag"]), tag_rule_y)], fill=ACCENT_COLOR, width=2)
        # Assert: rule y > tag_bottom + 4
        assert tag_rule_y > tag_bottom + 4, f"Grid {idx} tag rule strikes through text: rule_y={tag_rule_y}, tag_bottom={tag_bottom}"

        y = tag_rule_y + 10

        # Headline
        headline_lines = wrap_text(block["headline"], grid_headline_font, col_width)
        y, _ = draw_text_block(x, y, headline_lines, grid_headline_font, TEXT_COLOR, line_spacing=1.15)

        y += 6

        # Summary (1 line, wrapped if needed)
        summary_lines = wrap_text(block["summary"], body_font, col_width)
        y, _ = draw_text_block(x, y, summary_lines[:2], body_font, TEXT_COLOR, line_spacing=1.3)

    grid_bottom = grid_top + 2 * (row_height + 16)

    # ============================================================
    # 4. FOOTER
    # ============================================================
    footer_y = HEIGHT - MARGIN - 40

    # Thin rule
    draw.line([(MARGIN, footer_y), (WIDTH - MARGIN, footer_y)], fill=RULE_COLOR, width=1)
    footer_y += 10

    # Sources line
    sources_text = "Sources: wire reports, 18 November 2026 · Drawn illustration, no photographs"
    sources_w = text_width(footer_font, sources_text)
    sources_x = (WIDTH - sources_w) // 2
    draw.text((sources_x, footer_y), sources_text, font=footer_font, fill=TEXT_COLOR)
    footer_y += 22

    # Tomorrow note (if it fits)
    tomorrow_text = "Xi, Trump and Putin meet in Shenzhen tomorrow."
    tomorrow_w = text_width(tomorrow_font, tomorrow_text)
    tomorrow_x = (WIDTH - tomorrow_w) // 2
    # Check if it fits without crowding (at least 16px from bottom)
    if footer_y + 22 <= HEIGHT - MARGIN:
        draw.text((tomorrow_x, footer_y), tomorrow_text, font=tomorrow_font, fill=ACCENT_COLOR)
        footer_y += 22

    # ============================================================
    # SAVE
    # ============================================================
    img.save(output_path, "PNG", optimize=True)


def main():
    # Determine output directory
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if output_dir:
        output_path = Path(output_dir) / "entry.png"
    else:
        output_path = Path("/output/entry.png")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Try PIL path first
    try:
        draw_with_pil(output_path)
    except ImportError:
        # Fallback: copy bundled entry.png
        try:
            base_dir = Path(__file__).resolve().parent
        except NameError:
            # When run via exec(), __file__ may not be defined
            base_dir = Path.cwd()
        bundled = base_dir / "entry.png"
        if not bundled.exists():
            raise RuntimeError("PIL not available and no bundled entry.png found")
        shutil.copyfile(bundled, output_path)


if __name__ == "__main__":
    main()