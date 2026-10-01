#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the bilingual B7 Global site into ../site  (run: python3 build.py)."""
import datetime
import html
import json
import re
import shutil
from pathlib import Path

from content import CONFIG, T

SRC = Path(__file__).parent
OUT = SRC.parent / "site"
esc = html.escape

ICONS = {
    "link": '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.3 10.9l7.4-3.8M8.3 13.1l7.4 3.8"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2M3 13h18"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "swap": '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
    "layers": '<path d="M12 3l9 4.5-9 4.5-9-4.5L12 3z"/><path d="M3 12l9 4.5 9-4.5"/><path d="M3 16.5L12 21l9-4.5"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="6.5"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1"/>',
    "box": '<path d="M3 7.5L12 3l9 4.5v9L12 21l-9-4.5v-9z"/><path d="M3 7.5l9 4.5 9-4.5M12 12v9"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "chat": '<path d="M4 20l1.3-4A8 8 0 1112 20a8 8 0 01-3.8-1L4 20z"/>',
    "pin": '<path d="M12 21s7-6.2 7-11.5A7 7 0 005 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def digits(s):
    return re.sub(r"\D", "", s)


def contact_value(kind, t):
    """Return inner HTML for a contact value; placeholder when config is empty."""
    soon = f'<span class="placeholder">{esc(t["soon"])}</span>'
    if kind == "phone":
        p = CONFIG["phone"]
        return f'<a href="tel:+{digits(p)}"><bdi dir="ltr">{esc(p)}</bdi></a>' if p else soon
    if kind == "email":
        e = CONFIG["email"]
        return f'<a href="mailto:{esc(e)}"><bdi dir="ltr">{esc(e)}</bdi></a>' if e else soon
    if kind == "whatsapp":
        w = CONFIG["whatsapp"]
        return f'<a href="https://wa.me/{digits(w)}" target="_blank" rel="noopener"><bdi dir="ltr">{esc(w)}</bdi></a>' if w else soon
    raise ValueError(kind)


def build_blocks(t, lang):
    b = {}
    b["trust"] = "".join(
        f'<div class="trust-item">{icon(i)}<span>{esc(txt)}</span></div>' for i, txt in t["trust"]
    )
    b["values"] = "".join(f'<li>{icon("check", "tick")}<span>{esc(v)}</span></li>' for v in t["values"])
    b["info"] = "".join(f'<div><dt>{esc(k)}</dt><dd><bdi>{esc(v)}</bdi></dd></div>' for k, v in t["info"])
    b["services"] = "".join(
        f'<article class="card reveal"><div class="icon-badge">{icon(i)}</div><h3>{esc(ti)}</h3><p>{esc(d)}</p></article>'
        for i, ti, d in t["services"]
    )
    b["licensed"] = "".join(f"<li>{esc(x)}</li>" for x in t["licensed"])
    b["focus"] = "".join(
        f'<article class="focus-card reveal"><div class="icon-badge icon-badge-dark">{icon(i)}</div><h3>{esc(ti)}</h3><p>{esc(d)}</p></article>'
        for i, ti, d in t["focus"]
    )
    b["chips"] = "".join(f"<li>{esc(c)}</li>" for c in t["serve_chips"])
    b["steps"] = "".join(
        f'<li class="step reveal"><span class="step-num">{n}</span><h3>{esc(ti)}</h3><p>{esc(d)}</p></li>'
        for n, (ti, d) in enumerate(t["steps"], 1)
    )
    b["expect"] = "".join(f'<li>{icon("check", "tick")}<span>{esc(x)}</span></li>' for x in t["expect"])
    b["topics"] = "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in t["f_topics"])

    location = CONFIG["location_" + lang]
    rows = [
        ("user", t["c_person"], esc(t["c_person_v"])),
        ("phone", t["c_phone"], contact_value("phone", t)),
        ("mail", t["c_email"], contact_value("email", t)),
        ("chat", t["c_whatsapp"], contact_value("whatsapp", t)),
        ("pin", t["c_location"], esc(location)),
    ]
    b["contact_rows"] = "".join(
        f'<li><span class="c-icon">{icon(i)}</span><span class="c-text"><small>{esc(lab)}</small><strong>{val}</strong></span></li>'
        for i, lab, val in rows
    )
    foot = []
    if CONFIG["phone"]:
        foot.append(contact_value("phone", t))
    foot.append(contact_value("email", t))
    if CONFIG["whatsapp"]:
        foot.append(contact_value("whatsapp", t))
    foot.append(esc(location))
    b["footer_contact"] = "".join(f"<li>{x}</li>" for x in foot)
    return b


def main():
    tpl = (SRC / "template.html").read_text(encoding="utf-8")
    year = datetime.date.today().year
    site = CONFIG["site_url"].rstrip("/")

    fonts = {
        "en": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600&display=swap",
        "ar": "https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600&display=swap",
    }
    urls = {"en": site + "/", "ar": site + "/ar/"}
    paths = {"en": OUT / "index.html", "ar": OUT / "ar" / "index.html"}

    for lang, t in T.items():
        ctx = {k: v for k, v in t.items() if isinstance(v, str)}
        other = t["other_lang_code"]
        ctx.update(
            base="" if lang == "en" else "../",
            home_href="./" if lang == "en" else "./",
            other_href="ar/" if lang == "en" else "../",
            canonical=urls[lang],
            url_en=urls["en"],
            url_ar=urls["ar"],
            site_url=site,
            og_locale="en_AE" if lang == "en" else "ar_AE",
            fonts_url=fonts[lang],
            year=str(year),
            form_endpoint=esc(CONFIG["form_endpoint"]),
            emailjs_service_id=esc(CONFIG["emailjs_service_id"]),
            emailjs_template_id=esc(CONFIG["emailjs_template_id"]),
            emailjs_public_key=esc(CONFIG["emailjs_public_key"]),
            email=esc(CONFIG["email"]),
            phone=esc(CONFIG["phone"]),
            f_notready_final=esc(
                t["f_notready_phone"].format(phone=CONFIG["phone"]) if CONFIG["phone"] else t["f_notready"]
            ),
        )
        ld = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "B7 Global Brokerage Services",
            "alternateName": "B7 Global",
            "url": site + "/",
            "logo": site + "/assets/logo-full.png",
            "description": t["meta_desc"],
            "areaServed": "AE",
        }
        if CONFIG["phone"]:
            ld["telephone"] = CONFIG["phone"]
        if CONFIG["email"]:
            ld["email"] = CONFIG["email"]
        ctx["jsonld"] = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")

        blocks = build_blocks(t, lang)

        def sub(m):
            key = m.group(1)
            if key.startswith("@"):
                return blocks[key[1:]]
            if key.startswith("i:"):
                return ICONS[key[2:]]
            if key not in ctx:
                raise KeyError(f"template placeholder not defined: {key}")
            val = ctx[key]
            # values used inside attributes/text are escaped; pre-escaped keys are listed here
            raw = {"jsonld", "form_endpoint", "email", "phone", "f_notready_final",
                   "emailjs_service_id", "emailjs_template_id", "emailjs_public_key"}
            return val if key in raw else esc(val, quote=True)

        out = re.sub(r"\{\{([^}]+)\}\}", sub, tpl)
        paths[lang].parent.mkdir(parents=True, exist_ok=True)
        paths[lang].write_text(out, encoding="utf-8")

    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for f in ("style.css", "script.js"):
        shutil.copy(SRC / f, assets / f)

    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n", encoding="utf-8")
    sm = "".join(
        f'<url><loc>{urls[l]}</loc>'
        + "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{urls[x]}"/>' for x in ("en", "ar"))
        + "</url>"
        for l in ("en", "ar")
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + sm + "</urlset>\n",
        encoding="utf-8",
    )
    print("Built:", ", ".join(str(p.relative_to(OUT.parent)) for p in paths.values()))


if __name__ == "__main__":
    main()
