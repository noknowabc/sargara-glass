# SARGARA® — Building Materials Website

A professional international-trade website for **SARGARA®** (Ningbo, Zhejiang,
China), built as a static site — no framework and no server required.

Product and technical content was originally sourced from `unitedperfect.com`
and has been rebranded for SARGARA. Branding, contact details and company claims
must be reviewed before publication — see "Notes before going live".

## Brand

| Item | Value |
| --- | --- |
| Brand | SARGARA® |
| Head office | No. 1890 Qingqing Road, Zhenhai District, Ningbo, Zhejiang, China |
| Email | david@china.sargara.com |
| Phone / WhatsApp | +86 188 6868 5020 |
| Domain (canonical) | https://www.sargara.com |

Logo assets: `assets/img/logo.svg` (light backgrounds), `logo-white.svg` (dark
backgrounds), `logo-mark.svg` (square mark / favicon), plus generated
`favicon-32.png` and `apple-touch-icon.png`.

## Quick start

Open `index.html` directly in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://127.0.0.1:8000/
```

Deploy by uploading the whole folder to any static host (Netlify, Vercel, S3,
Nginx, or the client's existing hosting). `sitemap.xml` and `robots.txt` are
generated automatically.

## Deployment

The site is published from the GitHub repository `noknowabc/sargara-website`
(private). The repository root **is** the site root — there is no build step.

| Branch | Contents |
| --- | --- |
| `main` | This static site |
| `legacy-hvac-catalog` | The previous bilingual HVAC/R catalog project, preserved for reference |

```bash
git push origin main      # publish an update
```

GitHub Pages is **not** available for this private repository on the current
plan (the API returns HTTP 422). To get a public URL, either make the repository
public and enable Settings → Pages (source `main`, folder `/`), or connect the
repository to a host such as Netlify, Vercel or Cloudflare Pages.

## What is in the build

| Page | File | Notes |
| --- | --- | --- |
| Home | `index.html` | Hero, four product platforms, capability, applications, export markets, certifications, process, best sellers, projects, FAQ, RFQ form |
| Catalogue | `products.html` | All 34 products, client-side category filter, live search, deep links via `?cat=` |
| Product detail | `products/<slug>.html` | 34 pages: gallery, key characteristics, typical specification table, applications, sticky RFQ card, related products |
| About | `about.html` | Company story, manufacturing capability, OEM & private label, R&D, certifications, sustainability, mission, team |
| Applications | `applications.html` | 9 application areas, alternating layout, matched product sets |
| Knowledge | `news.html` | 14 real technical articles with topic tags |
| Article | `news/<slug>.html` | Full article body, sticky enquiry card, related guides |
| Contact | `contact.html` | Contact channels, full enquiry form, FAQ, privacy and terms |
| Not found | `404.html` | Recovery page with best sellers |

Plus `sitemap.xml`, `robots.txt` and a shared `assets/` folder.

## Structure

```
.
├── index.html · about.html · products.html · applications.html
├── news.html · contact.html · 404.html · sitemap.xml · robots.txt
├── products/                 34 generated product pages
├── news/                     14 generated article pages
├── assets/
│   ├── css/main.css          design system + components
│   ├── js/main.js            navigation, filters, gallery, forms, reveal
│   ├── js/i18n.js            EN / 中文 / ES / FR / RU interface translations
│   └── img/                  147 images (logo, products, news, applications)
├── data/
│   ├── products.json         product catalogue data
│   └── articles.json         article data
└── tools/
    └── build_site.py         static site generator
```

## Editing content

The HTML pages are **generated**. Edit the data, then rebuild:

```bash
python3 tools/build_site.py
```

* **Products** — add or edit an entry in `data/products.json` (slug, name,
  category, summary, features, specs, applications, badges). A matching image at
  `assets/img/products/<slug>.jpg` is picked up automatically; `-1`, `-2`
  variants become additional gallery images.
* **Articles** — edit `data/articles.json`. `body` is a list of text lines;
  lines beginning with `•` or `✔` become list items, short lines become
  subheadings, and `**text**` becomes bold.
* **Site-wide copy** — company details, categories, applications,
  certifications, markets, process steps, FAQ and the "why us" list live at the
  top of `tools/build_site.py`.

The generator also deletes stale pages from earlier builds and rewrites
`sitemap.xml`, so the output always matches the data.

## Legacy assets to review

The rebrand removed every reference to the previous brand from the generated
HTML, but two groups of files still need attention:

* **37 unused images (13 MB)** in `assets/img/` — `company-factory*`,
  `banner-*`, `project-*`, `category-*`, `systems-platform.jpg`,
  `roofing-system.jpg`, `logo.png`, `logo-mark.png`. These are no longer
  referenced and show the previous company's signage, so they can be deleted.
* **Product photography** in `assets/img/products/` still carries a faint
  supplier watermark. Automated removal was tested and rejected because it
  visibly smears the material surfaces; real SARGARA photos are the right fix.

## Features

* **Five-language interface switcher** (EN / 中文 / ES / FR / RU) covering
  navigation, calls to action, section headings and all form labels. The choice
  is remembered in `localStorage`.
* **Product catalogue** with category filters, live search, result counter,
  empty state and `?cat=` deep links.
* **RFQ-led conversion design** — request-a-quote in the header, a sticky quote
  card on every product page, an enquiry form on the home and contact pages, and
  a floating WhatsApp button.
* **Client-side form validation** with inline error messages and a success
  state (wire the `<form>` `action` to a backend or form service to go live).
* **Accessible markup** — skip link, landmarks, labelled controls, keyboard
  focus styles, `prefers-reduced-motion` support.
* **Responsive** from 360 px upward, with a mega menu on desktop and a slide-in
  drawer on mobile.
* **Self-contained images** — everything is stored locally under `assets/img`
  and compressed for the web (142 files, ~40 MB total).

## Notes before going live

1. Replace the placeholder company claims. Founding year, "20+ years" and
   similar history statements were removed during the rebrand because they
   described the previous company. Add SARGARA's own facts back into
   `tools/build_site.py` once confirmed.
2. Replace the remaining product photography. Product images still carry a faint
   watermark from the original supplier, and the unused `company-*`, `banner-*`,
   `project-*` and `category-*` files show the previous company's signage — real
   SARGARA product and factory photos are strongly preferred.
3. Point the enquiry forms at a real endpoint. Replace
   `<form data-validate novalidate>` with your handler (or add an `action`
   attribute) in `tools/build_site.py` and rebuild.
4. Confirm the canonical domain. `SITE["domain"]` in `tools/build_site.py`
   currently points at `https://www.sargara.com`; change it if the live host
   differs so canonical URLs, the sitemap and `robots.txt` stay correct.
5. Replace the placeholder LinkedIn and YouTube URLs, and confirm the WhatsApp
   number, email and address.
6. Specification tables carry typical reference values; confirm the final
   figures against each product's technical data sheet before publication.
