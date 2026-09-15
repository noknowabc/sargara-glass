#!/usr/bin/env python3
"""
SARGARA® website builder.

Reads   : data/products.json, data/articles.json
Writes  : index.html, about.html, products.html, applications.html,
          news.html, contact.html, 404.html, sitemap.xml, robots.txt,
          products/<slug>.html, news/<slug>.html

Run:  python3 tools/build_site.py
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "assets", "img")

# --------------------------------------------------------------------------- #
# Site constants
# --------------------------------------------------------------------------- #

SITE = {
    "brand": "SARGARA",
    "brand_reg": "SARGARA®",
    "legal": "SARGARA",
    "group": "SARGARA",
    "tagline": "Make Buildings Better Together",
    "domain": "https://www.sargara.com",
    "address": "No. 1890 Qingqing Road, Zhenhai District, Ningbo, Zhejiang, China",
    "email": "david@china.sargara.com",
    "whatsapp": "+86 188 6868 5020",
    "whatsapp_link": "8618868685020",
    "tel": "+86 188 6868 5020",
    "hotline": "+86 188 6868 5020",
    "hours": "Mon – Sat, 8:30 – 18:00 (GMT+8)",
    "linkedin": "https://www.linkedin.com/",
    "youtube": "https://www.youtube.com/",
    "capacity": "20,000+ tons per month",
}

CATEGORIES = [
    {
        "id": "foil",
        "name": "Aluminum Foil Lamination",
        "short": "Foil Lamination",
        "tagline": "Reflective facings, vapour retarders and laminates for insulation manufacturers.",
        "blurb": "WPM, Aluglass, heat-sealing foil, reinforced foil, AluPET and foil tape — engineered for online lamination of glass wool, rock wool, PUR/PIR panels and HVAC systems.",
        "image": "assets/img/products/fsk-1.jpg",
        "bullets": [
            "FSK, FSV, WMP and WPSK facings",
            "Aluminum foil fiberglass and woven reinforcement",
            "Heat-sealing and adhesive-free laminates",
            "Custom structures, widths, colours and print"
        ],
        "subs": [
            "Aluminum Fiberglass Fabric",
            "Double Sided Aluminum Foil",
            "Aluminum Foil Reinforced Kraft",
            "Reinforced Kraft Paper",
            "Aluminum Foil Woven Fabric",
            "Heat-Sealing Foil",
            "White / Black Film Reinforced Kraft",
            "Aluminum Foil Laminated PE & PET",
            "Adhesive Tape",
        ],
    },
    {
        "id": "roofing",
        "name": "Roofing & Walling",
        "short": "Roofing & Walling",
        "tagline": "Building envelope systems that keep water out and let walls breathe.",
        "blurb": "Synthetic underlayment, breathable membrane, ice & water shield, house wrap, vapour barrier and radiant barrier — supplied as individual layers or as one coordinated envelope system.",
        "image": "assets/img/application-3.jpg",
        "bullets": [
            "SARGARA™ flash-spun HDPE membrane platform",
            "9 ft / 10 ft wide house wrap rolls",
            "Self-adhered ice & water shield",
            "System selection support for each climate"
        ],
        "subs": [
            "Synthetic Underlayment",
            "Ice & Water Shield",
            "House Wrap",
            "Breathable Membrane",
            "Vapour Barrier",
            "Radiant Barrier",
            "Building Envelope Systems",
        ],
    },
    {
        "id": "insulation",
        "name": "Insulation & Acoustic",
        "short": "Insulation & Acoustic",
        "tagline": "CE / FM certified rock wool, glass wool and acoustic ceiling systems.",
        "blurb": "Rock wool board, blanket and pipe, glass wool in the same formats, hydroponic growing media, plus fiberglass ceiling panels, wall panels and suspended baffles.",
        "image": "assets/img/products/rock-wool-board-1.jpg",
        "bullets": [
            "More than 20,000 tons monthly capacity",
            "FM, CE and CCS certified production",
            "Board, blanket, pipe and custom shapes",
            "Acoustic panels with a wide choice of facings"
        ],
        "subs": [
            "Rock Wool Board",
            "Rock Wool Blanket",
            "Rock Wool Pipe",
            "Glass Wool Board",
            "Glass Wool Blanket",
            "Glass Wool Pipe",
            "Acoustic Ceiling & Wall Panels",
            "Hydroponic Rock Wool",
        ],
    },
    {
        "id": "fiberglass",
        "name": "Fiberglass",
        "short": "Fiberglass",
        "tagline": "Tissue, mat and woven fabric for facings, boards and composites.",
        "blurb": "Fiberglass tissue, black glass veil, coated fiberglass mat, woven E-glass fabric and silicone coated fabric — controlled thickness, weight and strength.",
        "image": "assets/img/products/fiberglass-fabric-series-1.jpg",
        "bullets": [
            "E-glass yarn, modern weaving technology",
            "Coated and uncoated mat options",
            "Gypsum, acoustic and insulation board facings",
            "Silicone coated fabric for duct and industry"
        ],
        "subs": [
            "Fiberglass Tissue & BGT",
            "Coated Fiberglass Mat",
            "Fiberglass Fabric Series",
            "Coated Fiberglass Fabric",
        ],
    },
]

APPLICATIONS = [
    {
        "slug": "metal-building-insulation",
        "tag": "Metal Building",
        "title": "Metal Building Insulation",
        "image": "assets/img/application-1.jpg",
        "summary": "Faced glass wool and rock wool blankets engineered for the metal building market, with facings that protect insulation from physical abuse and moisture.",
        "body": "SARGARA supplies insulation vapour retarders and facings to the Metal Building Insulation market. Our facings are designed with proprietary flame-retardant chemistry to help you meet demanding fire codes and standards, and can be laminated online for consistent output.",
        "products": ["fsk", "white-film-reinforced-kraft-wmp-series", "glass-wool-blanket", "rock-wool-blanket"],
    },
    {
        "slug": "hvac-duct",
        "tag": "HVAC",
        "title": "HVAC, Duct Wrap & Duct Board",
        "image": "assets/img/application-1.jpg",
        "summary": "Foil facings, duct board liners and acoustic membranes that seal air paths and keep insulated ducts performing over decades.",
        "body": "HVAC insulation facing is not just an outer covering. The right facing protects insulation, controls moisture vapour, improves durability and delivers the finished appearance that specifiers expect on exposed ductwork.",
        "products": ["fsk", "double-sided-aluminum-foil", "adhesive-tape", "coated-fiberglass-fabric"],
    },
    {
        "slug": "roofing-systems",
        "tag": "Roofing",
        "title": "Roofing & Underlayment Systems",
        "image": "assets/img/application-3.jpg",
        "summary": "Complete secondary roof protection: synthetic underlayment, ice & water shield, sarking and radiant barrier.",
        "body": "Modern roofing systems need more than traditional felt. Our underlayment range is designed for wind uplift resistance, anti-slip installation and long term protection of the roof deck in every climate.",
        "products": ["synthetic-underlayment", "ice-and-water-shield", "roof-sarking", "radiant-barrier"],
    },
    {
        "slug": "wall-envelope",
        "tag": "Walls",
        "title": "Wall Weather Barriers & WRB",
        "image": "assets/img/application-2.jpg",
        "summary": "House wrap and breathable membranes that manage moisture across wood frame, light steel frame and modular construction.",
        "body": "Exterior walls need to shed bulk water while allowing vapour to escape. Our WRB range combines tear strength, controlled vapour permeability and wide roll formats that reduce installation time on site.",
        "products": ["house-wrap", "sargara-b2066-hdpe-house-wrap", "breathable-membrane", "vapor-barrier"],
    },
    {
        "slug": "pur-pir-panels",
        "tag": "Panels",
        "title": "PUR / PIR Insulated Panels",
        "image": "assets/img/products/aluminum-foil-laminated-pe-pet-1.jpg",
        "summary": "Heat-sealing foil and multi-layer facings developed for continuous lamination of insulated panel lines.",
        "body": "Panel producers need facings that bond reliably at line speed, resist handling damage and deliver a stable finished surface. Our heat-sealing and ALU/PET/PE constructions are engineered for automated processing.",
        "products": ["heat-sealing-foil-2", "aluminum-foil-laminated-pe-pet", "aluglass", "reinforced-kraft-paper-facing"],
    },
    {
        "slug": "industrial-pipe",
        "tag": "Industrial",
        "title": "Industrial & Pipe Insulation",
        "image": "assets/img/products/aluglass-1.jpg",
        "summary": "Rock wool and glass wool pipe sections, heavy-duty foil facings and jacketing for high temperature service.",
        "body": "Process piping, tanks and equipment need insulation that survives temperature cycling and mechanical abuse. We supply pre-formed pipe sections and heavy duty facings as a matched package.",
        "products": ["rock-wool-pipe", "glass-wool-pipe", "aluglass", "adhesive-tape"],
    },
    {
        "slug": "cold-storage",
        "tag": "Cold Room",
        "title": "Cold Room & Refrigeration",
        "image": "assets/img/products/vapor-barrier-1.jpg",
        "summary": "Vapour barriers and reflective composites that control condensation in chilled and frozen environments.",
        "body": "In cold rooms the vapour barrier is the critical layer. We supply reflective vapour control membranes and high barrier foil composites that keep moisture where it belongs and protect panel performance.",
        "products": ["vapor-barrier", "aluminum-foil-laminated-pe-pet", "double-sided-aluminum-foil", "radiant-barrier"],
    },
    {
        "slug": "acoustic-interiors",
        "tag": "Acoustic",
        "title": "Acoustic Ceilings & Interiors",
        "image": "assets/img/products/fiberglass-ceiling-panel-1.jpg",
        "summary": "Fiberglass ceiling panels, wall panels and suspended baffles for public and commercial interiors.",
        "body": "Acoustic comfort is a specification, not an afterthought. Our glass wool panels are produced with high density cores and a wide choice of facings, edge details and formats.",
        "products": ["fiberglass-ceiling-panel", "fiberglass-wall-panel", "fiberglass-suspended-baffle", "coated-fiberglass-mat"],
    },
    {
        "slug": "hydroponics",
        "tag": "Horticulture",
        "title": "Hydroponic Growing Media",
        "image": "assets/img/products/hydroponic-rock-wool-cube-1.jpg",
        "summary": "Sterile rock wool plugs, cubes, blocks and slabs for commercial soilless cultivation.",
        "body": "Hydroponic substrates demand uniform fibre structure, controlled density and consistent water-air balance. Our rock wool growing media are produced on the same certified mineral wool lines as our construction products.",
        "products": ["hydroponic-rock-wool-cube", "rock-wool-blanket", "rock-wool-board"],
    },
]

CERTIFICATIONS = [
    ("ISO 9001", "Quality management system"),
    ("ISO 14001", "Environmental management"),
    ("ISO 45001", "Occupational health & safety"),
    ("FM Approved", "Rock wool & mineral wool production"),
    ("CE Marking", "European conformity for mineral wool"),
    ("EN 13501-1 B-s1,d0", "SARGARA B2066 flame classification"),
    ("SGS Tested", "Membranes and WRB performance"),
    ("CCS Certified", "Marine & industrial mineral wool"),
]

MARKETS = [
    ("North America", "US and Canada focused WRB, synthetic underlayment and ice & water shield programmes, supported by DDP delivery options."),
    ("Europe", "CE-marked mineral wool, EN 13501-1 fire classified membranes and facings aligned to European project specifications."),
    ("Australia & New Zealand", "Roof sarking, breathable membranes and foil facings matched to AS/NZS building practice and harsh UV conditions."),
    ("Middle East", "High reflectivity radiant barriers, vapour control and insulation systems for extreme heat and desert climates."),
    ("South America", "Cost-optimised foil composites, mineral wool and envelope materials for distributors and contractors."),
    ("Asia-Pacific", "Full portfolio supply with short lead times, regional documentation and multilingual commercial support."),
]

PROCESS = [
    ("Enquiry & Specification", "Send your specification, drawing, sample or target price. We confirm the structure and performance required."),
    ("Engineering & Sampling", "Our technical team proposes a construction, produces samples and confirms the data sheet parameters."),
    ("Quotation & Terms", "Clear pricing on FOB, CIF or DDP terms, with lead time, packing and payment terms stated up front."),
    ("Production & QC", "In-house laminating, coating and converting with raw material, in-process and pre-shipment inspection."),
    ("Shipping & After-Sales", "Container loading supervision, full documentation and technical follow-up after the goods arrive."),
]

CAPABILITIES = [
    ("Laminating", "Online and offline lamination of foil, scrim, kraft, PE, PET and fiberglass substrates with controlled tension and adhesion.", "layers"),
    ("Coating", "Flame-retardant, colour and functional coatings applied with consistent coat weight across the web.", "droplet"),
    ("Weaving & Converting", "Slitting, rewinding, printing, perforating and packaging — so material arrives ready for your line.", "spool"),
    ("Quality Control", "Raw material inspection, in-process monitoring, finished product testing and pre-shipment verification.", "shield-check"),
    ("Engineering & R&D", "Rapid prototyping of new constructions, benchmarking against leading global products, and private-label development.", "flask"),
    ("Customisation", "Roll width, length, basis weight, colour, surface texture, logo, fire performance, UV resistance and packaging.", "sliders"),
]

WHY_US = [
    ("Integrated system supplier", "We develop materials that are designed to be used together — fewer compatibility problems, one shipment, one set of documents.", "layers"),
    ("Four manufacturing platforms", "Foil lamination, roofing & walling, insulation & acoustic and fiberglass production under one organisation.", "factory"),
    ("OEM & private label", "Your logo, your label, your colour, your packaging — from one container to annual programmes.", "tag"),
    ("Wide width capability", "Production lines able to deliver wide rolls and 9 ft / 10 ft formats that reduce installation labour.", "arrows"),
    ("One-stop sourcing & DDP", "Lower procurement cost and fewer suppliers to manage, with door-to-door delivery to the USA and Canada.", "truck"),
    ("Export team that answers", "Engineers and export specialists who understand regional regulations, climates and technical standards.", "globe"),
]

FAQ = [
    (
        "Can you produce to our own specification or private label?",
        "Yes. OEM and private-label production is one of our core capabilities. We customise structure, roll width, length, basis weight, colour, surface texture, logo, fire performance, UV resistance and packaging, then supply under your own brand and documentation.",
    ),
    (
        "Which certifications can you supply?",
        "Our management systems are certified to ISO 9001, ISO 14001 and ISO 45001. Selected products are tested or certified to relevant international standards including FM, CE, TÜV, CCS and SGS, with EN 13501-1 fire classification achieved for our SARGARA B2066 membrane.",
    ),
    (
        "What are your minimum order quantities?",
        "MOQ depends on the product and the level of customisation. Standard items can often be shipped from a single pallet, while custom laminated structures are usually quoted from one 20 ft container. Tell us your target volume and we will confirm what is practical.",
    ),
    (
        "Can you deliver door to door?",
        "Yes. We quote FOB, CIF and DDP. Our DDP service to the USA and Canada has reduced sourcing costs for customers by 20–30% by removing freight, customs and inland delivery from their workload.",
    ),
    (
        "How do you control quality before shipment?",
        "Quality control covers raw material inspection, in-process monitoring, finished product testing and pre-shipment verification. Inspection reports, test data and loading photos are provided with the shipping documents.",
    ),
    (
        "How quickly will I get a reply?",
        "Our export team replies within one working day. WhatsApp and email are the fastest routes; both are monitored outside Chinese business hours for urgent enquiries.",
    ),
]

ICONS = {
    "layers": '<path d="M12 3 3 7.5l9 4.5 9-4.5L12 3Z"/><path d="m3 12.5 9 4.5 9-4.5"/><path d="m3 17 9 4.5 9-4.5"/>',
    "droplet": '<path d="M12 3s6 6.4 6 10.6A6 6 0 0 1 6 13.6C6 9.4 12 3 12 3Z"/>',
    "spool": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.6"/><path d="M12 4v3M12 17v3M4 12h3M17 12h3"/>',
    "shield-check": '<path d="M12 3l7 3v5.5c0 4.3-2.9 7.9-7 9-4.1-1.1-7-4.7-7-9V6l7-3Z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "flask": '<path d="M9 3h6M10 3v5.2L5.6 17A2.4 2.4 0 0 0 7.7 21h8.6a2.4 2.4 0 0 0 2.1-4L14 8.2V3"/><path d="M7.5 15h9"/>',
    "sliders": '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
    "factory": '<path d="M3 21V10l5 3V10l5 3V8l5 3v10H3Z"/><path d="M7 21v-4M12 21v-4M17 21v-4"/>',
    "tag": '<path d="M3 12V4h8l9 9-8 8-9-9Z"/><circle cx="7.5" cy="8" r="1.4"/>',
    "arrows": '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
    "truck": '<path d="M3 7h10v8H3z"/><path d="M13 10h4l3 3v2h-7z"/><circle cx="7" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.4 2.6 3.6 5.6 3.6 9S14.4 18.4 12 21c-2.4-2.6-3.6-5.6-3.6-9S9.6 5.6 12 3Z"/>',
    "phone": '<path d="M5 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L15 13l5 2v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 3 5.2 2 2 0 0 1 5 3Z"/>',
    "mail": '<path d="M3 6h18v12H3z"/><path d="m3 7 9 6 9-6"/>',
    "pin": '<path d="M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.4l3.4 2"/>',
    "whatsapp": '<path d="M20.5 11.6A8.4 8.4 0 0 1 8 19.3L3.6 20.4l1.1-4.3A8.4 8.4 0 1 1 20.5 11.6Z"/><path d="M9.2 8.4c.3-.6.6-.5.9-.5h.7c.2 0 .5 0 .7.6l.7 1.7c.1.3 0 .5-.1.7l-.6.7c-.2.2-.2.4-.1.6a5.6 5.6 0 0 0 2.6 2.3c.3.1.5 0 .7-.2l.7-.8c.2-.2.4-.2.6-.1l1.7.9c.4.2.5.4.4.7a2 2 0 0 1-1.8 1.5c-1.4.1-3.6-.9-5.2-2.5s-2.5-3.7-2.4-5A2 2 0 0 1 9.2 8.4Z"/>',
    "arrow": '<path d="M5 12h13M13 6l6 6-6 6"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/>',
    "download": '<path d="M12 4v10M8 11l4 4 4-4"/><path d="M5 19h14"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "play": '<circle cx="12" cy="12" r="9"/><path d="M10 8.5 16 12l-6 3.5z"/>',
    "linkedin": '<path d="M6 9v9M6 6.2v.1"/><path d="M11 18v-5.2a2.6 2.6 0 0 1 5.2 0V18"/><path d="M11 9v9"/>',
    "youtube": '<rect x="3" y="6" width="18" height="12" rx="3.4"/><path d="M11 10.2 14.8 12 11 13.8z"/>',
    "arrow-up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def e(value) -> str:
    return html.escape(str(value), quote=True)


def icon(name: str, size: int = 20, cls: str = "") -> str:
    body = ICONS.get(name, "")
    klass = f' class="{cls}"' if cls else ""
    return (
        f'<svg{klass} width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def asset_variants(slug: str) -> list[str]:
    """Return every existing image for a product slug, first one first."""
    base = os.path.join(IMG, "products")
    found = []
    for suffix in ["-1", "-2", ""]:
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            name = f"{slug}{suffix}{ext}"
            if os.path.exists(os.path.join(base, name)):
                found.append(f"assets/img/products/{name}")
                break
    return found or ["assets/img/application-1.jpg"]


def slug_to_url(slug: str) -> str:
    return f"products/{slug}.html"


ARTICLE_CARD_IMAGES = {
    "Foil Lamination": [
        "assets/img/products/fsk-1.jpg",
        "assets/img/products/double-sided-aluminum-foil-1.jpg",
        "assets/img/products/aluglass-1.jpg",
        "assets/img/products/heat-sealing-foil-2-1.jpg",
    ],
    "Building Envelope": [
        "assets/img/application-2.jpg",
        "assets/img/application-3.jpg",
        "assets/img/team-planning.jpg",
    ],
    "Roofing": [
        "assets/img/application-3.jpg",
        "assets/img/products/synthetic-underlayment-1.jpg",
    ],
    "HVAC & Duct": [
        "assets/img/application-1.jpg",
        "assets/img/products/adhesive-tape-1.jpg",
    ],
    "Mineral Wool": [
        "assets/img/products/rock-wool-board-1.jpg",
        "assets/img/products/glass-wool-blanket-1.jpg",
        "assets/img/products/rock-wool-blanket-1.jpg",
    ],
    "Sourcing": [
        "assets/img/team-engineers.jpg",
        "assets/img/application-1.jpg",
    ],
}


def article_card_image(article: dict) -> str:
    """Cards use clean photography; the original poster stays on the article page."""
    pool = ARTICLE_CARD_IMAGES.get(article["topic"])
    if not pool:
        return article["image"]
    index = next(
        (i for i, a in enumerate(ARTICLES) if a["slug"] == article["slug"]), 0
    )
    return pool[index % len(pool)]


def w(rel: str, path: str) -> str:
    return f"{rel}{path}"


# --------------------------------------------------------------------------- #
# Layout
# --------------------------------------------------------------------------- #


def head(title: str, description: str, rel: str = "", canonical: str = "", extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical or SITE['domain'])}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:site_name" content="SARGARA® Building Materials">
<meta name="theme-color" content="#06203f">
<link rel="icon" href="{rel}assets/img/logo-mark.svg" type="image/svg+xml">
<link rel="icon" href="{rel}assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{rel}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/css/main.css">
{extra}</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>"""


def topbar(rel: str) -> str:
    return f"""<div class="topbar">
  <div class="container topbar__inner">
    <ul class="topbar__list">
      <li><span class="topbar__label" data-i18n="top.hotline">Sales &amp; WhatsApp</span> <a href="tel:{SITE['tel'].replace(' ', '')}">{SITE['tel']}</a></li>
      <li><a href="mailto:{SITE['email']}">{icon('mail', 15)} {SITE['email']}</a></li>
      <li><span>{icon('pin', 15)}</span> <span>Ningbo, Zhejiang, China</span></li>
    </ul>
    <div class="lang">
      <button class="lang__current" type="button" aria-expanded="false" aria-label="Change language">
        {icon('globe', 15)} <span data-lang-label>English</span> {icon('chevron', 14)}
      </button>
      <div class="lang__menu" role="menu">
        <button type="button" data-lang="en" data-lang-name="English" aria-pressed="true">English <span>EN</span></button>
        <button type="button" data-lang="zh" data-lang-name="中文" aria-pressed="false">中文 <span>ZH</span></button>
        <button type="button" data-lang="es" data-lang-name="Español" aria-pressed="false">Español <span>ES</span></button>
        <button type="button" data-lang="fr" data-lang-name="Français" aria-pressed="false">Français <span>FR</span></button>
        <button type="button" data-lang="ru" data-lang-name="Русский" aria-pressed="false">Русский <span>RU</span></button>
      </div>
    </div>
  </div>
</div>"""


def mega_menu(rel: str) -> str:
    cols = []
    for cat in CATEGORIES:
        items = []
        for prod in PRODUCTS:
            if prod["category"] == cat["id"]:
                items.append(
                    f'<li><a href="{rel}{slug_to_url(prod["slug"])}">{e(prod["name"])}</a></li>'
                )
        cols.append(
            f"""<div class="mega__col">
      <h4><a href="{rel}products.html?cat={cat['id']}" style="color:inherit">{e(cat['short'])}</a></h4>
      <ul>{''.join(items)}</ul>
    </div>"""
        )
    return f'<div class="mega">{"".join(cols)}</div>'


def header(active: str, rel: str = "") -> str:
    def cls(key):
        return ' class="nav__item is-active"' if key == active else ' class="nav__item"'

    return f"""{topbar(rel)}
<header class="site-header">
  <div class="container header__inner">
    <a class="brand" href="{rel}index.html" aria-label="SARGARA home">
      <img src="{rel}assets/img/logo.svg" alt="SARGARA — Building Materials" width="184" height="44">
    </a>
    <nav class="nav" aria-label="Main">
      <ul class="nav__list">
        <li{cls('home')}><a class="nav__link" href="{rel}index.html" data-i18n="nav.home">Home</a></li>
        <li{cls('products')}>
          <a class="nav__link" href="{rel}products.html" data-i18n="nav.products">Products</a>
          {mega_menu(rel)}
        </li>
        <li{cls('about')}><a class="nav__link" href="{rel}about.html" data-i18n="nav.about">About Us</a></li>
        <li{cls('applications')}><a class="nav__link" href="{rel}applications.html" data-i18n="nav.applications">Applications</a></li>
        <li{cls('news')}><a class="nav__link" href="{rel}news.html" data-i18n="nav.news">Knowledge</a></li>
        <li{cls('contact')}><a class="nav__link" href="{rel}contact.html" data-i18n="nav.contact">Contact</a></li>
      </ul>
    </nav>
    <div class="header__actions">
      <div class="header__phone">
        <span data-i18n="top.whatsapp">WhatsApp</span>
        <strong>{SITE['whatsapp']}</strong>
      </div>
      <a class="btn btn--primary" href="{rel}contact.html#inquiry" data-i18n="cta.quote">Request a Quote</a>
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="drawer"><span></span></button>
    </div>
  </div>
</header>
<div class="drawer" id="drawer">
  <div class="drawer__scrim" data-drawer-close></div>
  <div class="drawer__panel" role="dialog" aria-modal="true" aria-label="Menu">
    <div class="drawer__head">
      <strong style="font-family:var(--display);letter-spacing:.06em">SARGARA®</strong>
      <button class="drawer__close" type="button" data-drawer-close aria-label="Close menu">✕</button>
    </div>
    <nav aria-label="Mobile">
      <a href="{rel}index.html" data-i18n="nav.home">Home</a>
      <a href="{rel}products.html" data-i18n="nav.products">Products</a>
      {''.join(f'<div class="drawer__group-title">{e(c["short"])}</div><div class="drawer__sub"><a href="{rel}products.html?cat={c["id"]}">{e(" / ".join(c["subs"][:4]))}</a></div>' for c in CATEGORIES)}
      <a href="{rel}about.html" data-i18n="nav.about">About Us</a>
      <a href="{rel}applications.html" data-i18n="nav.applications">Applications</a>
      <a href="{rel}news.html" data-i18n="nav.news">Knowledge</a>
      <a href="{rel}contact.html" data-i18n="nav.contact">Contact</a>
    </nav>
    <div class="drawer__contact">
      <strong>Talk to our export team</strong>
      <a href="tel:{SITE['tel'].replace(' ', '')}">{SITE['tel']}</a>
      <a href="mailto:{SITE['email']}">{SITE['email']}</a>
      <a class="btn btn--primary btn--block" style="margin-top:14px" href="{rel}contact.html#inquiry" data-i18n="cta.quote">Request a Quote</a>
    </div>
  </div>
</div>"""


def footer(rel: str) -> str:
    cols = []
    for cat in CATEGORIES:
        links = "".join(
            f'<li><a href="{rel}{slug_to_url(p["slug"])}">{e(p["name"])}</a></li>'
            for p in PRODUCTS
            if p["category"] == cat["id"]
        )
        cols.append(f'<div><h4>{e(cat["short"])}</h4><ul class="footer__links">{links}</ul></div>')

    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer__top">
      <div class="footer__brand">
        <img src="{rel}assets/img/logo-white.svg" alt="SARGARA — Building Materials" width="192" height="46">
        <p>{SITE['legal']} supplies building envelope, thermal insulation, acoustic and fiberglass materials to distributors, importers, contractors and private-label brands worldwide.</p>
        <div class="footer__social">
          <a href="{SITE['linkedin']}" aria-label="LinkedIn" rel="noopener">{icon('linkedin', 18)}</a>
          <a href="{SITE['youtube']}" aria-label="YouTube" rel="noopener">{icon('youtube', 18)}</a>
          <a href="https://wa.me/{SITE['whatsapp_link']}" aria-label="WhatsApp" rel="noopener">{icon('whatsapp', 18)}</a>
        </div>
      </div>
      <div>
        <h4 data-i18n="footer.company">Company</h4>
        <ul class="footer__links">
          <li><a href="{rel}about.html" data-i18n="nav.about">About Us</a></li>
          <li><a href="{rel}products.html" data-i18n="cta.viewCatalogue">View Full Catalogue</a></li>
          <li><a href="{rel}applications.html" data-i18n="nav.applications">Applications</a></li>
          <li><a href="{rel}news.html" data-i18n="nav.news">Knowledge</a></li>
          <li><a href="{rel}about.html#certifications">Certifications</a></li>
          <li><a href="{rel}about.html#oem">OEM &amp; Private Label</a></li>
          <li><a href="{rel}contact.html" data-i18n="nav.contact">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="footer.categories">Product Categories</h4>
        <ul class="footer__links">
          {''.join(f'<li><a href="{rel}products.html?cat={c["id"]}">{e(c["name"])}</a></li>' for c in CATEGORIES)}
          <li><a href="{rel}products.html">All products (34)</a></li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="footer.contact">Contact</h4>
        <ul class="footer__contact">
          <li>{icon('pin', 18)}<span>{SITE['address']}</span></li>
          <li>{icon('mail', 18)}<a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
          <li>{icon('whatsapp', 18)}<a href="https://wa.me/{SITE['whatsapp_link']}" rel="noopener">WhatsApp {SITE['whatsapp']}</a></li>
          <li>{icon('phone', 18)}<a href="tel:{SITE['tel'].replace(' ', '')}">Tel {SITE['tel']}</a></li>
          <li>{icon('clock', 18)}<span>{SITE['hours']}</span></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>Copyright © <span data-year>2026</span> SARGARA. <span data-i18n="footer.rights">All rights reserved.</span></span>
      <nav>
        <a href="{rel}contact.html#privacy" data-i18n="footer.privacy">Privacy Policy</a>
        <a href="{rel}contact.html#terms" data-i18n="footer.terms">Terms of Use</a>
        <a href="{rel}about.html" data-i18n="footer.sitemap">Sitemap</a>
      </nav>
    </div>
  </div>
</footer>
<div class="floaties">
  <a class="floaty floaty--wa" href="https://wa.me/{SITE['whatsapp_link']}" aria-label="Chat on WhatsApp" rel="noopener">{icon('whatsapp', 26)}</a>
  <button class="floaty floaty--top" type="button" aria-label="Back to top">{icon('arrow-up', 22)}</button>
</div>
<script src="{rel}assets/js/i18n.js"></script>
<script src="{rel}assets/js/main.js"></script>
</body>
</html>"""


def page_hero(title_html: str, lead: str, crumbs: list[tuple[str, str]], rel: str,
              image: str = "assets/img/application-3.jpg", extra: str = "") -> str:
    crumb_html = ""
    for i, (label, href) in enumerate(crumbs):
        if href:
            crumb_html += f'<a href="{rel}{href}">{e(label)}</a>'
        else:
            crumb_html += f"<span>{e(label)}</span>"
        if i < len(crumbs) - 1:
            crumb_html += "<span>/</span>"
    return f"""<section class="page-hero">
  <div class="page-hero__bg"><img src="{rel}{image}" alt="" loading="eager"></div>
  <div class="container page-hero__inner">
    <div class="crumbs">{crumb_html}</div>
    <h1>{title_html}</h1>
    <p class="lead" style="max-width:760px;margin-bottom:0">{lead}</p>
    {extra}
  </div>
</section>"""


def inquiry_form(rel: str, compact: bool = False, heading: str = "Request a quotation",
                 sub: str = "Tell us what you need and our export team will reply within one working day.",
                 preselect: str = "") -> str:
    options = "".join(
        f'<option value="{e(p["name"])}"{" selected" if p["name"] == preselect else ""}>{e(p["name"])}</option>'
        for p in PRODUCTS
    )
    return f"""<div class="form-card">
  <div class="form-alert" data-form-alert>{icon('check', 18)} <span data-i18n="form.success">Thank you — your enquiry has been received. Our export team will contact you shortly.</span></div>
  <h3 style="margin-bottom:6px">{e(heading)}</h3>
  <p style="font-size:.9rem;color:var(--ink-500)">{e(sub)}</p>
  <form data-validate novalidate>
    <div class="form-grid">
      <div class="field">
        <label for="f-name"><span data-i18n="form.name">Full name</span> <span class="req">*</span></label>
        <input id="f-name" name="name" type="text" required autocomplete="name">
        <span class="error">Please enter your name.</span>
      </div>
      <div class="field">
        <label for="f-company" data-i18n="form.company">Company</label>
        <input id="f-company" name="company" type="text" autocomplete="organization">
        <span class="error"></span>
      </div>
      <div class="field">
        <label for="f-email"><span data-i18n="form.email">Business email</span> <span class="req">*</span></label>
        <input id="f-email" name="email" type="email" required autocomplete="email">
        <span class="error">Please enter a valid email address.</span>
      </div>
      <div class="field">
        <label for="f-wa" data-i18n="form.whatsapp">WhatsApp / Phone</label>
        <input id="f-wa" name="phone" type="tel" autocomplete="tel">
        <span class="error">Please enter a valid phone number.</span>
      </div>
      <div class="field">
        <label for="f-country" data-i18n="form.country">Country</label>
        <input id="f-country" name="country" type="text" autocomplete="country-name">
        <span class="error"></span>
      </div>
      <div class="field">
        <label for="f-product" data-i18n="form.product">Product of interest</label>
        <select id="f-product" name="product">
          <option value="" data-i18n="form.selectProduct">Please select…</option>
          {options}
          <option value="Other / not listed">Other / not listed</option>
        </select>
        <span class="error"></span>
      </div>
      <div class="field field--full">
        <label for="f-qty" data-i18n="form.quantity">Estimated quantity</label>
        <input id="f-qty" name="quantity" type="text" placeholder="e.g. 2 × 40HQ per month">
        <span class="error"></span>
      </div>
      <div class="field field--full">
        <label for="f-msg"><span data-i18n="form.message">Your requirement</span> <span class="req">*</span></label>
        <textarea id="f-msg" name="message" required data-i18n-placeholder="form.messagePlaceholder"></textarea>
        <span class="error">Please tell us what you need.</span>
      </div>
    </div>
    <button class="btn btn--primary btn--block" type="submit" style="margin-top:18px" data-i18n="form.submit">Send Enquiry</button>
    <p class="form-note" data-i18n="form.note">We reply within one working day. Your information stays confidential and is never shared.</p>
  </form>
</div>"""


def cta_band(rel: str) -> str:
    return f"""<section class="section cta-band on-dark">
  <div class="container cta-band__inner">
    <div>
      <h2 data-i18n="band.title">Let's build your next project together</h2>
      <p data-i18n="band.lead">Send us your specification, drawing or sample requirement. Our export team replies within one working day.</p>
    </div>
    <div class="btn-row">
      <a class="btn btn--white" href="{rel}contact.html#inquiry" data-i18n="cta.quote">Request a Quote</a>
      <a class="btn btn--light" href="https://wa.me/{SITE['whatsapp_link']}" rel="noopener">{icon('whatsapp', 18)} WhatsApp</a>
    </div>
  </div>
</section>"""


# --------------------------------------------------------------------------- #
# Components
# --------------------------------------------------------------------------- #


def product_card(prod: dict, rel: str = "", reveal: int = 0) -> str:
    img = asset_variants(prod["slug"])[0]
    delay = f' data-reveal-delay="{reveal}"' if reveal else ""
    return f"""<article class="product-card" data-cats="{e(prod['category'])}" data-search="{e(prod['name'] + ' ' + prod['sub'] + ' ' + prod['group'] + ' ' + prod['alias'])}"{delay} data-reveal>
  <div class="product-card__media">
    <img src="{rel}{img}" alt="{e(prod['name'])}" loading="lazy" width="600" height="600">
    <span class="product-card__tag">{e(prod['sub'])}</span>
  </div>
  <div class="product-card__body">
    <h3><a href="{rel}{slug_to_url(prod['slug'])}">{e(prod['name'])}</a></h3>
    <p>{e(prod['summary'])}</p>
    <div class="product-card__foot">
      <span class="product-card__cat">{e(prod['group'])}</span>
      <a class="link-arrow" href="{rel}{slug_to_url(prod['slug'])}" data-i18n="cta.viewDetails">View Details</a>
    </div>
  </div>
</article>"""


def news_card(article: dict, rel: str = "", reveal: int = 0) -> str:
    delay = f' data-reveal-delay="{reveal}"' if reveal else ""
    pretty = date.fromisoformat(article["date"]).strftime("%b %d, %Y")
    return f"""<article class="news-card"{delay} data-reveal>
  <a class="news-card__media" href="{rel}news/{article['slug']}.html" aria-label="{e(article['title'])}">
    <img src="{rel}{article_card_image(article)}" alt="{e(article['title'])}" loading="lazy" width="640" height="360">
  </a>
  <div class="news-card__body">
    <div class="news-card__meta">
      <span class="news-card__cat">{e(article['topic'])}</span>
      <span>{pretty}</span>
      <span>· {article['minutes']} min read</span>
    </div>
    <h3><a href="{rel}news/{article['slug']}.html">{e(article['title'])}</a></h3>
    <p>{e(article['excerpt'] or '')}</p>
    <a class="link-arrow" href="{rel}news/{article['slug']}.html" data-i18n="cta.readMore">Read More</a>
  </div>
</article>"""


def feature_card(title: str, text: str, icon_name: str, reveal: int = 0) -> str:
    return f"""<div class="feature-card" data-reveal data-reveal-delay="{reveal}">
  <div class="feature-card__icon">{icon(icon_name, 24)}</div>
  <h3>{e(title)}</h3>
  <p>{e(text)}</p>
</div>"""


def pillar_card(cat: dict, index: int, rel: str = "", reveal: int = 0) -> str:
    bullets = "".join(f"<li>{e(b)}</li>" for b in cat["bullets"])
    return f"""<article class="pillar" data-reveal data-reveal-delay="{reveal}">
  <div class="pillar__media">
    <img src="{rel}{cat['image']}" alt="{e(cat['name'])}" loading="lazy" width="640" height="480">
    <span class="pillar__index">0{index}</span>
  </div>
  <div class="pillar__body">
    <h3>{e(cat['name'])}</h3>
    <p>{e(cat['blurb'])}</p>
    <ul class="pillar__list">{bullets}</ul>
    <a class="link-arrow" href="{rel}products.html?cat={cat['id']}" data-i18n="cta.viewProducts">View Products</a>
  </div>
</article>"""


def faq_block(items: list[tuple[str, str]]) -> str:
    rows = "".join(
        f"""<details style="border:1px solid var(--line);border-radius:var(--radius);padding:18px 22px;background:#fff;margin-bottom:12px">
  <summary style="cursor:pointer;font-family:var(--display);font-weight:600;color:var(--ink-900);list-style:none;display:flex;justify-content:space-between;gap:16px;align-items:center">
    {e(q)}<span style="color:var(--brand-600);flex:none">{icon('chevron', 18)}</span>
  </summary>
  <p style="margin:14px 0 0;font-size:.94rem;color:var(--ink-500);line-height:1.7">{e(a)}</p>
</details>"""
        for q, a in items
    )
    return rows


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #


def build_index() -> str:
    rel = ""
    featured = [p for p in PRODUCTS if p["slug"] in {
        "aluglass", "fsk", "heat-sealing-foil-2", "white-film-reinforced-kraft-wmp-series",
        "house-wrap", "sargara-b2066-hdpe-house-wrap", "synthetic-underlayment", "ice-and-water-shield",
    }]
    latest = ARTICLES[:3]

    trust = "".join(
        f'<span class="trustbar__item">{e(name)}</span>'
        for name in ["ISO 9001", "ISO 14001", "ISO 45001", "FM Approved", "CE", "SGS Tested", "CCS"]
    )

    body = f"""
<section class="hero">
  <div class="hero__bg"><img src="assets/img/application-3.jpg" alt="" fetchpriority="high"></div>
  <div class="container hero__inner">
    <div class="hero__content">
      <span class="eyebrow" data-i18n="hero.eyebrow">Building materials manufacturer &amp; supplier</span>
      <h1 data-i18n="hero.title">Make Buildings <em>Better</em>, Together.</h1>
      <p class="hero__sub" data-i18n="hero.lead">SARGARA® manufactures foil lamination, roofing &amp; walling underlayments, thermal insulation and acoustic materials — supplied to distributors, importers, contractors and private-label brands in more than 80 countries.</p>
      <div class="hero__pillars">
        <span data-i18n="hero.p1">Foil Lamination</span>
        <span data-i18n="hero.p2">Roofing &amp; Walling</span>
        <span data-i18n="hero.p3">Insulation &amp; Acoustic</span>
        <span data-i18n="hero.p4">Fiberglass</span>
      </div>
      <div class="btn-row">
        <a class="btn btn--primary" href="contact.html#inquiry" data-i18n="cta.quote">Request a Quote</a>
        <a class="btn btn--light" href="products.html" data-i18n="cta.viewCatalogue">View Full Catalogue</a>
      </div>
    </div>
    <div class="hero__stats">
      <div class="hero__stat"><b>34+</b><span data-i18n="stats.years">Product families</span></div>
      <div class="hero__stat"><b>20k t</b><span data-i18n="stats.capacity">Monthly insulation capacity</span></div>
      <div class="hero__stat"><b>80+</b><span data-i18n="stats.countries">Export markets served</span></div>
      <div class="hero__stat"><b>4</b><span data-i18n="stats.skus">Manufacturing platforms</span></div>
    </div>
  </div>
</section>

<div class="trustbar">
  <div class="container trustbar__inner">
    <span class="trustbar__label">Certified &amp; tested to</span>
    {trust}
  </div>
</div>

<section class="section" id="products">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow" data-i18n="sec.products.eyebrow">Product portfolio</span>
      <h2 data-i18n="sec.products.title">Four manufacturing platforms, one supply partner</h2>
      <p class="lead" data-i18n="sec.products.lead">From reflective foil facings to complete building envelope systems — engineered to work together and delivered from a single factory.</p>
    </div>
    <div class="pillars">
      {''.join(pillar_card(c, i + 1, rel, i * 70) for i, c in enumerate(CATEGORIES))}
    </div>
  </div>
</section>

<section class="section section--mist" id="about">
  <div class="container split">
    <div data-reveal>
      <span class="eyebrow" data-i18n="sec.about.eyebrow">Who we are</span>
      <h2 data-i18n="sec.about.title">Engineering materials for better buildings</h2>
      <p class="lead">{SITE['legal']} specialises in building envelope protection, thermal insulation, acoustic and functional material solutions for international markets.</p>
      <p>We integrate manufacturing, engineering, OEM &amp; private-label production and international marketing on one platform. Rather than supplying individual building materials, we build integrated material systems designed to improve compatibility, simplify procurement and deliver better building performance.</p>
      <ul class="check-list" style="margin-bottom:26px">
        <li>Supply partnerships with distributors, importers, contractors and private-label brands worldwide</li>
        <li>Stable standard products, flexible customisation and reliable technical support</li>
        <li>Manufacturing, engineering and export operations under one organisation</li>
      </ul>
      <div class="btn-row">
        <a class="btn" href="about.html" data-i18n="cta.about">More About Us</a>
        <a class="btn btn--ghost" href="about.html#capability">{icon('factory', 18)} <span data-i18n="sec.capability.eyebrow">Capability</span></a>
      </div>
    </div>
    <div class="split__media" data-reveal data-reveal-delay="120">
      <div class="media-frame media-frame--wide">
        <img src="assets/img/application-2.jpg" alt="Insulation installation using SARGARA materials" loading="lazy" width="1000" height="620">
        <div class="media-badge">
          <b>20k+</b>
          <span>tons of mineral wool capacity per month across our certified lines</span>
        </div>
      </div>
      <div class="stat-row" style="grid-template-columns:repeat(2,minmax(0,1fr))">
        <div class="stat"><b>Ningbo</b><span>Head office and export operations, Zhejiang, China</span></div>
        <div class="stat"><b>6</b><span>Continents served by our export team</span></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--dark on-dark" id="capability">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow" data-i18n="sec.capability.eyebrow">Capability</span>
      <h2 data-i18n="sec.capability.title">Manufacturing capability, in detail</h2>
      <p class="lead" data-i18n="sec.capability.lead">Laminating, coating, weaving, slitting, rewinding, printing and packaging — controlled end to end under one roof.</p>
    </div>
    <div class="grid grid--3">
      {''.join(feature_card(t, d, i, idx * 60) for idx, (t, d, i) in enumerate(CAPABILITIES))}
    </div>
  </div>
</section>

<section class="section" id="applications">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow" data-i18n="sec.apps.eyebrow">Applications</span>
      <h2 data-i18n="sec.apps.title">Materials matched to real construction systems</h2>
      <p class="lead" data-i18n="sec.apps.lead">Every product in our range is developed around the way it is installed — not around a catalogue number.</p>
    </div>
    <div class="app-grid">
      {''.join(f'''<a class="app-tile" href="applications.html#{a['slug']}" data-reveal data-reveal-delay="{i * 60}">
        <img src="{a['image']}" alt="{e(a['title'])}" loading="lazy" width="640" height="480">
        <div class="app-tile__body">
          <span class="app-tile__tag">{e(a['tag'])}</span>
          <h3>{e(a['title'])}</h3>
          <p>{e(a['summary'])}</p>
        </div>
      </a>''' for i, a in enumerate(APPLICATIONS[:6]))}
    </div>
    <div class="btn-row" style="margin-top:34px;justify-content:center">
      <a class="btn btn--ghost" href="applications.html">All application areas {icon('arrow', 18)}</a>
    </div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Why SARGARA®</span>
      <h2>What global buyers get when they switch to us</h2>
    </div>
    <div class="grid grid--3">
      {''.join(feature_card(t, d, i, idx * 60) for idx, (t, d, i) in enumerate(WHY_US))}
    </div>
  </div>
</section>

<section class="section section--dark on-dark">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow" data-i18n="sec.markets.eyebrow">Export markets</span>
      <h2 data-i18n="sec.markets.title">Standards that travel</h2>
      <p class="lead" data-i18n="sec.markets.lead">Our teams work daily with regional codes, climates and procurement practices across six continents.</p>
    </div>
    <div class="region-list">
      {''.join(f'<div class="region" data-reveal data-reveal-delay="{i*50}"><h4>{e(n)}</h4><p>{e(d)}</p></div>' for i, (n, d) in enumerate(MARKETS))}
    </div>
  </div>
</section>

<section class="section" id="featured">
  <div class="container">
    <div class="section-head" style="max-width:none;display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap">
      <div>
        <span class="eyebrow">Best sellers</span>
        <h2 style="margin-bottom:0">Products our customers order most</h2>
      </div>
      <a class="btn btn--ghost" href="products.html">All 34 products {icon('arrow', 16)}</a>
    </div>
    <div class="product-grid">
      {''.join(product_card(p, rel, i * 45) for i, p in enumerate(featured))}
    </div>
  </div>
</section>

<section class="section section--mist" id="certifications">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow" data-i18n="sec.cert.eyebrow">Quality &amp; compliance</span>
      <h2 data-i18n="sec.cert.title">Certified, tested and traceable</h2>
      <p class="lead" data-i18n="sec.cert.lead">Quality control covers raw material inspection, in-process monitoring, finished product testing and pre-shipment verification.</p>
    </div>
    <div class="grid grid--4">
      {''.join(f'<div class="feature-card" data-reveal data-reveal-delay="{i*40}" style="padding:24px 22px"><h3 style="font-size:1.02rem;margin-bottom:6px">{e(n)}</h3><p style="font-size:.85rem">{e(d)}</p></div>' for i, (n, d) in enumerate(CERTIFICATIONS))}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow" data-i18n="sec.process.eyebrow">How we work</span>
      <h2 data-i18n="sec.process.title">From enquiry to delivered container</h2>
    </div>
    <div class="process">
      {''.join(f'<div class="process__step" data-reveal data-reveal-delay="{i*60}"><h4>{e(t)}</h4><p>{e(d)}</p></div>' for i, (t, d) in enumerate(PROCESS))}
    </div>
  </div>
</section>

<section class="section section--mist" id="projects">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow" data-i18n="sec.projects.eyebrow">Selected shipments</span>
      <h2 data-i18n="sec.projects.title">Projects delivered</h2>
    </div>
    <div class="project-grid">
      <article class="project-card" data-reveal>
        <div class="project-card__media"><img src="assets/img/application-3.jpg" alt="Roofing underlayment installation" loading="lazy" width="720" height="450"></div>
        <div class="project-card__body">
          <div class="project-card__meta">North America · Roofing</div>
          <h3>Roofing &amp; Ice Dam Protection</h3>
          <p>Self-adhered ice &amp; water shield combined with synthetic underlayment for a cold-climate roof assembly.</p>
        </div>
      </article>
      <article class="project-card" data-reveal data-reveal-delay="70">
        <div class="project-card__media"><img src="assets/img/application-2.jpg" alt="Wall insulation and weather barrier installation" loading="lazy" width="720" height="450"></div>
        <div class="project-card__body">
          <div class="project-card__meta">North America · Walls</div>
          <h3>Wall Weather Barrier Project</h3>
          <p>Breathable house wrap and foil-faced insulation for a durable timber-frame exterior wall.</p>
        </div>
      </article>
      <article class="project-card" data-reveal data-reveal-delay="140">
        <div class="project-card__media"><img src="assets/img/application-1.jpg" alt="Foil-faced HVAC duct insulation" loading="lazy" width="720" height="450"></div>
        <div class="project-card__body">
          <div class="project-card__meta">Middle East · HVAC</div>
          <h3>HVAC Duct Insulation Project</h3>
          <p>Foil-faced duct wrap applied to a commercial HVAC system for thermal and vapour control.</p>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section" id="faq">
  <div class="container split" style="align-items:start">
    <div data-reveal>
      <span class="eyebrow">Buyer FAQ</span>
      <h2>Questions we are asked every week</h2>
      <p class="lead">If your question is not answered here, our export engineers will answer it directly.</p>
      <a class="btn btn--ghost" href="contact.html#inquiry">{icon('mail', 18)} Ask our team</a>
    </div>
    <div data-reveal data-reveal-delay="100">{faq_block(FAQ)}</div>
  </div>
</section>

<section class="section section--mist" id="knowledge">
  <div class="container">
    <div class="section-head" style="max-width:none;display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap">
      <div>
        <span class="eyebrow" data-i18n="sec.news.eyebrow">Technical knowledge</span>
        <h2 style="margin-bottom:0" data-i18n="sec.news.title">Guides for buyers and engineers</h2>
      </div>
      <a class="btn btn--ghost" href="news.html">All articles {icon('arrow', 16)}</a>
    </div>
    <div class="news-grid">{''.join(news_card(a, rel, i * 60) for i, a in enumerate(latest))}</div>
  </div>
</section>

<section class="section" id="inquiry">
  <div class="container split" style="align-items:start">
    <div data-reveal>
      <span class="eyebrow" data-i18n="band.title">Let's build your next project together</span>
      <h2>Send us your specification</h2>
      <p class="lead">Tell us the structure, width, basis weight, target market and certification you need. We will come back with a technical proposal, a sample plan and a quotation on FOB, CIF or DDP terms.</p>
      <ul class="check-list" style="margin-bottom:26px">
        <li>Reply within one working day</li>
        <li>Samples available for evaluation</li>
        <li>OEM, private label and custom structures supported</li>
        <li>Technical data sheets and certificates supplied with the quotation</li>
      </ul>
      <div class="contact-list">
        <div class="contact-item">
          <div class="contact-item__icon">{icon('whatsapp', 20)}</div>
          <div><h4>WhatsApp</h4><a href="https://wa.me/{SITE['whatsapp_link']}" rel="noopener">{SITE['whatsapp']}</a></div>
        </div>
        <div class="contact-item">
          <div class="contact-item__icon">{icon('mail', 20)}</div>
          <div><h4>Email</h4><a href="mailto:{SITE['email']}">{SITE['email']}</a></div>
        </div>
      </div>
    </div>
    <div data-reveal data-reveal-delay="120">{inquiry_form(rel)}</div>
  </div>
</section>
"""
    return (
        head(
            "SARGARA® | Foil Lamination, Roofing & Walling, Insulation & Acoustic, Fiberglass Manufacturer",
            "SARGARA® is a manufacturer of aluminum foil lamination, roofing & walling underlayments, CE/FM certified rock wool, glass wool, acoustic ceiling and fiberglass materials. OEM and private label supply to 80+ countries.",
            rel,
            SITE["domain"] + "/",
        )
        + header("home", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + cta_band(rel)
        + footer(rel)
    )


def build_about() -> str:
    rel = ""
    body = f"""
{page_hero(
    "Make Buildings Better, Together",
    "SARGARA® supplies building envelope, thermal insulation, acoustic and fiberglass materials worldwide, combining manufacturing, engineering and OEM production on one platform.",
    [("Home", "index.html"), ("About Us", "")],
    rel,
)}

<section class="section">
  <div class="container split">
    <div data-reveal>
      <span class="eyebrow">Our story</span>
      <h2>A single source for the whole building envelope</h2>
      <p class="lead">SARGARA® is headquartered in Ningbo, Zhejiang, and works with qualified production partners to supply foil lamination, roofing &amp; walling, insulation &amp; acoustic and fiberglass materials under one commercial platform.</p>
      <p>Rather than selling one product at a time, we build a range that is designed to work together: reflective facings and vapour retarders, house wrap and roofing underlayments, mineral wool insulation, and acoustic and fiberglass materials. Customers can specify and purchase an entire assembly from a single point of contact.</p>
      <p>We support distributors, importers, contractors, insulation manufacturers and private-label brands across North America, Europe, Australia, the Middle East, South America and Asia-Pacific — with OEM production, technical documentation and export logistics handled in house.</p>
      <div class="stat-row" style="grid-template-columns:repeat(2,minmax(0,1fr))">
        <div class="stat"><b>Ningbo</b><span>Head office, Zhejiang, China</span></div>
        <div class="stat"><b>20k t</b><span>Mineral wool capacity per month</span></div>
        <div class="stat"><b>80+</b><span>Export markets</span></div>
        <div class="stat"><b>4</b><span>Manufacturing platforms</span></div>
      </div>
    </div>
    <div class="split__media" data-reveal data-reveal-delay="120">
      <div class="media-frame"><img src="assets/img/application-3.jpg" alt="Roofing underlayment installation" loading="lazy" width="900" height="675" style="object-position:center 50%"></div>
      <div class="media-frame" style="margin-top:20px"><img src="assets/img/application-2.jpg" alt="Wall insulation installation with SARGARA facing materials" loading="lazy" width="900" height="675" style="object-position:center 50%"></div>
    </div>
  </div>
</section>

<section class="section section--dark on-dark" id="capability">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Capability</span>
      <h2>What our factory can actually do</h2>
      <p class="lead">Our production capabilities include laminating, coating, weaving, slitting, rewinding, printing and packaging. Products can be customised by roll width, length, basis weight, colour, surface texture, logo, fire performance, UV resistance and packaging.</p>
    </div>
    <div class="grid grid--3">
      {''.join(feature_card(t, d, i, idx * 60) for idx, (t, d, i) in enumerate(CAPABILITIES))}
    </div>
  </div>
</section>

<section class="section" id="oem">
  <div class="container split split--reverse">
    <div class="split__media" data-reveal>
      <div class="media-frame"><img src="assets/img/team-engineers.jpg" alt="Private-label product development and specification review" loading="lazy" width="900" height="675"></div>
    </div>
    <div data-reveal data-reveal-delay="100">
      <span class="eyebrow">OEM &amp; Private label</span>
      <h2>Your brand, our lines</h2>
      <p class="lead">Private-label production is one of our core capabilities, not a side service. Customers build their own product ranges on our manufacturing platform — from a single trial container to annual programmes.</p>
      <ul class="check-list" style="margin-bottom:24px">
        <li><strong>Structure</strong> — foil type, reinforcement, scrim, film and adhesive systems selected to your performance target</li>
        <li><strong>Format</strong> — custom roll width, roll length, core size, pallet pattern and 9 ft / 10 ft wide formats</li>
        <li><strong>Appearance</strong> — colour, surface texture, embossing and 1–4 colour printing with your logo</li>
        <li><strong>Performance</strong> — flame retardant chemistry, UV resistance and vapour control to your market's codes</li>
        <li><strong>Packaging</strong> — your label, your carton, your pallet specification and shipping marks</li>
      </ul>
      <div class="btn-row">
        <a class="btn btn--primary" href="contact.html#inquiry" data-i18n="cta.quote">Request a Quote</a>
        <a class="btn btn--ghost" href="products.html" data-i18n="cta.viewCatalogue">View Full Catalogue</a>
      </div>
    </div>
  </div>
</section>

<section class="section section--mist" id="quality">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Technology &amp; innovation</span>
      <h2>Innovation driven by real construction applications</h2>
      <p class="lead">Our core R&amp;D focuses on building envelope technologies, including the SARGARA™ flash-spun HDPE product family, advanced synthetic roofing underlayments and reflective vapour barrier systems. New developments are validated against regional building standards and long-term customer feedback.</p>
    </div>
    <div class="grid grid--3">
      <article class="project-card" data-reveal>
        <div class="project-card__media"><img src="assets/img/application-2.jpg" alt="Breathable membrane on an exterior wall assembly" loading="lazy" width="720" height="450"></div>
        <div class="project-card__body">
          <div class="project-card__meta">SARGARA™ Platform</div>
          <h3>B1060 &amp; B2066 HDPE Membranes</h3>
          <p>Flash-spun HDPE membranes engineered for market-leading vapour permeability, with the B2066 achieving EN 13501-1 B-s1,d0.</p>
        </div>
      </article>
      <article class="project-card" data-reveal data-reveal-delay="70">
        <div class="project-card__media"><img src="assets/img/application-1.jpg" alt="Foil facing on HVAC ductwork" loading="lazy" width="720" height="450"></div>
        <div class="project-card__body">
          <div class="project-card__meta">R&amp;D</div>
          <h3>Foil facing development</h3>
          <p>Reflective foil facings and vapour control membranes developed for modern HVAC and envelope assemblies.</p>
        </div>
      </article>
      <article class="project-card" data-reveal data-reveal-delay="140">
        <div class="project-card__media"><img src="assets/img/application-3.jpg" alt="Synthetic roofing underlayment installation" loading="lazy" width="720" height="450"></div>
        <div class="project-card__body">
          <div class="project-card__meta">Roofing</div>
          <h3>Synthetic underlayment systems</h3>
          <p>Anti-slip, high-tear membranes developed with professional roofers in North America and Europe.</p>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section section--dark on-dark" id="certifications">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Quality management</span>
      <h2>Quality &amp; international certifications</h2>
      <p class="lead">Quality control covers raw material inspection, in-process monitoring, finished product testing and pre-shipment verification. Our management systems are certified to ISO 9001, ISO 14001 and ISO 45001. Selected products are tested or certified according to relevant international standards and market requirements.</p>
    </div>
    <div class="cert-grid">
      {''.join(f'<div class="cert" data-reveal data-reveal-delay="{i*50}"><b>{e(n)}</b><span>{e(d)}</span></div>' for i, (n, d) in enumerate(CERTIFICATIONS))}
    </div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div data-reveal>
      <span class="eyebrow">Sustainability</span>
      <h2>Materials that reduce energy demand for decades</h2>
      <p class="lead">We believe premium building materials create safer, more comfortable and more energy-efficient buildings. Through responsible manufacturing and continuous material innovation, we support sustainable construction and long-term partnerships worldwide.</p>
      <ul class="check-list">
        <li>Recycled glass feedstock in our glass wool production</li>
        <li>Long service life and recyclable inorganic mineral wool</li>
        <li>ISO 14001 environmental management across operations</li>
        <li>Reflective and insulating systems that cut operational energy use</li>
      </ul>
    </div>
    <div class="split__media" data-reveal data-reveal-delay="100">
      <div class="media-frame media-frame--wide"><img src="assets/img/application-3.jpg" alt="Sustainable construction with SARGARA materials" loading="lazy" width="1000" height="620"></div>
    </div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Our mission</span>
      <h2>To Make Buildings Better, Together.</h2>
      <p class="lead">We combine engineering expertise, reliable manufacturing and a long-term partnership mindset to help customers build safer, longer-lasting and more energy-efficient buildings.</p>
    </div>
    <div class="grid grid--3" style="max-width:960px;margin-inline:auto">
      <div class="feature-card" data-reveal><div class="feature-card__icon">{icon('globe', 24)}</div><h3>Global market coverage</h3><p>Regional regulations, climate conditions, procurement practices and technical standards understood by our team.</p></div>
      <div class="feature-card" data-reveal data-reveal-delay="70"><div class="feature-card__icon">{icon('factory', 24)}</div><h3>Reliable manufacturing</h3><p>Four material platforms with in-house control from raw material to pre-shipment inspection.</p></div>
      <div class="feature-card" data-reveal data-reveal-delay="140"><div class="feature-card__icon">{icon('layers', 24)}</div><h3>System thinking</h3><p>Materials engineered to work together, so the whole assembly performs — not just one layer.</p></div>
    </div>
  </div>
</section>

<section class="section" id="team">
  <div class="container split split--reverse">
    <div class="split__media" data-reveal>
      <div class="media-frame"><img src="assets/img/team-engineers.jpg" alt="SARGARA export and engineering team" loading="lazy" width="900" height="675"></div>
      <div class="media-frame" style="margin-top:20px"><img src="assets/img/team-planning.jpg" alt="Technical discussion on a construction site" loading="lazy" width="900" height="675"></div>
    </div>
    <div data-reveal data-reveal-delay="100">
      <span class="eyebrow">Our team</span>
      <h2>Talk to people who know the material</h2>
      <p class="lead">Our export team is not a call centre. Enquiries are handled by people who understand structures, standards and production constraints, and who can escalate a technical question to the factory the same day.</p>
      <div class="contact-list">
        <div class="contact-item">
          <div class="contact-item__icon">{icon('globe', 20)}</div>
          <div><h4>Mr. Du — Global Business Director</h4><p>International sales strategy and key account programmes.</p></div>
        </div>
        <div class="contact-item">
          <div class="contact-item__icon">{icon('mail', 20)}</div>
          <div><h4>Export department</h4><p><a href="mailto:{SITE['email']}">{SITE['email']}</a> · WhatsApp <a href="https://wa.me/{SITE['whatsapp_link']}" rel="noopener">{SITE['whatsapp']}</a></p></div>
        </div>
        <div class="contact-item">
          <div class="contact-item__icon">{icon('clock', 20)}</div>
          <div><h4>Response time</h4><p>Within one working day. Urgent enquiries are monitored 24 hours on WhatsApp.</p></div>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return (
        head(
            "About SARGARA® | Building Materials Supplier from Ningbo, China",
            "SARGARA® supplies foil lamination, building envelope, insulation and fiberglass materials to 80+ export markets. Headquartered in Ningbo, Zhejiang, with OEM and private-label production support.",
            rel,
            SITE["domain"] + "/about.html",
        )
        + header("about", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + cta_band(rel)
        + footer(rel)
    )


def build_products() -> str:
    rel = ""
    chips = [("all", "All products", len(PRODUCTS))]
    for cat in CATEGORIES:
        chips.append(
            (cat["id"], cat["short"], sum(1 for p in PRODUCTS if p["category"] == cat["id"]))
        )
    filters = "".join(
        f'<button class="filter{" is-active" if key == "all" else ""}" type="button" '
        f'data-filter="{key}">{e(label)} <span style="opacity:.55">{count}</span></button>'
        for key, label, count in chips
    )

    body = f"""
{page_hero(
    "Product Catalogue",
    "34 standard product families across four manufacturing platforms — foil lamination, roofing &amp; walling, insulation &amp; acoustic and fiberglass. Every item can be customised for width, length, basis weight, colour, print and fire performance.",
    [("Home", "index.html"), ("Products", "")],
    rel,
    "assets/img/application-1.jpg",
)}

<section class="section">
  <div class="container">
    <div class="catalog-toolbar">
      <div class="filters">{filters}</div>
      <div class="catalog-search">
        {icon('search', 18)}
        <input type="search" placeholder="Search products, structures, applications…" data-catalog-search aria-label="Search products">
      </div>
    </div>
    <p class="catalog-count" style="margin-bottom:22px">Showing <strong data-catalog-count>34</strong> products</p>
    <div class="product-grid" data-catalog>
      {''.join(product_card(p, rel, (i % 8) * 40) for i, p in enumerate(PRODUCTS))}
      <div class="catalog-empty" hidden>No products match that search. Try a different term or <a href="contact.html#inquiry">ask our team</a>.</div>
    </div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Need something specific?</span>
      <h2>Custom structures are our normal business</h2>
      <p class="lead">Most of what we ship is not a catalogue item. Tell us the performance you need and we will engineer the construction, produce samples and quote it.</p>
    </div>
    <div class="grid grid--3">
      {feature_card("Drawings &amp; specifications", "Send a drawing, a competitor sample or a written specification. We reverse-engineer the structure and confirm the parameters with you.", "sliders", 0)}
      {feature_card("Samples before commitment", "We produce evaluation samples so your team can test adhesion, tear strength, appearance and line compatibility.", "flask", 70)}
      {feature_card("Private label from one pallet", "Your brand, label, colour and packaging — starting from a trial order and scaling to annual programmes.", "tag", 140)}
    </div>
  </div>
</section>
"""
    return (
        head(
            "Product Catalogue | Foil Lamination, Roofing, Insulation & Fiberglass — SARGARA®",
            "Browse 34 product families: FSK, WMP, Aluglass, heat-sealing foil, house wrap, breathable membrane, ice & water shield, rock wool, glass wool, acoustic panels and fiberglass mat.",
            rel,
            SITE["domain"] + "/products.html",
        )
        + header("products", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + cta_band(rel)
        + footer(rel)
    )


def build_applications() -> str:
    rel = ""
    blocks = []
    for i, a in enumerate(APPLICATIONS):
        rel_products = "".join(
            product_card(p, rel) for p in PRODUCTS if p["slug"] in a["products"]
        )
        reverse = ' split--reverse' if i % 2 else ""
        blocks.append(
            f"""<section class="section{' section--mist' if i % 2 else ''}" id="{a['slug']}">
  <div class="container">
    <div class="split{reverse}">
      <div class="split__media" data-reveal>
        <div class="media-frame media-frame--wide"><img src="{a['image']}" alt="{e(a['title'])}" loading="lazy" width="1000" height="620"></div>
      </div>
      <div data-reveal data-reveal-delay="100">
        <span class="eyebrow">{e(a['tag'])}</span>
        <h2>{e(a['title'])}</h2>
        <p class="lead">{e(a['summary'])}</p>
        <p>{e(a['body'])}</p>
        <ul class="check-list" style="margin-bottom:24px">
          <li>Material selection matched to the installed assembly</li>
          <li>Technical data sheets and certificates supplied with the quotation</li>
          <li>OEM formats, widths and facings available for your market</li>
        </ul>
        <a class="btn btn--ghost" href="contact.html#inquiry">Discuss this application {icon('arrow', 16)}</a>
      </div>
    </div>
    <div class="product-grid" style="margin-top:34px">{rel_products}</div>
  </div>
</section>"""
        )

    body = (
        page_hero(
            "Applications",
            "Building envelope protection, thermal insulation and acoustic performance — engineered for the way your project is actually built and installed.",
            [("Home", "index.html"), ("Applications", "")],
            rel,
            "assets/img/application-1.jpg",
        )
        + "".join(blocks)
    )
    return (
        head(
            "Applications | Metal Building, HVAC, Roofing, Walls, Panels & Acoustic — SARGARA®",
            "See how SARGARA foil facings, membranes, mineral wool and acoustic materials are applied in metal building insulation, HVAC ductwork, roofing, wall envelopes, PUR/PIR panels and industrial insulation.",
            rel,
            SITE["domain"] + "/applications.html",
        )
        + header("applications", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + cta_band(rel)
        + footer(rel)
    )


def build_news() -> str:
    rel = ""
    topics = sorted({a["topic"] for a in ARTICLES})
    body = f"""
{page_hero(
    "Technical Knowledge",
    "Practical material selection guidance written by our engineering team — structure comparisons, sourcing advice and standards explained without the marketing language.",
    [("Home", "index.html"), ("Knowledge", "")],
    rel,
    "assets/img/team-planning.jpg",
)}

<section class="section">
  <div class="container">
    <div class="catalog-toolbar">
      <div class="filters">
        <button class="filter is-active" type="button">{len(ARTICLES)} articles</button>
        {''.join(f'<span class="filter" style="cursor:default">{e(t)}</span>' for t in topics)}
      </div>
    </div>
    <div class="news-grid">
      {''.join(news_card(a, rel, (i % 3) * 60) for i, a in enumerate(ARTICLES))}
    </div>
  </div>
</section>

<section class="section section--mist">
  <div class="container split">
    <div data-reveal>
      <span class="eyebrow">Talk to an engineer</span>
      <h2>Still deciding which structure is right?</h2>
      <p class="lead">Tell us the application, the climate and the standard you are working to. We will recommend a construction and send a sample.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="contact.html#inquiry" data-i18n="cta.quote">Request a Quote</a>
        <a class="btn btn--ghost" href="products.html" data-i18n="cta.viewCatalogue">View Full Catalogue</a>
      </div>
    </div>
    <div class="split__media" data-reveal data-reveal-delay="100">
      <div class="media-frame media-frame--wide"><img src="assets/img/team-engineers.jpg" alt="SARGARA engineering team" loading="lazy" width="1000" height="620"></div>
    </div>
  </div>
</section>
"""
    return (
        head(
            "Technical Knowledge | Insulation Facing, Membranes & Mineral Wool Guides — SARGARA®",
            "Buyer and engineer guides on FSK, FSV, WMP facings, aluminum foil composites, house wrap, WRB, vapour barriers, roofing underlayment and mineral wool insulation.",
            rel,
            SITE["domain"] + "/news.html",
        )
        + header("news", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + cta_band(rel)
        + footer(rel)
    )


def build_contact() -> str:
    rel = ""
    body = f"""
{page_hero(
    "Contact SARGARA®",
    "Our export team replies within one working day. Send a specification, request a sample or ask for a quotation on FOB, CIF or DDP terms.",
    [("Home", "index.html"), ("Contact", "")],
    rel,
)}

<section class="section" id="inquiry">
  <div class="container split" style="align-items:start">
    <div data-reveal>
      <span class="eyebrow">Get in touch</span>
      <h2>Talk to our export team</h2>
      <p class="lead">Whether you need a standard product, a private-label range or a long-term manufacturing partner, we are ready to support your growth.</p>
      <div class="contact-list" style="margin-bottom:28px">
        <div class="contact-item">
          <div class="contact-item__icon">{icon('pin', 20)}</div>
          <div><h4>Head office</h4><p>{SITE['address']}</p></div>
        </div>
        <div class="contact-item">
          <div class="contact-item__icon">{icon('mail', 20)}</div>
          <div><h4>Email</h4><p><a href="mailto:{SITE['email']}">{SITE['email']}</a></p></div>
        </div>
        <div class="contact-item">
          <div class="contact-item__icon">{icon('whatsapp', 20)}</div>
          <div><h4>WhatsApp / Phone</h4><p><a href="https://wa.me/{SITE['whatsapp_link']}" rel="noopener">{SITE['whatsapp']}</a></p></div>
        </div>
        <div class="contact-item">
          <div class="contact-item__icon">{icon('clock', 20)}</div>
          <div><h4>Business hours</h4><p>{SITE['hours']}</p></div>
        </div>
      </div>
      <div class="media-frame media-frame--wide"><img src="assets/img/team-planning.jpg" alt="SARGARA export team working on a project specification" loading="lazy" width="1000" height="620" style="object-position:center 42%"></div>
      <p style="font-size:.82rem;color:var(--ink-400);margin-top:12px">{SITE['address']} — visitors are welcome by appointment.</p>
    </div>
    <div data-reveal data-reveal-delay="120">{inquiry_form(rel, heading="Send us your enquiry", sub="The more detail you give us about structure, width, quantity and target market, the more precise our reply will be.")}</div>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Before you ask</span>
      <h2>Frequently asked questions</h2>
    </div>
    <div style="max-width:860px;margin-inline:auto">{faq_block(FAQ)}</div>
  </div>
</section>

<section class="section" id="privacy">
  <div class="container split" style="align-items:start">
    <div>
      <h2 style="font-size:1.5rem">Privacy policy</h2>
      <p style="font-size:.9rem;color:var(--ink-500)">Information submitted through the forms on this website — name, company, contact details and requirement details — is used solely to prepare and respond to your enquiry. It is never sold or shared with third parties, and it is retained only for as long as needed to support the commercial relationship. You may request deletion at any time by writing to <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>
    </div>
    <div id="terms">
      <h2 style="font-size:1.5rem">Terms of use</h2>
      <p style="font-size:.9rem;color:var(--ink-500)">Product descriptions, typical values and images on this website are provided for general information. Final specifications, tolerances and performance data are confirmed in the technical data sheet and the sales contract for each order. Trademarks and brand names referenced belong to their respective owners.</p>
    </div>
  </div>
</section>
"""
    return (
        head(
            "Contact SARGARA® | Building Materials Supplier, Ningbo China",
            f"Contact SARGARA® for quotations, samples and technical support. Head office: {SITE['address']}. Email {SITE['email']} or WhatsApp {SITE['whatsapp']}.",
            rel,
            SITE["domain"] + "/contact.html",
        )
        + header("contact", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + footer(rel)
    )


def build_product_page(prod: dict) -> str:
    rel = "../"
    images = asset_variants(prod["slug"])
    thumbs = "".join(
        f'<button class="gallery__thumb{" is-active" if i == 0 else ""}" type="button" data-src="{rel}{src}" aria-label="View image {i+1}">'
        f'<img src="{rel}{src}" alt="" loading="lazy"></button>'
        for i, src in enumerate(images)
    )
    features = "".join(f"<li>{e(f)}</li>" for f in prod["features"])
    specs = "".join(
        f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in prod["specs"]
    )
    apps = "".join(f"<li>{e(a)}</li>" for a in prod["applications"])
    badges = "".join(
        f'<span class="badge{"" if i == 0 else ""}">{icon("check", 14)} {e(b)}</span>'
        for i, b in enumerate(prod["badges"])
    )

    related = [p for p in PRODUCTS if p["category"] == prod["category"] and p["slug"] != prod["slug"]][:4]
    related_html = "".join(product_card(p, rel) for p in related)

    cat = next(c for c in CATEGORIES if c["id"] == prod["category"])

    body = page_hero(
        e(prod["name"]),
        e(prod["summary"]),
        [("Home", "index.html"), ("Products", "products.html"), (prod["name"], "")],
        rel,
        "assets/img/application-1.jpg",
        extra=f'<div class="badge-row" style="margin-top:24px">{badges}</div>',
    )

    body += f"""
<section class="section">
  <div class="container detail-layout">
    <div data-reveal>
      <div class="gallery" data-gallery>
        <div class="gallery__main"><img src="{rel}{images[0]}" alt="{e(prod['name'])}" width="900" height="675"></div>
        <div class="gallery__thumbs">{thumbs}</div>
      </div>

      <div class="divider"></div>

      <h2 style="font-size:1.6rem">Product overview</h2>
      <p class="lead">{e(prod['summary'])}</p>

      <h3 style="margin-top:1.8em">Key characteristics</h3>
      <ul class="check-list">{features}</ul>

      <h3 style="margin-top:1.8em">Typical specification</h3>
      <table class="spec-table"><tbody>{specs}</tbody></table>
      <p style="font-size:.82rem;color:var(--ink-400);margin-top:12px">Typical values shown for reference and material selection. Final parameters are confirmed in the technical data sheet and the order confirmation.</p>

      <h3 style="margin-top:1.8em">Applications</h3>
      <ul class="check-list">{apps}</ul>

      <h3 style="margin-top:1.8em">Customisation &amp; supply</h3>
      <div class="grid grid--2" style="margin-top:14px">
        <div class="feature-card" style="padding:22px"><h4 style="margin-bottom:8px">Custom manufacturing</h4><p style="font-size:.88rem">Roll width, length, basis weight, colour, surface texture, printing, fire performance, UV resistance and packaging can all be specified.</p></div>
        <div class="feature-card" style="padding:22px"><h4 style="margin-bottom:8px">Trade terms</h4><p style="font-size:.88rem">FOB, CIF and DDP. Door-to-door delivery is available for the USA and Canada, reducing landed sourcing cost.</p></div>
      </div>
    </div>

    <aside>
      <div class="quote-card">
        <div class="quote-card__head">
          <h3>Request a quotation</h3>
          <p>Reply within one working day · samples available</p>
        </div>
        <div class="quote-card__body">
          <ul class="quote-list">
            <li>Technical data sheet included</li>
            <li>Custom widths and structures</li>
            <li>OEM &amp; private label supported</li>
            <li>FOB · CIF · DDP terms</li>
          </ul>
          <form data-validate novalidate>
            <div class="form-alert" data-form-alert>{icon('check', 18)} <span data-i18n="form.success">Thank you — your enquiry has been received. Our export team will contact you shortly.</span></div>
            <div class="form-grid">
              <div class="field"><label><span data-i18n="form.name">Full name</span> <span class="req">*</span></label><input type="text" name="name" required><span class="error">Please enter your name.</span></div>
              <div class="field"><label><span data-i18n="form.email">Business email</span> <span class="req">*</span></label><input type="email" name="email" required><span class="error">Please enter a valid email address.</span></div>
              <div class="field"><label data-i18n="form.country">Country</label><input type="text" name="country"><span class="error"></span></div>
              <div class="field"><label data-i18n="form.quantity">Estimated quantity</label><input type="text" name="quantity" placeholder="e.g. 1 × 40HQ"><span class="error"></span></div>
              <div class="field"><label><span data-i18n="form.message">Your requirement</span> <span class="req">*</span></label><textarea name="message" required data-i18n-placeholder="form.messagePlaceholder" style="min-height:96px"></textarea><span class="error">Please tell us what you need.</span></div>
            </div>
            <input type="hidden" name="product" value="{e(prod['name'])}">
            <button class="btn btn--primary btn--block" type="submit" style="margin-top:16px" data-i18n="form.submit">Send Enquiry</button>
            <p class="form-note" data-i18n="form.note">We reply within one working day. Your information stays confidential and is never shared.</p>
          </form>
          <div class="divider" style="margin:22px 0"></div>
          <p style="font-size:.85rem;margin-bottom:8px"><strong>Prefer to talk?</strong></p>
          <a class="btn btn--ghost btn--block" href="https://wa.me/{SITE['whatsapp_link']}" rel="noopener">{icon('whatsapp', 18)} {SITE['whatsapp']}</a>
          <a class="btn btn--ghost btn--block" style="margin-top:10px" href="mailto:{SITE['email']}">{icon('mail', 18)} {SITE['email']}</a>
        </div>
      </div>
    </aside>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head" style="max-width:none;display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap">
      <div>
        <span class="eyebrow">Related products</span>
        <h2 style="margin-bottom:0">More from {e(cat['name'])}</h2>
      </div>
      <a class="btn btn--ghost" href="{rel}products.html?cat={cat['id']}">All {e(cat['short'])} {icon('arrow', 16)}</a>
    </div>
    <div class="product-grid">{related_html}</div>
  </div>
</section>
"""
    title = f"{prod['name']} | {prod['group']} Manufacturer — SARGARA®"
    return (
        head(title, prod["summary"][:180], rel, f"{SITE['domain']}/{slug_to_url(prod['slug'])}")
        + header("products", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + cta_band(rel)
        + footer(rel)
    )


def build_article_page(article: dict) -> str:
    rel = "../"
    pretty = date.fromisoformat(article["date"]).strftime("%B %d, %Y")

    blocks = article["body"]
    head_line = blocks[0] if blocks else article["title"]
    rest = blocks[1:]

    bullet_re = re.compile(r"^([•✔▪–-]|\*\*[•✔])")
    numbered_re = re.compile(r"^\d+[.)]\s+\S")

    def flush(pending: list[str], parts: list[str]) -> None:
        if pending:
            parts.append(
                "<ul>" + "".join(f"<li>{p}</li>" for p in pending) + "</ul>"
            )
            pending.clear()

    html_parts: list[str] = []
    pending: list[str] = []

    for line in rest:
        s = re.sub(r"^\*\*|\*\*$", "", line.strip()).strip()
        if not s:
            continue

        # inline bullet runs such as "• FSK • FSV • DFC"
        if bullet_re.match(s):
            items = [i.strip(" *") for i in re.split(r"[•✔]\s*", s) if i.strip(" *")]
            pending.extend(items or [s.lstrip("•✔ ").strip()])
            continue

        flush(pending, html_parts)

        plain = s.replace("**", "")
        if numbered_re.match(plain) and len(plain) < 95:
            html_parts.append(f"<h3>{plain}</h3>")
            continue
        if re.match(r"^(Introduction|Conclusion|Summary|Key takeaways)$", plain, re.I):
            html_parts.append(f"<h2>{plain}</h2>")
            continue
        if len(plain) < 90 and len(plain.split()) <= 10 and not plain.endswith(
            (".", ",", ";", ":", ")", "…")
        ):
            html_parts.append(f"<h3>{plain}</h3>")
            continue
        html_parts.append(f"<p>{s}</p>")

    flush(pending, html_parts)

    prose = "\n".join(html_parts)
    related = [a for a in ARTICLES if a["slug"] != article["slug"]][:3]

    body = page_hero(
        e(article["title"]),
        e(article["excerpt"] or article["title"]),
        [("Home", "index.html"), ("Knowledge", "news.html"), (article["topic"], "")],
        rel,
        article["image"],
        extra=f'<div class="page-hero__meta" style="margin-top:18px"><span>{icon("clock", 16)} {pretty}</span><span>{article["minutes"]} min read</span><span>{e(article["topic"])}</span></div>',
    )

    body += f"""
<section class="section">
  <div class="container detail-layout">
    <article class="prose" data-reveal>
      <p class="lead" style="font-size:1.1rem;color:var(--ink-500)">{e(head_line)}</p>
      {prose}
      <div class="divider"></div>
      <div style="display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between">
        <p style="margin:0;font-size:.88rem;color:var(--ink-400)">Written by the SARGARA® technical team · {pretty}</p>
        <a class="btn btn--ghost btn--sm" href="{rel}news.html" data-i18n="nav.news">Knowledge</a>
      </div>
    </article>
    <aside>
      <div class="quote-card">
        <div class="quote-card__head">
          <h3>Ask about this topic</h3>
          <p>Our engineers answer technical questions directly</p>
        </div>
        <div class="quote-card__body">
          <ul class="quote-list">
            <li>Material selection support</li>
            <li>Samples for evaluation</li>
            <li>Data sheets and certificates</li>
          </ul>
          <form data-validate novalidate>
            <div class="form-alert" data-form-alert>{icon('check', 18)} <span data-i18n="form.success">Thank you — your enquiry has been received. Our export team will contact you shortly.</span></div>
            <div class="form-grid">
              <div class="field"><label><span data-i18n="form.name">Full name</span> <span class="req">*</span></label><input type="text" name="name" required><span class="error">Please enter your name.</span></div>
              <div class="field"><label><span data-i18n="form.email">Business email</span> <span class="req">*</span></label><input type="email" name="email" required><span class="error">Please enter a valid email address.</span></div>
              <div class="field"><label><span data-i18n="form.message">Your requirement</span> <span class="req">*</span></label><textarea name="message" required data-i18n-placeholder="form.messagePlaceholder" style="min-height:96px"></textarea><span class="error">Please tell us what you need.</span></div>
            </div>
            <button class="btn btn--primary btn--block" type="submit" style="margin-top:16px" data-i18n="form.submit">Send Enquiry</button>
          </form>
        </div>
      </div>
    </aside>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head"><span class="eyebrow">Keep reading</span><h2>Related technical guides</h2></div>
    <div class="news-grid">{''.join(news_card(a, rel) for a in related)}</div>
  </div>
</section>
"""
    return (
        head(
            f"{article['title']} | SARGARA®",
            (article["excerpt"] or article["title"])[:180],
            rel,
            f"{SITE['domain']}/news/{article['slug']}.html",
        )
        + header("news", rel)
        + '<main id="main">'
        + body
        + "</main>"
        + cta_band(rel)
        + footer(rel)
    )


def build_404() -> str:
    body = f"""
<section class="section" style="padding-top:clamp(80px,10vw,140px)">
  <div class="container text-center">
    <span class="eyebrow" style="justify-content:center">Error 404</span>
    <h1>This page has moved or never existed</h1>
    <p class="lead" style="max-width:620px;margin-inline:auto">The link may be outdated. You can browse the full product catalogue, read our technical guides, or send us your requirement directly.</p>
    <div class="btn-row" style="justify-content:center;margin-top:28px">
      <a class="btn btn--primary" href="products.html" data-i18n="cta.viewCatalogue">View Full Catalogue</a>
      <a class="btn btn--ghost" href="contact.html#inquiry" data-i18n="cta.quote">Request a Quote</a>
    </div>
  </div>
</section>
<section class="section section--mist">
  <div class="container">
    <div class="section-head section-head--center"><span class="eyebrow">Popular products</span><h2>Start from our best sellers</h2></div>
    <div class="product-grid">{''.join(product_card(p) for p in PRODUCTS[:8])}</div>
  </div>
</section>
"""
    return (
        head("Page not found | SARGARA®", "The page you requested could not be found.", "", SITE["domain"] + "/404.html")
        + header("", "")
        + '<main id="main">' + body + "</main>"
        + footer("")
    )


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

PRODUCTS = json.load(open(os.path.join(DATA, "products.json")))
ARTICLES = json.load(open(os.path.join(DATA, "articles.json")))


def write(rel_path: str, content: str) -> None:
    path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def build_sitemap() -> str:
    urls = ["/", "/about.html", "/products.html", "/applications.html", "/news.html", "/contact.html"]
    urls += [f"/{slug_to_url(p['slug'])}" for p in PRODUCTS]
    urls += [f"/news/{a['slug']}.html" for a in ARTICLES]
    today = date.today().isoformat()
    rows = "".join(
        f"  <url><loc>{SITE['domain']}{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq>"
        f"<priority>{'1.0' if u == '/' else '0.7'}</priority></url>\n"
        for u in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n"
    )


def main() -> None:
    generated: set[str] = set()

    def track(rel_path: str, content: str) -> None:
        generated.add(rel_path.replace("\\", "/"))
        write(rel_path, content)

    track("index.html", build_index())
    track("about.html", build_about())
    track("products.html", build_products())
    track("applications.html", build_applications())
    track("news.html", build_news())
    track("contact.html", build_contact())
    track("404.html", build_404())

    for prod in PRODUCTS:
        track(slug_to_url(prod["slug"]), build_product_page(prod))

    for article in ARTICLES:
        track(f"news/{article['slug']}.html", build_article_page(article))

    track("sitemap.xml", build_sitemap())
    track("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE['domain']}/sitemap.xml\n")

    # remove pages from earlier builds that are no longer generated
    for folder in ("products", "news"):
        directory = os.path.join(ROOT, folder)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            rel_path = f"{folder}/{name}"
            if name.endswith(".html") and rel_path not in generated:
                os.remove(os.path.join(directory, name))
                print(f"  removed stale page: {rel_path}")

    count = 7 + len(PRODUCTS) + len(ARTICLES)
    print(f"Built {count} pages.")
    print(f"  {len(PRODUCTS)} product pages, {len(ARTICLES)} article pages, 7 top-level pages.")


if __name__ == "__main__":
    main()
