from matplotlib.patches import Wedge, Circle
from matplotlib import font_manager, rcParams
from io import BytesIO
from PIL import Image as PILImage
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from normalizer import normalize_text
from ngrams import get_ngrams
from config import ICO_PATH, APP_NAME
import os
import urllib
import pandas as pd
import matplotlib.pyplot as plt
import math


# Register custom fonts to ensure consistent typography in the PDF output
SEGOE_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"
SEGOE_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
font_manager.fontManager.addfont(SEGOE_REGULAR)
font_manager.fontManager.addfont(SEGOE_BOLD)
rcParams["font.family"] = "Segoe UI"
pdfmetrics.registerFont(TTFont("SegoeUI", SEGOE_REGULAR))
pdfmetrics.registerFont(TTFont("SegoeUI-Bold", SEGOE_BOLD))
registerFontFamily("SegoeUI", normal="SegoeUI", bold="SegoeUI-Bold")


def print_report(
    target_df: pd.DataFrame,
    target_ngram_index: dict,
    pdf_ngram_index: dict,
    output_pdf: str,
    n: int,
    overall_similarity: float,
    per_pdf_scores: dict,
    show_more_similar_sentences: bool,
    more_similar_ngram: int,
    show_references: bool,
    show_pagenum: bool,
    show_statistics: bool,
    translator,
) -> str:

    # Create the PDF template with specific margins
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    normal_style = styles["Normal"]
    normal_style.fontName = "SegoeUI"
    normal_style.fontSize = 10
    normal_style.leading = 14

    section_title_style = styles["Heading2"].clone("SectionTitle")
    section_title_style.fontName = "SegoeUI-Bold"
    section_title_style.fontSize = 13
    section_title_style.leading = 16
    section_title_style.spaceBefore = 14
    section_title_style.spaceAfter = 8
    section_title_style.textColor = colors.HexColor("#222222")
    section_title_style.alignment = TA_LEFT

    right_style = styles["Normal"].clone("RightAligned")
    right_style.fontName = "SegoeUI"
    right_style.fontSize = 9
    right_style.leading = 12
    right_style.alignment = TA_RIGHT

    ANCHOR_MAIN_TEXT = "main_text"
    ANCHOR_LONG_MATCHES = "long_matches"
    ANCHOR_SIMILAR_DOCS = "similar_docs"

    def create_similarity_gauge(value: float) -> BytesIO:
        value = max(0, min(100, value))

        fig, ax = plt.subplots(figsize=(6, 3))
        fig.patch.set_facecolor("white")

        center = (0, 0)
        radius = 1.0
        thickness = 0.35

        def angle(pct):
            # 0% = left (180°), 100% = right (0°)
            return 180 - (pct / 100) * 180

        # Zones
        zones = [
            (0, 10, "#2ecc71"),  # Green
            (10, 25, "#f1c40f"),  # Yellow
            (25, 100, "#e74c3c"),  # Red
        ]

        for start, end, color in zones:
            ax.add_patch(
                Wedge(
                    center,
                    radius,
                    angle(end),
                    angle(start),
                    width=thickness,
                    facecolor=color,
                    edgecolor="none",
                )
            )

        # Interval labels
        labels = [0, 10, 25, 100]
        label_radius = radius + 0.12

        for pct in labels:
            ang = math.radians(angle(pct))
            x = label_radius * math.cos(ang)
            y = label_radius * math.sin(ang)

            ax.text(
                x,
                y,
                f"{pct}",
                ha="center",
                va="center",
                fontsize=11 if pct in (10, 25) else 9,
                fontweight="bold" if pct in (10, 25) else "normal",
                color="#333333",
                fontfamily="Segoe UI",
            )

        # Needle
        a = math.radians(angle(value))
        ax.plot([0, 0.75 * math.cos(a)], [0, 0.75 * math.sin(a)], lw=3, color="black")

        # Pin
        ax.add_patch(Circle((0, 0), 0.05, color="black"))

        # Text
        ax.text(
            0,
            -0.25,
            f"{value:.2f}%",
            ha="center",
            va="center",
            fontsize=22,
            fontweight="bold",
            fontfamily="Segoe UI",
        )

        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.35, 1.05)  # semi-circle

        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=200, bbox_inches="tight", transparent=True)
        plt.close()
        buf.seek(0)

        return buf

    def draw_ico(canvas, ico_path, x, y, size=16):
        img = PILImage.open(ico_path)
        img = img.resize((size, size), PILImage.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_reader = ImageReader(buffer)
        canvas.drawImage(img_reader, x, y, width=size, height=size, mask="auto")

    def header_footer(canvas, doc):
        page_width, page_height = A4

        # Logo and text
        logo_size = 24
        spacing = 6

        text = APP_NAME
        canvas.setFont("SegoeUI-Bold", 16)
        text_width = canvas.stringWidth(text, "SegoeUI-Bold", 16)

        total_width = logo_size + spacing + text_width

        x_start = (page_width - total_width) / 2
        y = page_height - doc.topMargin + 5

        draw_ico(canvas, ICO_PATH, x_start, y, size=logo_size)

        canvas.drawString(x_start + logo_size + spacing, y + 2, text)

        # Separator
        line_y = page_height - doc.topMargin - 4
        canvas.setLineWidth(0.3)
        canvas.line(doc.leftMargin, line_y, page_width - doc.rightMargin, line_y)

        # Footer: prints page number at the bottom of each page
        page_num = canvas.getPageNumber()
        text = f"{page_num}"
        canvas.setFont("SegoeUI", 10)
        canvas.drawRightString(A4[0] / 2, 1 * cm, text)

    def compute_extension(words, i, index, pos, n):
        j = i
        norm_buffer = []
        consumed = 0
        # build initial n-gram
        while j < len(words) and len(norm_buffer) < n:
            w = normalize_text(words[j])
            if w:
                norm_buffer.append(w)
            j += 1
            consumed += 1

        if len(norm_buffer) < n:
            return 0

        extension = consumed

        # Extend by one word at a time
        i_pos = 0
        while j < len(words):
            w = normalize_text(words[j])
            if w:
                norm_buffer.append(w)
                if len(norm_buffer) > n:
                    norm_buffer.pop(0)

                chunk = " ".join(norm_buffer)

                if chunk in index and any(
                    e[1] == pos + i_pos + 1 for e in index[chunk]
                ):
                    i_pos += 1
                    extension += 1
                    j += 1
                else:
                    break
            else:
                # neglect empty words
                extension += 1
                j += 1

        return extension

    # Assign unique highlight colors to each compared PDF
    pdf_files = list(pdf_ngram_index.keys())
    colors_list = [
        colors.yellow,
        colors.lime,
        colors.cyan,
        colors.orange,
        colors.pink,
        colors.lightblue,
        colors.violet,
    ]

    color_map = {
        pdf: colors_list[i % len(colors_list)] for i, pdf in enumerate(pdf_files)
    }

    story = []
    story.append(Paragraph('<a name="top"/>', normal_style))
    story.append(
        Paragraph("<b>" + translator.gettext("title_report") + "</b>", title_style)
    )
    story.append(Spacer(1, 10))

    # Show a gauge with overall similarity score, if enabled
    if show_statistics:
        gauge_buffer = create_similarity_gauge(overall_similarity)
        gauge_img = Image(gauge_buffer, width=9 * cm, height=6 * cm)
        gauge_img.hAlign = "CENTER"

        story.append(gauge_img)
        story.append(Spacer(1, 12))

    story.append(Spacer(1, 8))

    # Build index of sections
    index_items = []
    if show_more_similar_sentences or show_references:
        index_items.append((ANCHOR_MAIN_TEXT, translator.gettext("main_text")))

    if show_more_similar_sentences:
        index_items.append(
            (ANCHOR_LONG_MATCHES, translator.gettext("list_more_similar_sentences"))
        )

    if show_references:
        index_items.append(
            (ANCHOR_SIMILAR_DOCS, translator.gettext("list_similar_documents"))
        )

    if index_items:
        story.append(
            Paragraph(f"<b>{translator.gettext('index')}</b>", section_title_style)
        )
        story.append(Spacer(1, 6))
        for anchor, label in index_items:
            story.append(
                Paragraph(
                    f'<a href="#{anchor}" color="blue">• {label}</a>',
                    normal_style,
                )
            )
        story.append(Spacer(1, 14))

    story.append(
        Paragraph(
            f'<a name="{ANCHOR_MAIN_TEXT}"/><b>{translator.gettext("main_text")}</b>',
            section_title_style,
        )
    )
    story.append(Spacer(1, 6))

    # Track used PDFs and cumulative similarity
    used_pdfs = set()
    pdf_order = {}
    cumulative_matched_ngrams = set()
    long_matches = []

    # Process each paragraph of the target document
    for _, row in target_df.iterrows():
        paragraph = row["paragraph"]
        words = paragraph.split()

        # Compute all n-grams for the paragraph
        para_ngrams = get_ngrams(" ".join(words), n=n)

        # Collect all matched n-grams for cumulative statistics
        matched_ngrams = set()
        for ng, _ in para_ngrams:
            for pdf_dict in pdf_ngram_index.values():
                if ng in pdf_dict:
                    matched_ngrams.add(ng)
                    break

        cumulative_matched_ngrams |= matched_ngrams
        cumulative_percent = (
            len(cumulative_matched_ngrams) / len(target_ngram_index) * 100
        )

        highlighted = []
        i = 0
        last_pdf = None
        last_color = None
        last_num_label = None
        last_page = None
        last_target_end = None
        buffer = []

        while i < len(words):
            matched = False
            if i + n <= len(words):
                # build initial n-gram
                j = i
                norm_buffer = []
                while j < len(words) and len(norm_buffer) < n:
                    w = normalize_text(words[j])
                    if w:
                        norm_buffer.append(w)
                    j += 1
                chunk = " ".join(norm_buffer)
                # Collect all candidates
                candidates = []
                for pdf_path, index in pdf_ngram_index.items():
                    if chunk in index:
                        for page_num, pos in index[chunk]:
                            candidates.append((pdf_path, index, page_num, pos))

                # Select the one with the longest extension
                best = None
                best_extension = 0

                for pdf_path, index, page_num, pos in candidates:
                    ext = compute_extension(words, i, index, pos, n)
                    if ext > best_extension:
                        best_extension = ext
                        best = (pdf_path, index, page_num, pos)

                # Apply the best match
                if best:
                    pdf_path, index, page_num, pos = best
                    extension = best_extension

                    if extension >= more_similar_ngram:
                        matched_text = " ".join(words[i : i + extension])

                        long_matches.append(
                            {
                                "text": matched_text,
                                "num_words": extension,
                                "pdf": pdf_path,
                                "page": page_num,
                                "paragraph": paragraph,
                            }
                        )

                    color = (
                        color_map.get(pdf_path, colors.yellow)
                        if show_references
                        else colors.yellow
                    )

                    if pdf_path not in pdf_order:
                        pdf_order[pdf_path] = len(pdf_order) + 1

                    if show_references:
                        encoded_path = urllib.parse.quote(
                            pdf_path.replace("\\", "/"), safe="/"
                        )
                        if page_num and show_pagenum:
                            link = f"file:///{encoded_path}#page={page_num}"
                        else:
                            link = f"file:///{encoded_path}"

                        num_label = (
                            f'<a href="{link}" color="blue">'
                            f"[{pdf_order[pdf_path]}]</a>"
                        )
                    else:
                        num_label = ""

                    if (
                        pdf_path == last_pdf
                        and page_num == last_page
                        and last_target_end == i
                    ):
                        buffer.extend(words[i : i + extension])
                        last_target_end = i + extension
                    else:
                        if buffer:
                            highlighted.append(
                                f"{last_num_label} "
                                f'<font backcolor="{last_color.hexval()}">'
                                f'{" ".join(buffer)}</font>'
                            )
                            used_pdfs.add(last_pdf)

                        buffer = words[i : i + extension]
                        last_pdf = pdf_path
                        last_page = page_num
                        last_color = color
                        last_num_label = num_label
                        last_target_end = i + extension

                    i += extension
                    matched = True

            if not matched:
                if buffer:
                    highlighted.append(
                        f"{last_num_label} "
                        f'<font backcolor="{last_color.hexval()}">'
                        f'{" ".join(buffer)}</font>'
                    )
                    used_pdfs.add(last_pdf)
                    buffer = []
                    last_pdf = None
                    last_pdf = None
                    last_page = None
                    last_color = None
                    last_num_label = None
                    last_target_end = None

                highlighted.append(words[i])
                i += 1

        # Flush remaining highlight buffer
        if buffer:
            highlighted.append(
                f'{last_num_label} <font backcolor="{last_color.hexval()}">{" ".join(buffer)}</font>'
            )
            used_pdfs.add(last_pdf)

        # Rebuild paragraph text
        para_text = " ".join(highlighted)

        # Append cumulative percentage, if enabled
        if show_statistics:
            para_text = (
                para_text
                + f"  <b>({translator.gettext('cumulated_percentage')}: {cumulative_percent:.2f}%)</b>"
            )
        story.append(Paragraph(para_text, normal_style))
        story.append(Spacer(1, 4))

    story.append(
        Paragraph(
            f'<a href="#top" color="blue">↑ {translator.gettext("back_to_top")}</a>',
            right_style,
        )
    )

    if show_more_similar_sentences:
        story.append(Spacer(1, 12))
        story.append(
            Paragraph(
                f'<a name="{ANCHOR_LONG_MATCHES}"/><b>{translator.gettext("list_more_similar_sentences")}</b>',
                section_title_style,
            )
        )

        if long_matches:
            story.append(Spacer(1, 6))
            long_matches = sorted(
                long_matches,
                key=lambda x: x["num_words"],
                reverse=True,
            )

            for m in long_matches:
                pdf_name = os.path.basename(m["pdf"])
                story.append(
                    Paragraph(
                        m["text"],
                        normal_style,
                    )
                )
                if show_statistics:
                    story.append(
                        Paragraph(
                            f"<font size='9'><b>({m['num_words']} {translator.gettext('words')})</b></font>",
                            normal_style,
                        )
                    )
                story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 6))
            story.append(
                Paragraph(
                    f'{translator.gettext("no_more_similar_sentences").format(more_similar_ngram=more_similar_ngram)}',
                    normal_style,
                )
            )
            story.append(Spacer(1, 6))
        story.append(
            Paragraph(
                f'<a href="#top" color="blue">↑ {translator.gettext("back_to_top")}</a>',
                right_style,
            )
        )

    # Build legend of referenced documents
    if show_references:
        story.append(Spacer(1, 12))
        story.append(
            Paragraph(
                f'<a name="{ANCHOR_SIMILAR_DOCS}"/><b>{translator.gettext("list_similar_documents")}</b>',
                section_title_style,
            )
        )
        used_pdfs = [p for p in pdf_order if p in used_pdfs]

        # Sort PDFs by score if available
        if per_pdf_scores:
            sorted_pdfs = sorted(
                [(p, per_pdf_scores.get(p, 0)) for p in used_pdfs],
                key=lambda x: x[1],
                reverse=True,
            )
        else:
            sorted_pdfs = [(p, 0) for p in used_pdfs]

        # Build legend table
        for pdf_path, perc in sorted_pdfs:
            index = pdf_ngram_index[pdf_path]
            pdf_name = os.path.basename(pdf_path)
            color = color_map[pdf_path]
            pdf_number = pdf_order[pdf_path]
            encoded_path = urllib.parse.quote(pdf_path.replace("\\", "/"), safe="/")
            link = f"file:///{encoded_path}"
            legend_html = (
                f'<a href="{link}" color="blue">[{pdf_number}]</a> '
                f'<font backcolor="{color.hexval()}">{pdf_name}</font> '
            )
            if show_statistics:
                legend_html = legend_html + f"<b>({perc:.2f}%)</b>"
            legend = Paragraph(legend_html, normal_style)
            table = Table([[legend]], colWidths=[16 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 2))

        story.append(
            Paragraph(
                f'<a href="#top" color="blue">↑ {translator.gettext("back_to_top")}</a>',
                right_style,
            )
        )
    # Generate the final PDF
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return output_pdf
