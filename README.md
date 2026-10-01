# B7 Global website

Bilingual (English / Arabic) static site for b7global.ae.

- `site/`  – the finished website. **This folder is what gets uploaded to hosting.**
  - `index.html` (English) and `ar/index.html` (Arabic) are generated – don't edit them by hand.
- `src/`   – the source the pages are generated from.
  - `content.py`  – all text (English + Arabic) and contact details (`CONFIG` at the top)
  - `template.html`, `style.css`, `script.js` – layout, design, behaviour
  - `build.py`    – regenerates `site/`

## Adding contact details

Open `src/content.py`, fill in the empty values in `CONFIG` (`email`, `whatsapp`, and optionally `form_endpoint`), then:

```bash
cd src && python3 build.py
```

Empty values show a "Coming soon" placeholder on the site.

## Preview locally

```bash
cd site && python3 -m http.server 8765
```

Then open http://localhost:8765/
