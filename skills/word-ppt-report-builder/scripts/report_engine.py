#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_engine.py - Bộ công cụ tự động hóa Báo cáo Word (.docx) & PowerPoint (.pptx)
Chuẩn tiếng Việt Unicode, hỗ trợ chế độ Hiện đại (Modern Corporate/Technical) & Nghị định 30/2020/NĐ-CP.
"""

from __future__ import annotations
import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Inches, Pt, RGBColor

from pptx import Presentation
from pptx.dml.color import RGBColor as PptRGB
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches as PptInches, Pt as PptPt


# ==============================================================================
# BẢNG MÀU CHUẨN (EXECUTIVE NAVY & SLATE PALETTE)
# ==============================================================================
PALETTE = {
    "primary": (27, 54, 93),       # #1B365D - Navy đậm chuyên nghiệp
    "secondary": (44, 82, 130),    # #2C5282 - Slate Blue
    "accent": (217, 119, 6),       # #D97706 - Amber Gold điểm nhấn
    "success": (22, 101, 52),      # #166534 - Xanh lá đạt chuẩn
    "danger": (185, 28, 28),       # #B91C1C - Đỏ cảnh báo
    "dark_text": (30, 41, 59),     # #1E293B - Chữ chính
    "muted_text": (100, 116, 139), # #64748B - Chữ phụ / chú thích
    "light_bg": (244, 247, 250),   # #F4F7FA - Nền bảng xen kẽ / card
    "card_border": (203, 213, 225),# #CBD5E1 - Viền nhẹ
    "white": (255, 255, 255),
}

HEX_PALETTE = {
    "primary": "1B365D",
    "secondary": "2C5282",
    "accent": "D97706",
    "success": "166534",
    "danger": "B91C1C",
    "light_bg": "F4F7FA",
    "callout_info": "EDF2F7",
    "callout_warn": "FEF3C7",
    "callout_success": "DCFCE7",
    "border": "CBD5E1",
}


def _docx_rgb(key: str) -> RGBColor:
    r, g, b = PALETTE[key]
    return RGBColor(r, g, b)


def _ppt_rgb(key: str) -> PptRGB:
    r, g, b = PALETTE[key]
    return PptRGB(r, g, b)


def _safe_save_path(target_path: str | Path) -> Path:
    """Đảm bảo thư mục tồn tại và xử lý trường hợp file đang bị khóa do mở trong Word/PowerPoint."""
    path = Path(target_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# ==============================================================================
# 1. WORD REPORT BUILDER (.DOCX)
# ==============================================================================
class WordReportBuilder:
    """
    Bộ khởi tạo Báo cáo Word (.docx) chuẩn tiếng Việt.
    Hỗ trợ 2 chế độ:
      - mode="modern": Báo cáo Kỹ thuật / Doanh nghiệp / Nghiên cứu hiện đại
      - mode="nd30"  : Chuẩn hành chính Nghị định 30/2020/NĐ-CP (Times New Roman 13pt, lề chuẩn)
    """

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        author: str = "",
        mode: str = "modern",
        font_name: Optional[str] = None,
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.mode = mode.lower().strip()
        self.font_name = font_name or ("Times New Roman" if self.mode == "nd30" else "Segoe UI")
        self.doc = Document()
        self._configure_page_and_styles()
        self._add_header_footer()

    def _set_run_font(self, run_or_style, font_name: str, size_pt: float, bold: bool = False, italic: bool = False, color_rgb: Optional[RGBColor] = None) -> None:
        font = run_or_style.font
        font.name = font_name
        font.size = Pt(size_pt)
        font.bold = bold
        font.italic = italic
        if color_rgb is not None:
            font.color.rgb = color_rgb

        rPr = run_or_style._element.get_or_add_rPr()
        rFonts = rPr.get_or_add_rFonts()
        for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rFonts.set(qn(attr), font_name)

    def _configure_page_and_styles(self) -> None:
        section = self.doc.sections[0]
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)

        if self.mode == "nd30":
            section.top_margin = Cm(2.0)
            section.bottom_margin = Cm(2.0)
            section.left_margin = Cm(3.0)
            section.right_margin = Cm(1.5)
            body_pt = 13.0
        else:
            section.top_margin = Cm(2.2)
            section.bottom_margin = Cm(2.2)
            section.left_margin = Cm(2.8)
            section.right_margin = Cm(2.0)
            body_pt = 11.5

        # Cấu hình Normal style
        normal_style = self.doc.styles["Normal"]
        self._set_run_font(normal_style, self.font_name, body_pt, color_rgb=_docx_rgb("dark_text"))
        normal_style.paragraph_format.line_spacing = 1.3
        normal_style.paragraph_format.space_after = Pt(6)
        if self.mode == "nd30":
            normal_style.paragraph_format.first_line_indent = Cm(1.27)

        # Cấu hình Heading 1, 2, 3
        h_configs = [
            ("Heading 1", 14.0 if self.mode == "nd30" else 14.5, True, False, "primary", 12, 6),
            ("Heading 2", 13.5 if self.mode == "nd30" else 13.0, True, False, "secondary", 10, 4),
            ("Heading 3", 13.0 if self.mode == "nd30" else 12.0, True, True, "dark_text", 6, 3),
        ]
        for style_name, pt_size, is_bold, is_italic, color_key, sp_before, sp_after in h_configs:
            st = self.doc.styles[style_name]
            self._set_run_font(st, self.font_name, pt_size, bold=is_bold, italic=is_italic, color_rgb=_docx_rgb(color_key))
            st.paragraph_format.space_before = Pt(sp_before)
            st.paragraph_format.space_after = Pt(sp_after)
            st.paragraph_format.first_line_indent = Cm(0)
            st.paragraph_format.keep_with_next = True

    def _add_header_footer(self) -> None:
        section = self.doc.sections[0]
        section.different_first_page_header_footer = True

        # Header cho các trang nội dung
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run(self.title)
        self._set_run_font(hrun, self.font_name, 9.0, italic=True, color_rgb=_docx_rgb("muted_text"))

        # Footer kèm đánh số trang tự động XML
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        prefix_Text = f"{self.author}  |  Trang " if self.author else "Trang "
        frun = fp.add_run(prefix_Text)
        self._set_run_font(frun, self.font_name, 9.0, color_rgb=_docx_rgb("muted_text"))
        self._append_xml_field(fp, "PAGE")
        mid_run = fp.add_run(" / ")
        self._set_run_font(mid_run, self.font_name, 9.0, color_rgb=_docx_rgb("muted_text"))
        self._append_xml_field(fp, "NUMPAGES")

    def _append_xml_field(self, paragraph, field_name: str) -> None:
        run = paragraph.add_run()
        self._set_run_font(run, self.font_name, 9.0, color_rgb=_docx_rgb("muted_text"))
        fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
        instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> %s </w:instrText>' % (nsdecls("w"), field_name))
        fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
        fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run._r.append(fldChar3)

    @staticmethod
    def _set_cell_shading(cell, hex_color: str) -> None:
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    @staticmethod
    def _set_cell_margins(cell, top_dxa: int = 120, bottom_dxa: int = 120, left_dxa: int = 160, right_dxa: int = 160) -> None:
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement("w:tcMar")
        for side, val in (("top", top_dxa), ("bottom", bottom_dxa), ("left", left_dxa), ("right", right_dxa)):
            node = OxmlElement(f"w:{side}")
            node.set(qn("w:w"), str(val))
            node.set(qn("w:type"), "dxa")
            tcMar.append(node)
        tcPr.append(tcMar)

    @staticmethod
    def _set_table_borders(table, border_color: str = "CBD5E1", hide_all: bool = False) -> None:
        tblPr = table._tbl.tblPr
        if hide_all:
            borders = parse_xml(
                f'<w:tblBorders {nsdecls("w")}>'
                '<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>'
                '<w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/>'
                "</w:tblBorders>"
            )
        else:
            borders = parse_xml(
                f'<w:tblBorders {nsdecls("w")}>'
                f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
                f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{HEX_PALETTE["primary"]}"/>'
                '<w:left w:val="none"/>'
                '<w:right w:val="none"/>'
                f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
                '<w:insideV w:val="none"/>'
                "</w:tblBorders>"
            )
        tblPr.append(borders)

    def add_cover_header(
        self,
        org_name: str = "ĐƠN VỊ CHỦ QUẢN / PHÒNG BAN",
        doc_code: str = "Số: 01/BC-KT",
        location_date: Optional[str] = None,
    ) -> None:
        """Thêm phần tiêu đề đầu báo cáo (Chuẩn Quốc hiệu NĐ30 hoặc Header Banner hiện đại)."""
        if not location_date:
            now = datetime.datetime.now()
            location_date = f"Ngày {now.day:02d} tháng {now.month:02d} năm {now.year}"

        if self.mode == "nd30":
            hdr_tbl = self.doc.add_table(rows=1, cols=2)
            hdr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr_tbl.autofit = False
            self._set_table_borders(hdr_tbl, hide_all=True)

            widths = [Cm(7.2), Cm(9.3)]
            for idx, w in enumerate(widths):
                hdr_tbl.columns[idx].width = w
                hdr_tbl.rows[0].cells[idx].width = w

            # Cột trái: Cơ quan ban hành
            c_left = hdr_tbl.rows[0].cells[0]
            p1 = c_left.paragraphs[0]
            p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p1.paragraph_format.first_line_indent = Cm(0)
            p1.paragraph_format.space_after = Pt(2)
            r1 = p1.add_run(org_name.upper() + "\n")
            self._set_run_font(r1, self.font_name, 12.0, bold=True)
            r2 = p1.add_run(doc_code)
            self._set_run_font(r2, self.font_name, 12.0)

            # Cột phải: Quốc hiệu & Tiêu ngữ
            c_right = hdr_tbl.rows[0].cells[1]
            p2 = c_right.paragraphs[0]
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p2.paragraph_format.first_line_indent = Cm(0)
            p2.paragraph_format.space_after = Pt(2)
            rq1 = p2.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n")
            self._set_run_font(rq1, self.font_name, 12.0, bold=True)
            rq2 = p2.add_run("Độc lập - Tự do - Hạnh phúc\n")
            self._set_run_font(rq2, self.font_name, 13.0, bold=True)
            rq3 = p2.add_run("─────────────────\n" + location_date)
            self._set_run_font(rq3, self.font_name, 11.5, italic=True)

            # Tiêu đề chính căn giữa
            tp = self.doc.add_paragraph()
            tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            tp.paragraph_format.first_line_indent = Cm(0)
            tp.paragraph_format.space_before = Pt(16)
            tp.paragraph_format.space_after = Pt(8)
            tr = tp.add_run(self.title.upper())
            self._set_run_font(tr, self.font_name, 15.0, bold=True, color_rgb=_docx_rgb("primary"))
            if self.subtitle:
                sub_r = tp.add_run("\n" + self.subtitle)
                self._set_run_font(sub_r, self.font_name, 13.0, italic=True, color_rgb=_docx_rgb("dark_text"))
        else:
            # Banner hiện đại cho báo cáo kỹ thuật / doanh nghiệp
            banner = self.doc.add_table(rows=1, cols=1)
            banner.alignment = WD_TABLE_ALIGNMENT.CENTER
            banner.autofit = False
            self._set_table_borders(banner, hide_all=True)
            cell = banner.rows[0].cells[0]
            cell.width = Cm(16.2)
            self._set_cell_shading(cell, HEX_PALETTE["primary"])
            self._set_cell_margins(cell, top_dxa=240, bottom_dxa=240, left_dxa=280, right_dxa=280)

            p_meta = cell.paragraphs[0]
            p_meta.paragraph_format.first_line_indent = Cm(0)
            p_meta.paragraph_format.space_after = Pt(4)
            r_meta = p_meta.add_run(f"{org_name.upper()}   |   {doc_code}   |   {location_date}")
            self._set_run_font(r_meta, self.font_name, 9.5, bold=True, color_rgb=RGBColor(219, 234, 254))

            p_title = cell.add_paragraph()
            p_title.paragraph_format.first_line_indent = Cm(0)
            p_title.paragraph_format.space_after = Pt(4)
            r_title = p_title.add_run(self.title.upper())
            self._set_run_font(r_title, self.font_name, 17.5, bold=True, color_rgb=_docx_rgb("white"))

            if self.subtitle:
                p_sub = cell.add_paragraph()
                p_sub.paragraph_format.first_line_indent = Cm(0)
                p_sub.paragraph_format.space_after = Pt(2)
                r_sub = p_sub.add_run(self.subtitle)
                self._set_run_font(r_sub, self.font_name, 11.0, italic=True, color_rgb=RGBColor(226, 232, 240))

            if self.author:
                p_auth = cell.add_paragraph()
                p_auth.paragraph_format.first_line_indent = Cm(0)
                p_auth.paragraph_format.space_after = Pt(0)
                r_auth = p_auth.add_run(f"Thực hiện: {self.author}")
                self._set_run_font(r_auth, self.font_name, 9.5, color_rgb=RGBColor(253, 224, 71))

            spacer = self.doc.add_paragraph()
            spacer.paragraph_format.space_after = Pt(4)

    def add_heading(self, text: str, level: int = 1) -> None:
        level = max(1, min(3, level))
        display_text = text.upper() if (level == 1 and self.mode == "nd30") else text
        h = self.doc.add_heading(display_text, level=level)
        h.paragraph_format.first_line_indent = Cm(0)
        for run in h.runs:
            color_key = "primary" if level == 1 else ("secondary" if level == 2 else "dark_text")
            pt_size = 14.0 if level == 1 else (13.0 if level == 2 else 12.0)
            self._set_run_font(run, self.font_name, pt_size, bold=True, italic=(level == 3), color_rgb=_docx_rgb(color_key))

    def add_paragraph(self, text: str, bold_prefix: str = "", align_justify: bool = True) -> None:
        p = self.doc.add_paragraph()
        if align_justify:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        body_pt = 13.0 if self.mode == "nd30" else 11.5
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            self._set_run_font(rb, self.font_name, body_pt, bold=True, color_rgb=_docx_rgb("dark_text"))
        r = p.add_run(text)
        self._set_run_font(r, self.font_name, body_pt, color_rgb=_docx_rgb("dark_text"))

    def add_bullets(self, items: Sequence[str | Tuple[str, str]]) -> None:
        """Thêm danh sách gạch đầu dòng. Mỗi phần tử có thể là chuỗi hoặc tuple (tiêu_đề_đậm, nội_dung)."""
        body_pt = 13.0 if self.mode == "nd30" else 11.5
        for item in items:
            p = self.doc.add_paragraph(style="List Bullet")
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(4)
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                rb = p.add_run(f"{item[0]}: ")
                self._set_run_font(rb, self.font_name, body_pt, bold=True, color_rgb=_docx_rgb("primary"))
                rt = p.add_run(str(item[1]))
                self._set_run_font(rt, self.font_name, body_pt, color_rgb=_docx_rgb("dark_text"))
            else:
                rt = p.add_run(str(item))
                self._set_run_font(rt, self.font_name, body_pt, color_rgb=_docx_rgb("dark_text"))

    def add_callout(self, title: str, content: str, tone: str = "info") -> None:
        """Tạo khối hộp nhấn mạnh (Executive Summary / Cảnh báo / Kết luận)."""
        tone_map = {
            "info": (HEX_PALETTE["primary"], HEX_PALETTE["callout_info"]),
            "warn": (HEX_PALETTE["accent"], HEX_PALETTE["callout_warn"]),
            "success": (HEX_PALETTE["success"], HEX_PALETTE["callout_success"]),
        }
        border_hex, bg_hex = tone_map.get(tone, tone_map["info"])

        tbl = self.doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.rows[0].cells[0]
        cell.width = Cm(16.2)
        self._set_cell_shading(cell, bg_hex)
        self._set_cell_margins(cell, top_dxa=140, bottom_dxa=140, left_dxa=220, right_dxa=180)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>'
            '<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
            "</w:tcBorders>"
        )
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(2)
        rt = p.add_run(title + "\n")
        self._set_run_font(rt, self.font_name, 11.5, bold=True, color_rgb=_docx_rgb("primary"))
        rc = p.add_run(content)
        self._set_run_font(rc, self.font_name, 11.0, color_rgb=_docx_rgb("dark_text"))

        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(2)

    def add_kpi_summary(self, kpis: Sequence[Tuple[str, str, str]]) -> None:
        """Hiển thị hàng thẻ chỉ số KPI (Tên chỉ số, Giá trị lớn, Ghi chú/So sánh)."""
        if not kpis:
            return
        cols = len(kpis)
        tbl = self.doc.add_table(rows=1, cols=cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        self._set_table_borders(tbl, hide_all=True)

        total_w = 16.2
        col_w = total_w / cols
        for idx, (label, val, delta) in enumerate(kpis):
            cell = tbl.rows[0].cells[idx]
            cell.width = Cm(col_w)
            self._set_cell_shading(cell, HEX_PALETTE["light_bg"])
            self._set_cell_margins(cell, top_dxa=140, bottom_dxa=140, left_dxa=140, right_dxa=140)
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.append(
                parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:top w:val="single" w:sz="16" w:space="0" w:color="{HEX_PALETTE["primary"]}"/>'
                    f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{HEX_PALETTE["border"]}"/>'
                    '<w:left w:val="single" w:sz="4" w:space="0" w:color="FFFFFF"/>'
                    '<w:right w:val="single" w:sz="4" w:space="0" w:color="FFFFFF"/>'
                    "</w:tcBorders>"
                )
            )
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(2)
            r_lbl = p.add_run(label.upper() + "\n")
            self._set_run_font(r_lbl, self.font_name, 9.0, bold=True, color_rgb=_docx_rgb("muted_text"))
            r_val = p.add_run(str(val) + "\n")
            self._set_run_font(r_val, self.font_name, 16.0, bold=True, color_rgb=_docx_rgb("primary"))
            r_del = p.add_run(str(delta))
            self._set_run_font(r_del, self.font_name, 9.5, italic=True, color_rgb=_docx_rgb("success"))

        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(4)

    def add_styled_table(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        col_widths_cm: Optional[Sequence[float]] = None,
        alignments: Optional[Sequence[str]] = None,
        caption: str = "",
    ) -> None:
        """Tạo bảng dữ liệu chuyên nghiệp có Header lặp lại qua trang và Zebra Striping."""
        num_cols = len(headers)
        if not col_widths_cm or len(col_widths_cm) != num_cols:
            col_widths_cm = [16.2 / num_cols] * num_cols

        tbl = self.doc.add_table(rows=1 + len(rows), cols=num_cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        self._set_table_borders(tbl)

        # Header Row
        hdr_row = tbl.rows[0]
        trPr = hdr_row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        for c_idx, h_text in enumerate(headers):
            cell = hdr_row.cells[c_idx]
            cell.width = Cm(col_widths_cm[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            self._set_cell_shading(cell, HEX_PALETTE["primary"])
            self._set_cell_margins(cell, top_dxa=110, bottom_dxa=110, left_dxa=120, right_dxa=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(h_text))
            self._set_run_font(run, self.font_name, 10.5, bold=True, color_rgb=_docx_rgb("white"))

        # Data Rows
        align_map = {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "right": WD_ALIGN_PARAGRAPH.RIGHT,
        }
        for r_idx, row_data in enumerate(rows):
            row = tbl.rows[r_idx + 1]
            r_trPr = row._tr.get_or_add_trPr()
            r_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            bg_color = HEX_PALETTE["light_bg"] if r_idx % 2 == 1 else "FFFFFF"

            for c_idx in range(num_cols):
                val = row_data[c_idx] if c_idx < len(row_data) else ""
                cell = row.cells[c_idx]
                cell.width = Cm(col_widths_cm[c_idx])
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                self._set_cell_shading(cell, bg_color)
                self._set_cell_margins(cell, top_dxa=90, bottom_dxa=90, left_dxa=120, right_dxa=120)

                p = cell.paragraphs[0]
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.space_after = Pt(0)
                if alignments and c_idx < len(alignments):
                    p.alignment = align_map.get(alignments[c_idx].lower(), WD_ALIGN_PARAGRAPH.LEFT)
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                run = p.add_run(str(val))
                self._set_run_font(run, self.font_name, 10.5, bold=(c_idx == 0), color_rgb=_docx_rgb("dark_text"))

        if caption:
            cp = self.doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.first_line_indent = Cm(0)
            cp.paragraph_format.space_before = Pt(4)
            cp.paragraph_format.space_after = Pt(8)
            cr = cp.add_run(caption)
            self._set_run_font(cr, self.font_name, 10.0, italic=True, color_rgb=_docx_rgb("muted_text"))

    def add_figure(self, image_path: str | Path, caption: str = "", width_cm: float = 15.2) -> None:
        img_p = Path(image_path)
        if not img_p.exists():
            return
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run()
        run.add_picture(str(img_p), width=Cm(width_cm))

        if caption:
            cp = self.doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.first_line_indent = Cm(0)
            cp.paragraph_format.space_after = Pt(8)
            cr = cp.add_run(caption)
            self._set_run_font(cr, self.font_name, 10.0, italic=True, color_rgb=_docx_rgb("muted_text"))

    def add_signature_block(
        self,
        left_title: str = "NGƯỜI LẬP BÁO CÁO",
        left_name: str = "",
        right_title: str = "THỦ TRƯỞNG ĐƠN VỊ / PHÊ DUYỆT",
        right_name: str = "",
    ) -> None:
        sig_tbl = self.doc.add_table(rows=1, cols=2)
        sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        sig_tbl.autofit = False
        self._set_table_borders(sig_tbl, hide_all=True)

        for idx, (title_txt, name_txt) in enumerate([(left_title, left_name), (right_title, right_name)]):
            cell = sig_tbl.rows[0].cells[idx]
            cell.width = Cm(8.1)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(12)
            r1 = p.add_run(title_txt.upper() + "\n")
            self._set_run_font(r1, self.font_name, 11.5, bold=True, color_rgb=_docx_rgb("dark_text"))
            r2 = p.add_run("(Ký, ghi rõ họ tên)\n\n\n\n")
            self._set_run_font(r2, self.font_name, 10.0, italic=True, color_rgb=_docx_rgb("muted_text"))
            if name_txt:
                r3 = p.add_run(name_txt)
                self._set_run_font(r3, self.font_name, 11.5, bold=True, color_rgb=_docx_rgb("primary"))

    def save(self, output_path: str | Path) -> Path:
        target = _safe_save_path(output_path)
        try:
            self.doc.save(str(target))
            return target
        except PermissionError:
            alt = target.with_name(f"{target.stem}_new{target.suffix}")
            self.doc.save(str(alt))
            return alt


# ==============================================================================
# 2. POWERPOINT REPORT BUILDER (.PPTX)
# ==============================================================================
class PPTReportBuilder:
    """
    Bộ khởi tạo Slide Thuyết trình PowerPoint 16:9 Widescreen (`13.333 x 7.5 inches`).
    Tự động áp dụng bố cục Action Title (McKinsey/BCG style), KPI Cards, Two-Column, Data Table.
    """

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        author: str = "",
        font_name: str = "Segoe UI",
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.font_name = font_name
        self.prs = Presentation()
        self.prs.slide_width = PptInches(13.333)
        self.prs.slide_height = PptInches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        self.slide_count = 0

    def _add_slide_chrome(self, slide, section_tag: str, action_title: str) -> None:
        """Thêm thanh Header, Action Title và Footer đồng nhất cho mọi slide nội dung."""
        self.slide_count += 1

        # Nền sáng sạch
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, PptInches(0), PptInches(0), PptInches(13.333), PptInches(7.5)
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = PptRGB(248, 250, 252)
        bg.line.fill.background()

        # Thanh Top Accent
        top_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, PptInches(0), PptInches(0), PptInches(13.333), PptInches(0.12)
        )
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = _ppt_rgb("primary")
        top_bar.line.fill.background()

        # Nhãn Section Tag
        tb_tag = slide.shapes.add_textbox(PptInches(0.6), PptInches(0.24), PptInches(12.1), PptInches(0.32))
        tf_tag = tb_tag.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        r_tag = p_tag.add_run()
        r_tag.text = section_tag.upper()
        r_tag.font.name = self.font_name
        r_tag.font.size = PptPt(10.5)
        r_tag.font.bold = True
        r_tag.font.color.rgb = _ppt_rgb("accent")

        # Action Title (Nhận định chiến lược/kỹ thuật chính của slide)
        tb_title = slide.shapes.add_textbox(PptInches(0.6), PptInches(0.52), PptInches(12.1), PptInches(0.85))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        r_title = p_title.add_run()
        r_title.text = action_title
        r_title.font.name = self.font_name
        r_title.font.size = PptPt(22 if len(action_title) > 75 else 24)
        r_title.font.bold = True
        r_title.font.color.rgb = _ppt_rgb("primary")

        # Đường kẻ phân cách dưới tiêu đề
        sep = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, PptInches(0.6), PptInches(1.38), PptInches(12.133), PptInches(0.025)
        )
        sep.fill.solid()
        sep.fill.fore_color.rgb = _ppt_rgb("card_border")
        sep.line.fill.background()

        # Footer
        tb_foot = slide.shapes.add_textbox(PptInches(0.6), PptInches(7.05), PptInches(12.133), PptInches(0.35))
        tf_foot = tb_foot.text_frame
        p_foot = tf_foot.paragraphs[0]
        r_foot = p_foot.add_run()
        r_foot.text = f"{self.title}   |   {self.author}   |   Slide {self.slide_count}"
        r_foot.font.name = self.font_name
        r_foot.font.size = PptPt(9.5)
        r_foot.font.color.rgb = _ppt_rgb("muted_text")

    def add_title_slide(self, badge_text: str = "BÁO CÁO CHUYÊN ĐỀ & PHÂN TÍCH DỮ LIỆU") -> None:
        slide = self.prs.slides.add_slide(self.blank_layout)
        self.slide_count += 1

        # Nền Navy đậm toàn màn hình
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, PptInches(0), PptInches(0), PptInches(13.333), PptInches(7.5)
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = _ppt_rgb("primary")
        bg.line.fill.background()

        # Khối trang trí bên phải
        deco = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, PptInches(12.85), PptInches(0), PptInches(0.483), PptInches(7.5)
        )
        deco.fill.solid()
        deco.fill.fore_color.rgb = _ppt_rgb("accent")
        deco.line.fill.background()

        # Thanh điểm nhấn bên trái
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, PptInches(0.95), PptInches(1.8), PptInches(0.12), PptInches(3.8)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = _ppt_rgb("accent")
        bar.line.fill.background()

        # Hộp nội dung chính
        tb = slide.shapes.add_textbox(PptInches(1.35), PptInches(1.75), PptInches(10.8), PptInches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.space_after = PptPt(14)
        r0 = p0.add_run()
        r0.text = badge_text.upper()
        r0.font.name = self.font_name
        r0.font.size = PptPt(12)
        r0.font.bold = True
        r0.font.color.rgb = PptRGB(253, 224, 71)

        p1 = tf.add_paragraph()
        p1.space_after = PptPt(16)
        r1 = p1.add_run()
        r1.text = self.title.upper()
        r1.font.name = self.font_name
        r1.font.size = PptPt(34 if len(self.title) < 60 else 28)
        r1.font.bold = True
        r1.font.color.rgb = _ppt_rgb("white")

        if self.subtitle:
            p2 = tf.add_paragraph()
            p2.space_after = PptPt(24)
            r2 = p2.add_run()
            r2.text = self.subtitle
            r2.font.name = self.font_name
            r2.font.size = PptPt(17)
            r2.font.color.rgb = PptRGB(203, 213, 225)

        if self.author:
            p3 = tf.add_paragraph()
            r3 = p3.add_run()
            r3.text = self.author
            r3.font.name = self.font_name
            r3.font.size = PptPt(13)
            r3.font.color.rgb = PptRGB(148, 163, 184)

    def add_kpi_slide(
        self,
        action_title: str,
        section_tag: str,
        kpis: Sequence[Tuple[str, str, str]],
        takeaways: Sequence[str],
        takeaway_title: str = "NHẬN ĐỊNH & KẾT LUẬN TRỌNG TÂM",
    ) -> None:
        """Slide gồm hàng thẻ KPI lớn phía trên + Khung phân tích tổng hợp phía dưới."""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._add_slide_chrome(slide, section_tag, action_title)

        n = max(1, len(kpis))
        gap = 0.28
        total_w = 12.133
        card_w = (total_w - gap * (n - 1)) / n

        for idx, (val, label, sub) in enumerate(kpis):
            left = 0.6 + idx * (card_w + gap)
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, PptInches(left), PptInches(1.65), PptInches(card_w), PptInches(2.15)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = _ppt_rgb("white")
            card.line.color.rgb = _ppt_rgb("card_border")
            card.line.width = PptPt(1.2)

            # Thanh màu trên đỉnh card
            top_strip = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, PptInches(left), PptInches(1.65), PptInches(card_w), PptInches(0.1)
            )
            top_strip.fill.solid()
            top_strip.fill.fore_color.rgb = _ppt_rgb("primary" if idx % 2 == 0 else "secondary")
            top_strip.line.fill.background()

            tb = slide.shapes.add_textbox(PptInches(left + 0.18), PptInches(1.85), PptInches(card_w - 0.36), PptInches(1.8))
            tf = tb.text_frame
            tf.word_wrap = True

            p_val = tf.paragraphs[0]
            p_val.space_after = PptPt(4)
            r_val = p_val.add_run()
            r_val.text = str(val)
            r_val.font.name = self.font_name
            r_val.font.size = PptPt(28)
            r_val.font.bold = True
            r_val.font.color.rgb = _ppt_rgb("primary")

            p_lbl = tf.add_paragraph()
            p_lbl.space_after = PptPt(4)
            r_lbl = p_lbl.add_run()
            r_lbl.text = str(label)
            r_lbl.font.name = self.font_name
            r_lbl.font.size = PptPt(13.5)
            r_lbl.font.bold = True
            r_lbl.font.color.rgb = _ppt_rgb("dark_text")

            p_sub = tf.add_paragraph()
            r_sub = p_sub.add_run()
            r_sub.text = str(sub)
            r_sub.font.name = self.font_name
            r_sub.font.size = PptPt(11.5)
            r_sub.font.color.rgb = _ppt_rgb("success")

        # Khung Takeaways bên dưới
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, PptInches(0.6), PptInches(4.05), PptInches(12.133), PptInches(2.75)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = _ppt_rgb("white")
        box.line.color.rgb = _ppt_rgb("card_border")
        box.line.width = PptPt(1.2)

        tb_tk = slide.shapes.add_textbox(PptInches(0.85), PptInches(4.2), PptInches(11.6), PptInches(2.45))
        tf_tk = tb_tk.text_frame
        tf_tk.word_wrap = True

        pt = tf_tk.paragraphs[0]
        pt.space_after = PptPt(8)
        rt = pt.add_run()
        rt.text = takeaway_title.upper()
        rt.font.name = self.font_name
        rt.font.size = PptPt(13)
        rt.font.bold = True
        rt.font.color.rgb = _ppt_rgb("secondary")

        for item in takeaways[:5]:
            p = tf_tk.add_paragraph()
            p.space_after = PptPt(6)
            r = p.add_run()
            r.text = f"▪  {item}"
            r.font.name = self.font_name
            r.font.size = PptPt(14)
            r.font.color.rgb = _ppt_rgb("dark_text")

    def add_two_column_slide(
        self,
        action_title: str,
        section_tag: str,
        left_title: str,
        left_bullets: Sequence[str],
        right_title: str = "",
        right_bullets: Optional[Sequence[str]] = None,
        right_image_path: Optional[str | Path] = None,
    ) -> None:
        """Slide chia 2 cột: Cột trái là Luận điểm, Cột phải là Luận điểm đối sánh hoặc Biểu đồ 300 DPI."""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._add_slide_chrome(slide, section_tag, action_title)

        # Khung cột trái
        left_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, PptInches(0.6), PptInches(1.65), PptInches(5.85), PptInches(5.15)
        )
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = _ppt_rgb("white")
        left_card.line.color.rgb = _ppt_rgb("card_border")

        tb_l = slide.shapes.add_textbox(PptInches(0.85), PptInches(1.85), PptInches(5.35), PptInches(4.75))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        pl0 = tf_l.paragraphs[0]
        pl0.space_after = PptPt(10)
        rl0 = pl0.add_run()
        rl0.text = left_title.upper()
        rl0.font.name = self.font_name
        rl0.font.size = PptPt(14.5)
        rl0.font.bold = True
        rl0.font.color.rgb = _ppt_rgb("primary")

        for b in left_bullets[:6]:
            p = tf_l.add_paragraph()
            p.space_after = PptPt(8)
            r = p.add_run()
            r.text = f"•  {b}"
            r.font.name = self.font_name
            r.font.size = PptPt(13.5)
            r.font.color.rgb = _ppt_rgb("dark_text")

        # Khung cột phải
        right_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, PptInches(6.75), PptInches(1.65), PptInches(5.98), PptInches(5.15)
        )
        right_card.fill.solid()
        right_card.fill.fore_color.rgb = _ppt_rgb("white")
        right_card.line.color.rgb = _ppt_rgb("card_border")

        if right_image_path and Path(right_image_path).exists():
            if right_title:
                tb_rt = slide.shapes.add_textbox(PptInches(6.95), PptInches(1.8), PptInches(5.55), PptInches(0.45))
                p_rt = tb_rt.text_frame.paragraphs[0]
                r_rt = p_rt.add_run()
                r_rt.text = right_title.upper()
                r_rt.font.name = self.font_name
                r_rt.font.size = PptPt(13.5)
                r_rt.font.bold = True
                r_rt.font.color.rgb = _ppt_rgb("secondary")
                img_top = PptInches(2.28)
                img_w = PptInches(5.65)
            else:
                img_top = PptInches(1.85)
                img_w = PptInches(5.65)
            slide.shapes.add_picture(str(right_image_path), PptInches(6.92), img_top, width=img_w)
        else:
            tb_r = slide.shapes.add_textbox(PptInches(7.0), PptInches(1.85), PptInches(5.45), PptInches(4.75))
            tf_r = tb_r.text_frame
            tf_r.word_wrap = True
            pr0 = tf_r.paragraphs[0]
            pr0.space_after = PptPt(10)
            rr0 = pr0.add_run()
            rr0.text = right_title.upper()
            rr0.font.name = self.font_name
            rr0.font.size = PptPt(14.5)
            rr0.font.bold = True
            rr0.font.color.rgb = _ppt_rgb("secondary")

            for b in (right_bullets or [])[:6]:
                p = tf_r.add_paragraph()
                p.space_after = PptPt(8)
                r = p.add_run()
                r.text = f"•  {b}"
                r.font.name = self.font_name
                r.font.size = PptPt(13.5)
                r.font.color.rgb = _ppt_rgb("dark_text")

    def add_table_slide(
        self,
        action_title: str,
        section_tag: str,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        col_widths_in: Optional[Sequence[float]] = None,
        footnote: str = "",
    ) -> None:
        """Slide trình bày bảng dữ liệu được căn chỉnh sắc nét."""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._add_slide_chrome(slide, section_tag, action_title)

        n_cols = len(headers)
        n_rows = len(rows) + 1
        total_w = 12.133
        row_h = min(0.52, 4.6 / max(1, n_rows))
        table_h = row_h * n_rows

        shape = slide.shapes.add_table(
            n_rows, n_cols, PptInches(0.6), PptInches(1.7), PptInches(total_w), PptInches(table_h)
        )
        tbl = shape.table

        if not col_widths_in or len(col_widths_in) != n_cols:
            col_widths_in = [total_w / n_cols] * n_cols
        for idx, w in enumerate(col_widths_in):
            tbl.columns[idx].width = PptInches(w)

        # Header
        for c_idx, h_text in enumerate(headers):
            cell = tbl.cell(0, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = _ppt_rgb("primary")
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = str(h_text)
            r.font.name = self.font_name
            r.font.size = PptPt(12.5)
            r.font.bold = True
            r.font.color.rgb = _ppt_rgb("white")

        # Data
        for r_idx, row_data in enumerate(rows):
            bg_rgb = PptRGB(241, 245, 249) if r_idx % 2 == 1 else _ppt_rgb("white")
            for c_idx in range(n_cols):
                val = row_data[c_idx] if c_idx < len(row_data) else ""
                cell = tbl.cell(r_idx + 1, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = bg_rgb
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                p = cell.text_frame.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.CENTER
                r = p.add_run()
                r.text = str(val)
                r.font.name = self.font_name
                r.font.size = PptPt(12)
                r.font.bold = c_idx == 0
                r.font.color.rgb = _ppt_rgb("dark_text")

        if footnote:
            tb_fn = slide.shapes.add_textbox(PptInches(0.6), PptInches(6.55), PptInches(12.133), PptInches(0.4))
            p_fn = tb_fn.text_frame.paragraphs[0]
            r_fn = p_fn.add_run()
            r_fn.text = footnote
            r_fn.font.name = self.font_name
            r_fn.font.size = PptPt(11)
            r_fn.font.italic = True
            r_fn.font.color.rgb = _ppt_rgb("muted_text")

    def save(self, output_path: str | Path) -> Path:
        target = _safe_save_path(output_path)
        try:
            self.prs.save(str(target))
            return target
        except PermissionError:
            alt = target.with_name(f"{target.stem}_new{target.suffix}")
            self.prs.save(str(alt))
            return alt


# ==============================================================================
# 3. KIỂM ĐỊNH ĐẦU RA TỰ ĐỘNG (ZERO-TRUST VERIFICATION)
# ==============================================================================
def verify_outputs(docx_path: Optional[str | Path] = None, pptx_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """Kiểm tra tính toàn vẹn của file Word (.docx) và PowerPoint (.pptx) sau khi xuất."""
    result: Dict[str, Any] = {"status": "OK", "checks": {}}

    if docx_path:
        dp = Path(docx_path)
        if not dp.exists() or dp.stat().st_size == 0:
            result["status"] = "ERROR"
            result["checks"]["docx"] = "File không tồn tại hoặc rỗng"
        else:
            loaded_doc = Document(str(dp))
            result["checks"]["docx"] = {
                "path": str(dp),
                "size_bytes": dp.stat().st_size,
                "paragraphs": len(loaded_doc.paragraphs),
                "tables": len(loaded_doc.tables),
            }

    if pptx_path:
        pp = Path(pptx_path)
        if not pp.exists() or pp.stat().st_size == 0:
            result["status"] = "ERROR"
            result["checks"]["pptx"] = "File không tồn tại hoặc rỗng"
        else:
            loaded_prs = Presentation(str(pp))
            overflow_warnings: List[str] = []
            for s_idx, slide in enumerate(loaded_prs.slides, start=1):
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        txt = shape.text_frame.text.strip()
                        if len(txt) > 650:
                            overflow_warnings.append(f"Slide {s_idx}: Khung chữ dài ({len(txt)} ký tự)")
            result["checks"]["pptx"] = {
                "path": str(pp),
                "size_bytes": pp.stat().st_size,
                "slides": len(loaded_prs.slides),
                "overflow_warnings": overflow_warnings,
            }

    return result


# ==============================================================================
# CLI ENTRYPOINT (JSON SPEC RUNNER)
# ==============================================================================
def build_from_json_spec(spec_path: str | Path) -> Dict[str, Any]:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    meta = spec.get("meta", {})
    title = meta.get("title", "BÁO CÁO CHUYÊN ĐỀ")
    subtitle = meta.get("subtitle", "")
    author = meta.get("author", "")

    docx_out = spec.get("docx_output")
    pptx_out = spec.get("pptx_output")

    if docx_out:
        w = WordReportBuilder(title=title, subtitle=subtitle, author=author, mode=meta.get("mode", "modern"))
        w.add_cover_header(
            org_name=meta.get("org_name", "ĐƠN VỊ BÁO CÁO"),
            doc_code=meta.get("doc_code", "Số: 01/BC"),
            location_date=meta.get("date", None),
        )
        if meta.get("executive_summary"):
            w.add_callout("TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)", meta["executive_summary"], tone="info")
        if spec.get("kpis"):
            w.add_kpi_summary([(k["label"], k["value"], k.get("delta", "")) for k in spec["kpis"]])
        for sec in spec.get("sections", []):
            w.add_heading(sec["heading"], level=sec.get("level", 1))
            for p in sec.get("paragraphs", []):
                w.add_paragraph(p)
            if sec.get("bullets"):
                w.add_bullets(sec["bullets"])
            if sec.get("table"):
                t = sec["table"]
                w.add_styled_table(
                    headers=t["headers"],
                    rows=t["rows"],
                    col_widths_cm=t.get("col_widths_cm"),
                    caption=t.get("caption", ""),
                )
            if sec.get("figure"):
                f = sec["figure"]
                w.add_figure(f["path"], caption=f.get("caption", ""), width_cm=f.get("width_cm", 15.0))
        w.save(docx_out)

    if pptx_out:
        p = PPTReportBuilder(title=title, subtitle=subtitle, author=author)
        p.add_title_slide(badge_text=meta.get("badge", "BÁO CÁO TỔNG HỢP & PHÂN TÍCH"))
        for sl in spec.get("slides", []):
            stype = sl.get("type", "two_column")
            if stype == "kpi":
                p.add_kpi_slide(
                    action_title=sl["action_title"],
                    section_tag=sl.get("section_tag", "TỔNG QUAN"),
                    kpis=[(k["value"], k["label"], k.get("delta", "")) for k in sl.get("kpis", [])],
                    takeaways=sl.get("takeaways", []),
                )
            elif stype == "table":
                p.add_table_slide(
                    action_title=sl["action_title"],
                    section_tag=sl.get("section_tag", "DỮ LIỆU CHI TIẾT"),
                    headers=sl["headers"],
                    rows=sl["rows"],
                    col_widths_in=sl.get("col_widths_in"),
                    footnote=sl.get("footnote", ""),
                )
            else:
                p.add_two_column_slide(
                    action_title=sl["action_title"],
                    section_tag=sl.get("section_tag", "PHÂN TÍCH"),
                    left_title=sl.get("left_title", "Nội dung chính"),
                    left_bullets=sl.get("left_bullets", []),
                    right_title=sl.get("right_title", ""),
                    right_bullets=sl.get("right_bullets", []),
                    right_image_path=sl.get("right_image_path"),
                )
        p.save(pptx_out)

    return verify_outputs(docx_out, pptx_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Word & PowerPoint Report Builder Engine")
    parser.add_argument("--spec", type=str, help="Đường dẫn tới file JSON đặc tả báo cáo")
    args = parser.parse_args()
    if args.spec:
        res = build_from_json_spec(args.spec)
        print(json.dumps(res, ensure_ascii=False, indent=2))
