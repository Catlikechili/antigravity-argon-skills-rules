#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_papers.py - Quét thư mục PDF & tìm kiếm bài báo học thuật (OpenAlex + Crossref).
Ưu tiên nguồn uy tín (ScienceDirect/Elsevier, IEEE, Nature, Science, ACM, Springer),
phân loại Độ mới học thuật (Frontier) & Bài nền tảng trích dẫn cao (Seminal),
và sắp xếp giảm dần theo độ mới (Newest First).

Thiết kế an toàn:
- Ép chuẩn UTF-8 toàn cục (tránh lỗi cp1252 tiếng Việt trên Windows).
- Không phụ thuộc thư viện ngoài bắt buộc (dùng urllib chuẩn; tự fallback nếu thiếu pypdf/PyMuPDF).
- Hoạt động cả khi mất mạng/offline (trích xuất DOI prefix, năm, tiêu đề cục bộ + cache JSON).
- Xử lý an toàn đường dẫn có khoảng trắng và ký tự Unicode.
"""

from __future__ import annotations
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Bảo vệ encoding đầu ra trên Windows PowerShell / CMD
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DOI_REGEX = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)")
YEAR_REGEX = re.compile(r"\b(19[5-9]\d|20[0-3]\d)\b")

# Nhận diện nhà xuất bản uy tín qua DOI Prefix (hoạt động ngay cả khi Offline)
DOI_PREFIX_PUBLISHER = {
    "10.1016": ("ScienceDirect / Elsevier", 1),
    "10.1109": ("IEEE", 1),
    "10.1038": ("Nature Portfolio", 1),
    "10.1126": ("Science (AAAS)", 2),
    "10.1145": ("ACM", 2),
    "10.1007": ("Springer", 2),
    "10.1002": ("Wiley", 2),
    "10.1111": ("Wiley", 2),
    "10.1093": ("Oxford University Press", 2),
    "10.1017": ("Cambridge University Press", 2),
    "10.1103": ("APS Physics", 2),
    "10.2514": ("AIAA", 2),
    "10.1137": ("SIAM", 2),
    "10.1016": ("ScienceDirect / Elsevier", 1),
    "10.48550": ("arXiv (Preprint)", 3),
}

TIER_1_KEYWORDS = [
    "elsevier", "sciencedirect", "ieee", "institute of electrical and electronics engineers",
    "nature", "springer nature"
]
TIER_2_KEYWORDS = [
    "association for computing machinery", "acm", "american association for the advancement of science",
    "science", "springer", "wiley", "oxford university press", "cambridge university press",
    "american physical society", "siam", "aiaa", "asme", "cell press", "lancet", "taylor & francis"
]
PREPRINT_KEYWORDS = ["arxiv", "biorxiv", "medrxiv", "techrxiv", "ssrn", "preprint"]


def clean_doi(raw_doi: str) -> str:
    """Làm sạch dấu câu thừa dính cuối DOI trong văn bản PDF."""
    doi = raw_doi.strip()
    while doi and doi[-1] in ".,;)]}>'\"":
        if doi[-1] == ")" and doi.count("(") >= doi.count(")"):
            break
        doi = doi[:-1]
    return doi.lower()


def classify_venue(publisher: str, venue: str, doi: str) -> Tuple[int, str]:
    """
    Phân bậc uy tín nguồn xuất bản:
    - Tier 1: ScienceDirect/Elsevier, IEEE, Nature (Ưu tiên cốt lõi)
    - Tier 2: ACM, Science, Springer, Wiley, OUP, AIAA, APS... (Uy tín mở rộng)
    - Tier 3: Preprint (arXiv/TechRxiv - chưa bình duyệt chính thức)
    - Tier 4: Chưa xác thực / Ngoài danh mục ưu tiên
    """
    pub_low = f"{publisher or ''} {venue or ''}".lower()
    doi_low = (doi or "").lower()

    for prefix, (label, tier) in DOI_PREFIX_PUBLISHER.items():
        if doi_low.startswith(prefix + "/"):
            # Nếu là Springer (10.1007) nhưng tên tạp chí thuộc hệ Nature thì nâng lên Tier 1
            if tier == 2 and "nature" in pub_low:
                return 1, f"Nature / {venue or label}"
            return tier, venue or label

    if any(k in pub_low for k in TIER_1_KEYWORDS):
        return 1, venue or publisher or "Tier-1 Venue"
    if any(k in pub_low for k in TIER_2_KEYWORDS):
        return 2, venue or publisher or "Tier-2 Reputable"
    if any(k in pub_low for k in PREPRINT_KEYWORDS):
        return 3, venue or "Preprint (Chưa bình duyệt)"
    return 4, venue or publisher or "Chưa xác thực nguồn"


def extract_pdf_text_and_meta(pdf_path: Path, max_pages: int = 2) -> Tuple[str, Dict[str, str]]:
    """Đọc 2 trang đầu của PDF với cơ chế fallback đa tầng (PyMuPDF -> pypdf -> raw binary)."""
    text_chunks: List[str] = []
    meta: Dict[str, str] = {}

    # Tầng 1: PyMuPDF (pymupdf / fitz)
    try:
        try:
            import pymupdf as fitz  # type: ignore
        except ImportError:
            import fitz  # type: ignore
        with fitz.open(str(pdf_path)) as doc:
            if doc.metadata:
                meta = {k.lower(): str(v) for k, v in doc.metadata.items() if v}
            for i in range(min(len(doc), max_pages)):
                text_chunks.append(doc[i].get_text("text") or "")
        if "".join(text_chunks).strip():
            return "\n".join(text_chunks), meta
    except Exception:
        pass

    # Tầng 2: pypdf / PyPDF2
    for lib_name in ("pypdf", "PyPDF2"):
        try:
            mod = __import__(lib_name)
            reader = mod.PdfReader(str(pdf_path))
            if reader.metadata:
                meta = {str(k).lstrip("/").lower(): str(v) for k, v in reader.metadata.items() if v}
            for i in range(min(len(reader.pages), max_pages)):
                text_chunks.append(reader.pages[i].extract_text() or "")
            if "".join(text_chunks).strip():
                return "\n".join(text_chunks), meta
        except Exception:
            continue

    # Tầng 3: Quét byte thô (không cần thư viện ngoài, bắt được DOI/Title/Year trong metadata/stream không nén)
    try:
        raw_bytes = pdf_path.read_bytes()[:262144]  # Chỉ đọc 256KB đầu để tiết kiệm RAM
        raw_text = raw_bytes.decode("latin-1", errors="ignore")
        title_match = re.search(r"/Title\s*\(([^)]{4,200})\)", raw_text)
        if title_match:
            meta["title"] = title_match.group(1)
        return raw_text, meta
    except Exception:
        return "", meta


def guess_local_info(pdf_path: Path, text: str, meta: Dict[str, str]) -> Dict[str, Any]:
    """Trích xuất thông tin cục bộ từ tên file & nội dung trang đầu."""
    doi = ""
    for candidate in (meta.get("doi", ""), meta.get("subject", ""), text, pdf_path.stem):
        m = DOI_REGEX.search(candidate)
        if m:
            doi = clean_doi(m.group(1))
            break

    # Đoán tiêu đề
    title = meta.get("title", "").strip()
    if not title or title.lower().startswith(("untitled", "microsoft word", "doi:")):
        lines = [ln.strip() for ln in text.splitlines() if 12 <= len(ln.strip()) <= 180]
        # Bỏ các dòng header nhà xuất bản phổ biến
        filtered = [
            ln for ln in lines[:12]
            if not any(h in ln.lower() for h in ("downloaded from", "elsevier", "sciencedirect", "ieee", "arxiv:", "http", "vol.", "issn"))
        ]
        title = filtered[0] if filtered else pdf_path.stem.replace("_", " ").replace("-", " ")

    # Đoán năm xuất bản
    year = None
    m_fn = YEAR_REGEX.search(pdf_path.stem)
    if m_fn:
        year = int(m_fn.group(1))
    else:
        years_in_text = [int(y) for y in YEAR_REGEX.findall(text[:3000]) if 1950 <= int(y) <= datetime.date.today().year + 1]
        if years_in_text:
            year = max(years_in_text)

    # Đoán nhà xuất bản cục bộ nếu offline
    low_sample = text[:4000].lower()
    pub_guess = ""
    if "sciencedirect" in low_sample or "elsevier" in low_sample:
        pub_guess = "ScienceDirect / Elsevier"
    elif "ieee" in low_sample:
        pub_guess = "IEEE"
    elif "nature" in low_sample:
        pub_guess = "Nature Portfolio"

    return {
        "file_name": pdf_path.name,
        "file_path": str(pdf_path),
        "doi": doi,
        "title": title,
        "year": year,
        "pub_date": f"{year}-01-01" if year else "",
        "publisher": pub_guess,
        "venue": pub_guess,
        "citations": None,
        "source_mode": "LOCAL_OFFLINE",
    }


def http_get_json(url: str, timeout: int = 8) -> Optional[Dict[str, Any]]:
    """Gọi REST API an toàn bằng thư viện chuẩn urllib với User-Agent lịch sự."""
    headers = {
        "User-Agent": "PaperTriageSkill/1.0 (Academic Literature Triage; mailto:researcher@example.org)",
        "Accept": "application/json",
    }
    api_key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if api_key and "api.openalex.org" in url and "api_key=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}api_key={urllib.parse.quote(api_key)}"

    req = urllib.request.Request(url, headers=headers)
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8", errors="replace"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
            if attempt == 0:
                time.sleep(0.4)
    return None


def parse_openalex_work(work: Dict[str, Any], fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Chuẩn hóa bản ghi OpenAlex (xử lý an toàn mọi trường None/thiếu)."""
    base = dict(fallback or {})
    raw_doi = work.get("doi") or ""
    doi = clean_doi(raw_doi.replace("https://doi.org/", "").replace("http://doi.org/", "")) or base.get("doi", "")

    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    venue = src.get("display_name") or ""
    publisher = src.get("host_organization_name") or ""

    # Nếu bản chính là Preprint (arXiv) nhưng bài đã được đăng chính thức ở IEEE/Elsevier/Nature trong locations
    if not venue or any(k in venue.lower() for k in PREPRINT_KEYWORDS):
        for alt_loc in (work.get("locations") or []):
            alt_src = (alt_loc or {}).get("source") or {}
            alt_name = alt_src.get("display_name") or ""
            alt_pub = alt_src.get("host_organization_name") or ""
            t_check, _ = classify_venue(alt_pub, alt_name, doi)
            if t_check in (1, 2):
                venue, publisher = alt_name, alt_pub
                break

    year = work.get("publication_year") or base.get("year")
    pub_date = work.get("publication_date") or (f"{year}-01-01" if year else base.get("pub_date", ""))
    citations = work.get("cited_by_count")
    if citations is None:
        citations = base.get("citations")

    authors_list = []
    for auth in (work.get("authorships") or [])[:4]:
        a_name = ((auth or {}).get("author") or {}).get("display_name")
        if a_name:
            authors_list.append(a_name)
    if len(work.get("authorships") or []) > 4:
        authors_list.append("et al.")

    return {
        "file_name": base.get("file_name", ""),
        "file_path": base.get("file_path", ""),
        "doi": doi,
        "title": (work.get("title") or work.get("display_name") or base.get("title") or "Untitled").strip(),
        "authors": ", ".join(authors_list) if authors_list else base.get("authors", ""),
        "year": int(year) if year else None,
        "pub_date": pub_date,
        "publisher": publisher or base.get("publisher", ""),
        "venue": venue or base.get("venue", ""),
        "citations": int(citations) if citations is not None else None,
        "oa_url": ((work.get("open_access") or {}).get("oa_url")) or "",
        "openalex_id": work.get("id") or "",
        "source_mode": "OPENALEX",
    }


def enrich_record_online(rec: Dict[str, Any], cache: Dict[str, Any]) -> Dict[str, Any]:
    """Tra cứu DOI hoặc Tiêu đề trên OpenAlex, fallback sang Crossref nếu cần."""
    cache_key = rec.get("doi") or f"title::{rec.get('title', '').lower()[:120]}"
    if cache_key and cache_key in cache:
        cached = dict(cache[cache_key])
        cached["file_name"] = rec.get("file_name", "")
        cached["file_path"] = rec.get("file_path", "")
        return cached

    doi = rec.get("doi", "")
    if doi:
        oa_url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}"
        data = http_get_json(oa_url)
        if data and data.get("id"):
            enriched = parse_openalex_work(data, rec)
            cache[cache_key] = enriched
            return enriched

        # Fallback Crossref nếu OpenAlex chưa kịp index bài vừa xuất bản hôm qua
        cr_url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
        cr_data = http_get_json(cr_url)
        if cr_data and "message" in cr_data:
            msg = cr_data["message"]
            titles = msg.get("title") or []
            containers = msg.get("container-title") or []
            issued = ((msg.get("issued") or {}).get("date-parts") or [[None]])[0]
            yr = issued[0] if issued and issued[0] else rec.get("year")
            mo = issued[1] if len(issued) > 1 and issued[1] else 1
            dy = issued[2] if len(issued) > 2 and issued[2] else 1
            enriched = {
                **rec,
                "title": (titles[0] if titles else rec.get("title", "Untitled")).strip(),
                "venue": containers[0] if containers else rec.get("venue", ""),
                "publisher": msg.get("publisher") or rec.get("publisher", ""),
                "year": int(yr) if yr else None,
                "pub_date": f"{int(yr):04d}-{int(mo):02d}-{int(dy):02d}" if yr else "",
                "citations": msg.get("is-referenced-by-count"),
                "source_mode": "CROSSREF",
            }
            cache[cache_key] = enriched
            return enriched

    # Nếu không có DOI, thử tìm theo tiêu đề trên OpenAlex
    title = rec.get("title", "").strip()
    if len(title) >= 15 and rec.get("file_name"):
        q = urllib.parse.quote(title[:140])
        search_url = f"https://api.openalex.org/works?search={q}&per-page=1"
        s_data = http_get_json(search_url)
        results = (s_data or {}).get("results") or []
        if results:
            cand_title = (results[0].get("title") or "").lower()
            # Kiểm tra độ khớp từ khóa để tránh gán nhầm bài
            w1 = {w for w in re.findall(r"[a-z0-9]{4,}", title.lower())}
            w2 = {w for w in re.findall(r"[a-z0-9]{4,}", cand_title)}
            if w1 and len(w1 & w2) / max(len(w1), 1) >= 0.6:
                enriched = parse_openalex_work(results[0], rec)
                cache[cache_key] = enriched
                return enriched

    return rec


def evaluate_and_tag(
    rec: Dict[str, Any],
    current_year: int,
    recent_window: int = 3,
    min_citations: int = 100,
    min_cpy: float = 15.0,
) -> Dict[str, Any]:
    """Đánh giá Uy tín nguồn + Phân nhánh Frontier (Độ mới) / Seminal (Trích dẫn nền tảng)."""
    tier, venue_label = classify_venue(rec.get("publisher", ""), rec.get("venue", ""), rec.get("doi", ""))
    year = rec.get("year")
    citations = rec.get("citations")

    age = max(1, current_year - year + 1) if year else 1
    cpy = round(citations / age, 1) if citations is not None else None

    is_trusted = tier in (1, 2)
    is_recent = bool(year and year >= (current_year - recent_window + 1))
    is_seminal = bool(
        citations is not None and (citations >= min_citations or (cpy is not None and cpy >= min_cpy and citations >= 30))
    )

    if not is_trusted:
        if tier == 3 and (is_recent or is_seminal):
            track = "PREPRINT_WATCH"
            action = "Kiểm tra bản đăng chính thức (IEEE/Elsevier/Nature)"
        else:
            track = "HOLD_UNVERIFIED"
            action = "Loại / Kiểm chứng lại uy tín tạp chí"
    else:
        if is_recent and is_seminal:
            track = "FRONTIER_STAR"
            action = "ĐỌC SÂU NGAY (Bài mới + Trích dẫn tăng vọt)"
        elif is_recent:
            track = "FRONTIER_NEW"
            action = "Đọc ưu tiên (Cập nhật độ mới học thuật)"
        elif is_seminal:
            track = "SEMINAL_CORE"
            action = "Đọc nền tảng (Bài gốc trích dẫn cao)"
        else:
            track = "ARCHIVE_LOW"
            action = "Đọc lướt / Tham khảo phụ"

    tier_badge = {
        1: "Tier-1 (IEEE/ScienceDirect/Nature)",
        2: "Tier-2 (Uy tín quốc tế)",
        3: "Preprint (Chưa bình duyệt)",
        4: "Chưa xác thực",
    }[tier]

    return {
        **rec,
        "venue_tier": tier,
        "venue_badge": tier_badge,
        "venue_display": venue_label,
        "citations_per_year": cpy,
        "track": track,
        "recommended_action": action,
    }


def search_online_topic(query: str, max_results: int, current_year: int) -> List[Dict[str, Any]]:
    """
    Tìm kiếm chủ đề trực tiếp trên OpenAlex:
    Kết hợp 2 luồng: (1) Bài mới nhất (sort=publication_date:desc) & (2) Bài nền tảng nhiều trích dẫn nhất (sort=cited_by_count:desc),
    sau đó lọc giữ các nguồn uy tín (Elsevier/ScienceDirect, IEEE, Nature, ACM, Springer...).
    """
    q_enc = urllib.parse.quote(query)
    half = max(10, max_results)
    urls = [
        f"https://api.openalex.org/works?search={q_enc}&filter=type:article,from_publication_date:{current_year-2}-01-01&sort=publication_date:desc&per-page={half}",
        f"https://api.openalex.org/works?search={q_enc}&filter=type:article,cited_by_count:>50&sort=cited_by_count:desc&per-page={half}",
    ]
    seen_keys = set()
    collected: List[Dict[str, Any]] = []
    for url in urls:
        payload = http_get_json(url, timeout=10)
        for item in (payload or {}).get("results") or []:
            parsed = parse_openalex_work(item)
            key = parsed.get("doi") or parsed.get("openalex_id") or parsed.get("title")
            if not key or key in seen_keys:
                continue
            tier, _ = classify_venue(parsed.get("publisher", ""), parsed.get("venue", ""), parsed.get("doi", ""))
            if tier in (1, 2):  # Chỉ nhận nguồn uy tín khi tìm kiếm tự động
                seen_keys.add(key)
                collected.append(parsed)
    return collected[: max_results * 2]


def sort_by_recency(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sắp xếp giảm dần theo Độ mới (Publication Date / Year mới nhất lên đầu), sau đó theo Bậc uy tín & Citations/Year."""
    def sort_key(r: Dict[str, Any]) -> Tuple[str, int, int, float]:
        pub_date = r.get("pub_date") or ""
        year = r.get("year") or 0
        # Đảo dấu tier để Tier 1 đứng trước Tier 4 khi cùng ngày
        inv_tier = -(r.get("venue_tier") or 4)
        cpy = r.get("citations_per_year") if r.get("citations_per_year") is not None else -1.0
        return (pub_date, year, inv_tier, cpy)

    return sorted(records, key=sort_key, reverse=True)


def render_markdown_report(records: List[Dict[str, Any]], scan_target: str, current_year: int) -> str:
    """Xuất bảng xếp hạng Markdown rõ ràng, chia tách nhóm Uy tín (xếp theo độ mới) & nhóm Cảnh báo nguồn."""
    trusted = [r for r in records if r.get("venue_tier") in (1, 2)]
    flagged = [r for r in records if r.get("venue_tier") not in (1, 2)]

    trusted_sorted = sort_by_recency(trusted)
    flagged_sorted = sort_by_recency(flagged)

    lines = [
        "# Bảng Xếp Hạng & Phân Loại Bài Báo Khoa Học (Triage Index)",
        "",
        f"- **Nguồn quét:** `{scan_target}`",
        f"- **Ngày cập nhật:** {datetime.date.today().isoformat()}",
        f"- **Tổng số bài quét:** {len(records)} | **Đạt chuẩn nguồn uy tín (Tier 1-2):** {len(trusted_sorted)} | **Cần kiểm chứng/Preprint:** {len(flagged_sorted)}",
        "- **Quy tắc sắp xếp:** Xếp giảm dần theo **Độ mới (Ngày/Năm xuất bản mới nhất lên đầu)**; phân nhãn tách biệt giữa **Độ mới học thuật (Frontier)** và **Bài nền tảng trích dẫn cao (Seminal)**.",
        "",
        "---",
        "",
        "## 1. Danh sách Bài báo Nguồn Uy tín — Xếp theo Độ mới (Newest First)",
        "",
    ]

    if not trusted_sorted:
        lines.append("> Chưa tìm thấy bài báo nào thuộc nhóm nguồn uy tín đã xác thực trong lần quét này.")
    else:
        lines.extend([
            "| # | Năm / Ngày | Phân loại | Tiêu đề & File / DOI | Nguồn xuất bản (Venue) | Trích dẫn (Tổng / Năm) | Khuyến nghị hành động |",
            "| :-: | :---: | :---: | :--- | :--- | :---: | :--- |",
        ])
        for idx, r in enumerate(trusted_sorted, 1):
            date_str = r.get("pub_date") or str(r.get("year") or "N/A")
            track_map = {
                "FRONTIER_STAR": "🔥 Mới + Nổi bật",
                "FRONTIER_NEW": "🆕 Độ mới (Frontier)",
                "SEMINAL_CORE": "🏛️ Nền tảng (Seminal)",
                "ARCHIVE_LOW": "📄 Tham khảo phụ",
            }
            badge = track_map.get(r.get("track", ""), r.get("track", ""))
            title_clean = (r.get("title") or "Untitled").replace("|", "\\|")
            loc_ref = f"`{r['file_name']}`" if r.get("file_name") else ""
            doi_ref = f"[DOI:{r['doi']}](https://doi.org/{r['doi']})" if r.get("doi") else "Chưa rõ DOI"
            ref_parts = " · ".join(p for p in (loc_ref, doi_ref) if p)
            venue_clean = f"**{r.get('venue_display', '')}** ({'Tier 1' if r.get('venue_tier') == 1 else 'Tier 2'})".replace("|", "\\|")
            cit = r.get("citations")
            cpy = r.get("citations_per_year")
            cit_str = f"{cit} ({cpy}/năm)" if cit is not None else "Offline / Chưa rõ"
            lines.append(
                f"| {idx} | {date_str} | {badge} | **{title_clean}**<br>{ref_parts} | {venue_clean} | {cit_str} | {r.get('recommended_action', '')} |"
            )

    lines.extend(["", "---", "", "## 2. Nhóm Bài Nền Tảng Trích Dẫn Cao Nhất (Top Seminal Foundations)", ""])
    seminals = sorted(
        [r for r in trusted if r.get("track") in ("SEMINAL_CORE", "FRONTIER_STAR")],
        key=lambda x: (x.get("citations") or 0),
        reverse=True,
    )
    if not seminals:
        lines.append("> Không có bài nào vượt ngưỡng trích dẫn nền tảng trong danh sách hiện tại (hoặc đang chạy chế độ Offline chưa có số liệu trích dẫn).")
    else:
        for s in seminals[:10]:
            lines.append(
                f"- **[{s.get('year', 'N/A')}] {s.get('title')}** — *{s.get('venue_display')}* | **{s.get('citations')} trích dẫn** ({s.get('citations_per_year')}/năm) | `{s.get('file_name') or s.get('doi')}`"
            )

    if flagged_sorted:
        lines.extend([
            "",
            "---",
            "",
            "## 3. Khu vực Kiểm chứng Nguồn / Preprint (Tách biệt khỏi nhóm IEEE, ScienceDirect, Nature)",
            "",
            "| # | Năm | Trạng thái nguồn | Tiêu đề & File | Nguồn ghi nhận | Ghi chú xử lý |",
            "| :-: | :-: | :--- | :--- | :--- | :--- |",
        ])
        for idx, r in enumerate(flagged_sorted, 1):
            t_clean = (r.get("title") or "Untitled").replace("|", "\\|")
            f_ref = f"`{r['file_name']}`" if r.get("file_name") else (r.get("doi") or "")
            v_clean = (r.get("venue_display") or "Không rõ").replace("|", "\\|")
            lines.append(
                f"| {idx} | {r.get('year') or 'N/A'} | {r.get('venue_badge')} | {t_clean} ({f_ref}) | {v_clean} | {r.get('recommended_action')} |"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Quét folder PDF bài báo & xếp hạng theo độ mới + uy tín nguồn.")
    parser.add_argument("--dir", type=str, default=".", help="Đường dẫn thư mục chứa các file PDF bài báo.")
    parser.add_argument("--search", type=str, default="", help="Từ khóa chủ đề muốn tìm trực tuyến (OpenAlex) từ nguồn uy tín.")
    parser.add_argument("--max-results", type=int, default=20, help="Số bài tối đa mỗi luồng khi dùng --search.")
    parser.add_argument("--recent-years", type=int, default=3, help="Cửa sổ năm tính là Độ mới học thuật (mặc định: 3 năm gần nhất).")
    parser.add_argument("--min-citations", type=int, default=100, help="Ngưỡng tổng trích dẫn tối thiểu cho bài Nền tảng (Seminal).")
    parser.add_argument("--min-cpy", type=float, default=15.0, help="Ngưỡng trích dẫn/năm tối thiểu cho bài Nền tảng.")
    parser.add_argument("--offline", action="store_true", help="Chỉ quét cục bộ, không gọi API mạng.")
    parser.add_argument("--out-md", type=str, default="", help="File Markdown xuất bảng xếp hạng (mặc định: <dir>/index_triage.md).")
    parser.add_argument("--out-json", type=str, default="", help="File JSON xuất dữ liệu chi tiết (mặc định: <dir>/triage_data.json).")
    parser.add_argument("--extract", type=str, default="", help="Trích xuất văn bản UTF-8 theo trang từ 1 file PDF cụ thể để phục vụ Giải phẫu 3 vòng.")
    parser.add_argument("--max-pages", type=int, default=30, help="Số trang tối đa khi dùng --extract (mặc định: 30).")
    args = parser.parse_args()

    if args.extract.strip():
        pdf_target = Path(args.extract.strip()).expanduser().resolve()
        if not pdf_target.exists() or not pdf_target.is_file():
            print(f"[ERROR] Không tìm thấy file PDF: {pdf_target}", file=sys.stderr)
            return 1
        text, meta = extract_pdf_text_and_meta(pdf_target, max_pages=args.max_pages)
        info = guess_local_info(pdf_target, text, meta)
        print(f"=== METADATA SƠ BỘ: {pdf_target.name} ===")
        print(json.dumps(info, ensure_ascii=False, indent=2))
        print("\n=== NỘI DUNG TRÍCH XUẤT ===")
        print(text)
        return 0

    current_year = datetime.date.today().year
    target_dir = Path(args.dir).expanduser().resolve()
    cache_path = target_dir / ".paper_metadata_cache.json" if target_dir.is_dir() else Path(".paper_metadata_cache.json")

    cache: Dict[str, Any] = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    raw_records: List[Dict[str, Any]] = []

    # Chế độ 1: Quét toàn bộ file PDF trong folder (đệ quy, bỏ qua thư mục ẩn như .git, .claude, .cursor)
    if target_dir.exists() and target_dir.is_dir():
        pdf_files = sorted(
            p for p in target_dir.rglob("*.pdf")
            if not any(part.startswith(".") for part in p.relative_to(target_dir).parts)
        )
        for pdf_path in pdf_files:
            text, meta = extract_pdf_text_and_meta(pdf_path)
            rec = guess_local_info(pdf_path, text, meta)
            if not args.offline:
                rec = enrich_record_online(rec, cache)
            raw_records.append(rec)

    # Chế độ 2: Tìm kiếm thêm trên mạng theo chủ đề từ nguồn uy tín (nếu có --search và không --offline)
    if args.search.strip() and not args.offline:
        online_recs = search_online_topic(args.search.strip(), args.max_results, current_year)
        existing_dois = {r.get("doi") for r in raw_records if r.get("doi")}
        for o_rec in online_recs:
            if not o_rec.get("doi") or o_rec.get("doi") not in existing_dois:
                raw_records.append(o_rec)

    evaluated = [
        evaluate_and_tag(
            r,
            current_year=current_year,
            recent_window=args.recent_years,
            min_citations=args.min_citations,
            min_cpy=args.min_cpy,
        )
        for r in raw_records
    ]
    sorted_all = sort_by_recency(evaluated)

    # Lưu cache metadata nếu có cập nhật online
    if cache and not args.offline:
        try:
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    out_md_path = Path(args.out_md).resolve() if args.out_md else (target_dir / "index_triage.md")
    out_json_path = Path(args.out_json).resolve() if args.out_json else (target_dir / "triage_data.json")

    scan_label = f"Folder: {target_dir}" + (f" + Search: '{args.search}'" if args.search else "")
    md_content = render_markdown_report(sorted_all, scan_label, current_year)

    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_md_path.write_text(md_content, encoding="utf-8")
    out_json_path.write_text(json.dumps(sorted_all, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Đã quét {len(sorted_all)} bài báo.")
    print(f"[OK] Bảng xếp hạng Markdown: {out_md_path}")
    print(f"[OK] Dữ liệu chi tiết JSON:   {out_json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
