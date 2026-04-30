#!/usr/bin/env python3
"""Generate index.html in every folder of WallPaperS_ColleCtoR.

Features:
- Root index.html lists all drawers with previews.
- Per-folder index.html (paginated if >IMAGES_PER_PAGE).
- Click image -> lightbox; Escape closes.
- Light/dark theme toggle (persisted in localStorage).
- Home button + back button to parent.
- 10 visual themes picked deterministically per folder.
- Includes the user's required boilerplate (filedn.eu links + social menu).
- All paths relative -> works fully offline.
"""
from __future__ import annotations

import hashlib
import html
import os
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SCAN_ROOT = ROOT / "WallPaperS"
IMAGES_PER_PAGE = 60
IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif", ".avif", ".jfif"}

# ---------- Boilerplate (mandated by user) ----------
BOILERPLATE_HEAD = '''<link rel="canonical" href="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/">
<link rel="icon" href="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/Site_Web/favicondepascal.png" type="image/png">
<link rel="icon" href="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/Site_Web/favicondepascal.ico" type="image/x-icon">
<link rel="stylesheet" type="text/css" href="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/Site_Web/style.css">
<script src="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/Site_Web/script.js"></script>
<script src="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/Site_Web/menu.js" defer></script>
<link rel="stylesheet" href="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/Site_Web/basedusite.css">
<script src="https://filedn.eu/llN3kr5vmyEBPIWCwFj3O6h/Site_Web/couleurs.js"></script>'''

BOILERPLATE_BODY = '''<nav class="social-menu">
    <ul>
      <li><a href="https://fr.pinterest.com/pascal509/mes-tableaux-tous-genre/" target="_blank" rel="noopener">Pinterest</a></li>
      <li><a href="https://www.flickr.com/photos/delfossepascal" target="_blank" rel="noopener">Flickr</a></li>
      <li><a href="https://www.tumblr.com/lestoilesdepascal" target="_blank" rel="noopener">Tumblr</a></li>
      <li><a href="https://x.com/PascalDelfossee" target="_blank" rel="noopener">X</a></li>
      <li><a href="https://www.youtube.com/c/DelfossePascal" target="_blank" rel="noopener">YouTube</a></li>
    </ul>
  </nav>
<header></header>'''

# ---------- 10 visual themes ----------
THEMES = [
    {  # 0 Aurora
        "name": "Aurora",
        "bg_dark": "linear-gradient(135deg,#0f2027,#203a43,#2c5364)",
        "bg_light": "linear-gradient(135deg,#a1ffce,#faffd1)",
        "accent": "#7afcff", "accent2": "#ff7eb9",
        "anim": "aurora",
    },
    {  # 1 Neon
        "name": "Neon",
        "bg_dark": "radial-gradient(circle at 20% 20%,#1a0033,#000)",
        "bg_light": "radial-gradient(circle at 20% 20%,#fff5fc,#ffe6f2)",
        "accent": "#ff00d4", "accent2": "#00ffe7",
        "anim": "pulse",
    },
    {  # 2 Sakura
        "name": "Sakura",
        "bg_dark": "linear-gradient(135deg,#3d0c2b,#150016)",
        "bg_light": "linear-gradient(135deg,#ffe4ef,#fff0f5)",
        "accent": "#ff6fa3", "accent2": "#ffd6e0",
        "anim": "drift",
    },
    {  # 3 Ocean
        "name": "Ocean",
        "bg_dark": "linear-gradient(135deg,#001f3f,#003366,#005c99)",
        "bg_light": "linear-gradient(135deg,#cfe9ff,#e6f7ff)",
        "accent": "#00b4d8", "accent2": "#90e0ef",
        "anim": "wave",
    },
    {  # 4 Sunset
        "name": "Sunset",
        "bg_dark": "linear-gradient(135deg,#2b0a3d,#5e0c63,#a32872)",
        "bg_light": "linear-gradient(135deg,#ffd6a5,#ffadad)",
        "accent": "#ff8c42", "accent2": "#ffb347",
        "anim": "shift",
    },
    {  # 5 Forest
        "name": "Forest",
        "bg_dark": "linear-gradient(135deg,#0b3d2e,#13261d)",
        "bg_light": "linear-gradient(135deg,#d4f1c8,#eef9e3)",
        "accent": "#4caf50", "accent2": "#a8d878",
        "anim": "sway",
    },
    {  # 6 Galaxy
        "name": "Galaxy",
        "bg_dark": "radial-gradient(ellipse at top,#1b1535,#04000d)",
        "bg_light": "linear-gradient(135deg,#e9defa,#f4f0ff)",
        "accent": "#9d4edd", "accent2": "#5a189a",
        "anim": "stars",
    },
    {  # 7 Lava
        "name": "Lava",
        "bg_dark": "linear-gradient(135deg,#1a0000,#440000,#8b0000)",
        "bg_light": "linear-gradient(135deg,#ffd1cf,#ffe0c2)",
        "accent": "#ff4500", "accent2": "#ffaa00",
        "anim": "ember",
    },
    {  # 8 Mint
        "name": "Mint",
        "bg_dark": "linear-gradient(135deg,#003b36,#016a4f)",
        "bg_light": "linear-gradient(135deg,#c8f7e2,#e8fff5)",
        "accent": "#2ec4b6", "accent2": "#cbf3f0",
        "anim": "ripple",
    },
    {  # 9 Royal
        "name": "Royal",
        "bg_dark": "linear-gradient(135deg,#1a0033,#2a0050,#3d0066)",
        "bg_light": "linear-gradient(135deg,#fff3d6,#fae3ff)",
        "accent": "#ffd700", "accent2": "#9d4edd",
        "anim": "shine",
    },
]


def pick_theme(key: str) -> dict:
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    return THEMES[h % len(THEMES)]


def rel_to_root(folder: Path) -> str:
    """Relative path string from `folder` back up to ROOT (with trailing /)."""
    depth = len(folder.relative_to(ROOT).parts)
    if depth == 0:
        return "./"
    return "../" * depth


def url_q(p: str) -> str:
    return quote(p.replace("\\", "/"), safe="/")


# ---------- CSS ----------
def build_css(theme: dict) -> str:
    return f"""
:root {{
  --bg: {theme['bg_dark']};
  --fg: #f5f5f5;
  --card-bg: rgba(255,255,255,0.05);
  --card-border: rgba(255,255,255,0.12);
  --accent: {theme['accent']};
  --accent2: {theme['accent2']};
  --shadow: 0 10px 30px rgba(0,0,0,.5);
}}
:root[data-theme="light"] {{
  --bg: {theme['bg_light']};
  --fg: #1a1a1a;
  --card-bg: rgba(255,255,255,0.55);
  --card-border: rgba(0,0,0,0.08);
  --shadow: 0 10px 30px rgba(0,0,0,.15);
}}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; min-height:100vh; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--fg);
  background: var(--bg);
  background-size: 400% 400%;
  animation: bgShift 22s ease infinite;
  overflow-x: hidden;
}}
@keyframes bgShift {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}
.topbar {{
  position: sticky; top:0; z-index:50;
  display: flex; gap:.6rem; padding:.7rem 1rem;
  backdrop-filter: blur(10px);
  background: rgba(0,0,0,.25);
  border-bottom: 1px solid var(--card-border);
}}
:root[data-theme="light"] .topbar {{ background: rgba(255,255,255,.45); }}
.btn {{
  border: 1px solid var(--card-border);
  background: var(--card-bg);
  color: var(--fg);
  padding: .5rem .9rem;
  border-radius: 999px;
  cursor: pointer;
  font-size: .9rem;
  text-decoration: none;
  transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
}}
.btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,.3); background: var(--accent); color:#000; }}
.title {{
  font-size: clamp(1.6rem, 4vw, 3rem);
  text-align: center;
  margin: 1.5rem 1rem .3rem;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
  letter-spacing: .03em;
}}
.subtitle {{ text-align:center; opacity:.8; margin: 0 1rem 1.2rem; }}
.gallery {{
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  padding: 1rem;
  max-width: 1600px;
  margin: 0 auto;
}}
.gallery a {{
  display:block; position:relative;
  border-radius: 14px; overflow: hidden;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  box-shadow: var(--shadow);
  cursor: zoom-in;
  transition: transform .35s cubic-bezier(.2,.7,.2,1.2), box-shadow .3s;
  animation: tileIn .6s ease both;
}}
.gallery a:nth-child(odd) {{ animation-delay: .05s; }}
.gallery a:nth-child(even) {{ animation-delay: .15s; }}
.gallery a:hover {{
  transform: translateY(-6px) scale(1.03);
  box-shadow: 0 18px 50px rgba(0,0,0,.55), 0 0 0 2px var(--accent);
}}
.gallery img {{
  width: 100%; height: 220px; object-fit: cover; display:block;
  transition: transform .6s ease;
}}
.gallery a:hover img {{ transform: scale(1.08); }}
@keyframes tileIn {{
  from {{ opacity:0; transform: translateY(20px) scale(.98); }}
  to   {{ opacity:1; transform: none; }}
}}

.folders {{
  display: grid; gap: 18px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  padding: 1rem; max-width: 1600px; margin: 0 auto;
}}
.folder-card {{
  display:flex; flex-direction: column; justify-content: space-between;
  padding: 1rem 1.2rem; min-height: 140px;
  border-radius: 18px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  box-shadow: var(--shadow);
  text-decoration: none; color: var(--fg);
  position: relative; overflow: hidden;
  transition: transform .3s, box-shadow .3s;
  animation: cardIn .7s ease both;
}}
.folder-card::before {{
  content:""; position:absolute; inset:-2px;
  background: linear-gradient(120deg, var(--accent), transparent 40%, var(--accent2));
  opacity:.0; transition: opacity .4s; z-index:0;
}}
.folder-card:hover::before {{ opacity:.25; }}
.folder-card:hover {{ transform: translateY(-5px) rotate(-.4deg); box-shadow: 0 16px 40px rgba(0,0,0,.45); }}
.folder-card > * {{ position: relative; z-index:1; }}
.folder-name {{ font-weight: 700; font-size: 1.15rem; }}
.folder-meta {{ opacity:.75; font-size:.85rem; margin-top: .4rem; }}
@keyframes cardIn {{
  from {{ opacity:0; transform: translateY(28px); }}
  to   {{ opacity:1; transform: none; }}
}}

.pager {{
  display:flex; justify-content:center; gap:.4rem; flex-wrap:wrap;
  padding: 1.5rem 1rem 3rem;
}}
.pager a, .pager span {{
  padding: .45rem .8rem; border-radius: 8px;
  border: 1px solid var(--card-border);
  background: var(--card-bg); color: var(--fg);
  text-decoration: none; font-size: .9rem;
}}
.pager .current {{ background: var(--accent); color:#000; border-color: var(--accent); }}

/* lightbox */
.lightbox {{
  position: fixed; inset:0; background: rgba(0,0,0,.92);
  display:none; align-items:center; justify-content:center; z-index:1000;
  padding:2rem; cursor: zoom-out;
  animation: fadeIn .25s ease;
}}
.lightbox.active {{ display:flex; }}
.lightbox img {{
  max-width: 96vw; max-height: 92vh; object-fit: contain;
  border-radius: 8px; box-shadow: 0 0 60px rgba(0,0,0,.8);
  animation: zoomIn .3s ease;
}}
.lightbox .hint {{ position:absolute; bottom:1rem; left:50%; transform:translateX(-50%);
  color:#fff; opacity:.7; font-size:.85rem; }}
@keyframes fadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
@keyframes zoomIn {{ from {{ opacity:0; transform: scale(.9); }} to {{ opacity:1; transform:none; }} }}

/* Theme-specific decorative animations */
.deco {{ position: fixed; inset:0; pointer-events:none; z-index:0; }}
.deco span {{ position:absolute; border-radius:50%; filter: blur(40px); opacity:.45; }}
"""


def deco_html(theme: dict) -> str:
    """Decorative animated background blobs / particles per theme."""
    a = theme["accent"]; b = theme["accent2"]; anim = theme["anim"]
    return f"""<div class="deco" aria-hidden="true">
<span style="width:380px;height:380px;background:{a};top:-100px;left:-80px;animation:{anim}A 18s ease-in-out infinite alternate"></span>
<span style="width:480px;height:480px;background:{b};bottom:-160px;right:-100px;animation:{anim}B 22s ease-in-out infinite alternate"></span>
<span style="width:260px;height:260px;background:{a};top:40%;left:50%;animation:{anim}C 26s ease-in-out infinite alternate"></span>
</div>
<style>
@keyframes {anim}A {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(140px,80px) scale(1.25); }} }}
@keyframes {anim}B {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(-160px,-90px) scale(1.15); }} }}
@keyframes {anim}C {{ from {{ transform: translate(-50%,-50%) scale(.8); }} to {{ transform: translate(-30%,-70%) scale(1.3); }} }}
</style>"""


# ---------- JS ----------
JS_COMMON = """
(function(){
  // Theme toggle
  const root = document.documentElement;
  const saved = localStorage.getItem('wp-theme');
  if(saved) root.setAttribute('data-theme', saved);
  const btn = document.getElementById('themeToggle');
  function syncLabel(){ if(!btn) return;
    btn.textContent = root.getAttribute('data-theme')==='light' ? 'Sombre' : 'Clair';
  }
  syncLabel();
  if(btn) btn.addEventListener('click', () => {
    const cur = root.getAttribute('data-theme')==='light' ? 'dark':'light';
    root.setAttribute('data-theme', cur);
    localStorage.setItem('wp-theme', cur);
    syncLabel();
  });
  // Lightbox
  const lb = document.getElementById('lightbox');
  if(lb){
    const lbImg = lb.querySelector('img');
    document.querySelectorAll('.gallery a[data-full]').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        lbImg.src = a.getAttribute('data-full');
        lb.classList.add('active');
        document.body.style.overflow='hidden';
      });
    });
    function close(){
      lb.classList.remove('active'); lbImg.src=''; document.body.style.overflow='';
    }
    lb.addEventListener('click', close);
    document.addEventListener('keydown', e => { if(e.key==='Escape') close(); });
  }
})();
"""


def build_page(
    title: str,
    folder: Path,
    theme: dict,
    body_main: str,
    is_root: bool,
) -> str:
    rel_root = rel_to_root(folder)
    rel_parent = "../" if not is_root else ""
    home_btn = "" if is_root else f'<a class="btn" href="{rel_root}index.html" title="Accueil">Accueil</a>'
    parent_btn = ""
    if not is_root and folder.parent != ROOT:
        parent_btn = f'<a class="btn" href="{rel_parent}index.html" title="Dossier parent">Parent</a>'
    css = build_css(theme)
    deco = deco_html(theme)
    safe_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title} — WallPaperS</title>
{BOILERPLATE_HEAD}
<style>{css}</style>
</head>
<body>
{BOILERPLATE_BODY}
{deco}
<div class="topbar">
  {home_btn}
  {parent_btn}
  <span style="flex:1"></span>
  <button class="btn" id="themeToggle" type="button">Clair</button>
</div>
<h1 class="title">{safe_title}</h1>
<p class="subtitle">Thème : {theme['name']}</p>
{body_main}
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true">
  <img alt="">
  <span class="hint">Clic ou Échap pour fermer</span>
</div>
<script>{JS_COMMON}</script>
</body>
</html>
"""


# ---------- Generation ----------
def list_subfolders(folder: Path) -> list[Path]:
    return sorted(
        [p for p in folder.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.name.lower(),
    )


def list_images(folder: Path) -> list[Path]:
    return sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS],
        key=lambda p: p.name.lower(),
    )


def folder_image_count_recursive(folder: Path) -> int:
    n = 0
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            n += 1
    return n


def find_preview_image(folder: Path) -> Path | None:
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            return p
    return None


def gallery_html(images: list[Path], page_folder: Path) -> str:
    items = []
    for img in images:
        rel = url_q(img.name)
        alt = html.escape(img.stem)
        items.append(
            f'<a href="{rel}" data-full="{rel}" title="{alt}"><img src="{rel}" alt="{alt}" loading="lazy"></a>'
        )
    return '<section class="gallery">\n' + "\n".join(items) + "\n</section>"


def pager_html(current: int, total: int, base: str) -> str:
    if total <= 1:
        return ""
    parts = ['<nav class="pager" aria-label="Pagination">']
    if current > 1:
        prev = base if current - 1 == 1 else f"page-{current-1}.html"
        parts.append(f'<a href="{prev}">&laquo; Préc</a>')
    for i in range(1, total + 1):
        href = base if i == 1 else f"page-{i}.html"
        if i == current:
            parts.append(f'<span class="current">{i}</span>')
        else:
            parts.append(f'<a href="{href}">{i}</a>')
    if current < total:
        nxt = f"page-{current+1}.html"
        parts.append(f'<a href="{nxt}">Suiv &raquo;</a>')
    parts.append("</nav>")
    return "\n".join(parts)


def subfolders_html(folder: Path, subs: list[Path]) -> str:
    if not subs:
        return ""
    cards = []
    for sub in subs:
        cnt = folder_image_count_recursive(sub)
        link = url_q(sub.name) + "/index.html"
        name = html.escape(sub.name)
        cards.append(
            f'<a class="folder-card" href="{link}">'
            f'<div class="folder-name">{name}</div>'
            f'<div class="folder-meta">{cnt} image{"s" if cnt != 1 else ""}</div>'
            f"</a>"
        )
    return (
        '<h2 class="title" style="font-size:1.6rem;margin-top:2rem">Sous-dossiers</h2>'
        '<section class="folders">\n' + "\n".join(cards) + "\n</section>"
    )


def write_folder_pages(folder: Path) -> None:
    images = list_images(folder)
    subs = list_subfolders(folder)
    rel_key = str(folder.relative_to(ROOT)).replace("\\", "/") or "ROOT"
    theme = pick_theme(rel_key)

    if not images and not subs:
        return  # nothing meaningful here

    title = folder.name if folder != SCAN_ROOT else "WallPaperS"

    if not images:
        body = subfolders_html(folder, subs)
        page = build_page(title, folder, theme, body, is_root=False)
        (folder / "index.html").write_text(page, encoding="utf-8")
        return

    total_pages = max(1, (len(images) + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE)
    for i in range(total_pages):
        chunk = images[i * IMAGES_PER_PAGE : (i + 1) * IMAGES_PER_PAGE]
        body = gallery_html(chunk, folder)
        body += pager_html(i + 1, total_pages, "index.html")
        if i == 0:
            body += subfolders_html(folder, subs)
        page = build_page(
            f"{title} — page {i+1}/{total_pages}" if total_pages > 1 else title,
            folder,
            theme,
            body,
            is_root=False,
        )
        out = folder / ("index.html" if i == 0 else f"page-{i+1}.html")
        out.write_text(page, encoding="utf-8")


def write_root_index() -> None:
    drawers = list_subfolders(SCAN_ROOT)
    cards = []
    for d in drawers:
        cnt = folder_image_count_recursive(d)
        link = "WallPaperS/" + url_q(d.name) + "/index.html"
        name = html.escape(d.name)
        cards.append(
            f'<a class="folder-card" href="{link}">'
            f'<div class="folder-name">{name}</div>'
            f'<div class="folder-meta">{cnt} image{"s" if cnt != 1 else ""}</div>'
            f"</a>"
        )
    body = (
        '<section class="folders">\n' + "\n".join(cards) + "\n</section>"
        if cards
        else '<p style="text-align:center;opacity:.7">Aucun tiroir trouvé.</p>'
    )
    theme = pick_theme("__ROOT__")
    page = build_page("WallPaperS Collector", ROOT, theme, body, is_root=True)
    (ROOT / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    if not SCAN_ROOT.exists():
        raise SystemExit(f"Missing {SCAN_ROOT}")
    # walk ALL folders under SCAN_ROOT (including SCAN_ROOT itself)
    all_dirs = [SCAN_ROOT] + [p for p in SCAN_ROOT.rglob("*") if p.is_dir()]
    for d in all_dirs:
        write_folder_pages(d)
    write_root_index()
    print(f"Generated index for {len(all_dirs)} folders + root.")


if __name__ == "__main__":
    main()
