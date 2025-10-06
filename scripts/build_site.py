#!/usr/bin/env python3
import json
import os
import re
import shutil
import sys
from urllib.parse import quote_plus


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def load_site_config(root):
    # Basic config; can be expanded or overridden by site_config.json
    cfg = {
        "site_name": "AGI Comics",
        "base_url": os.environ.get("BASE_URL", "/"),  # e.g. https://example.com
        "author": "",
        "description": "A comic series.",
        "twitter_handle": "",  # e.g. @yourhandle
        "explanation_label": os.environ.get("EXPLANATION_LABEL", "Explanation"),
        # Optional global likes API base (e.g., https://likes.example.com/api)
        "likes_api_base": os.environ.get("LIKES_API_BASE", None),
        # Optional: choose a specific comic to show on the homepage
        # by its slug (e.g., "ag-productivity"). If not set, homepage
        # will mirror the latest comic.
        "homepage_slug": None,
    }
    cfg_path = os.path.join(root, "site_config.json")
    if os.path.exists(cfg_path):
        try:
            data = read_json(cfg_path)
            if isinstance(data, dict):
                cfg.update({k: v for k, v in data.items() if v is not None})
        except Exception:
            pass
    # Normalize base_url
    bu = cfg.get("base_url") or "/"
    if not bu.endswith("/"):
        bu += "/"
    cfg["base_url"] = bu
    return cfg


def to_absolute(base_url: str, path: str) -> str:
    if base_url.startswith("http://") or base_url.startswith("https://"):
        if path.startswith("/"):
            return base_url.rstrip("/") + path
        else:
            return base_url + path
    # Fallback to relative path
    return path


def render_page_html(cfg, comic, index, total, prev_index, next_index, image_url, page_url):
    # We intentionally show only the current index, not total, per requirements.
    site_name = cfg["site_name"]
    title = f"{site_name} — #{index}: {comic['title']}"
    desc = comic.get("description") or cfg.get("description") or comic['title']
    og_image = to_absolute(cfg["base_url"], image_url)
    canonical = to_absolute(cfg["base_url"], page_url)

    # Share URLs
    share_text = f"{comic['title']}"
    share_url = canonical
    x_url = f"https://twitter.com/intent/tweet?text={quote_plus(share_text)}&url={quote_plus(share_url)}"
    bsky_url = f"https://bsky.app/intent/compose?text={quote_plus(share_text + ' ' + share_url)}"
    reddit_url = f"https://www.reddit.com/submit?url={quote_plus(share_url)}&title={quote_plus(share_text)}"

    # Direct image link
    direct_image_link = image_url
    

    # Minimal CSS inline to keep deployment simple
    css = """
    :root{--fg:#e6e6e6;--bg:#0b0b0f;--muted:#9aa0a6;--link:#7aa2ff;--link-hover:#a7c0ff;--img-max-h:75vh}
    *{box-sizing:border-box}
    body{margin:0;font:16px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg)}
    header,footer{padding:12px 16px}
    header{border-bottom:1px solid #1f232a;display:flex;flex-direction:column;align-items:center;gap:4px}
    header .title{font-weight:700;font-size:20px;text-align:center}
    header .meta{font-size:14px;color:var(--muted)}
    main{padding:24px 16px;max-width:980px;margin:0 auto}
    .comic{display:flex;flex-direction:column;align-items:center;width:100%}
    .comic .img-wrap{position:relative;display:inline-block}
    .comic img{max-width:100%;height:auto;max-height:var(--img-max-h);object-fit:contain;border-radius:2px}
    .meta{margin-top:8px;color:var(--muted);text-align:center}
    .likes{display:flex;align-items:center;gap:10px;justify-content:center;margin-top:14px}
    .like-btn{display:inline-flex;align-items:center;justify-content:center;padding:0;border:0;background:transparent;cursor:pointer;-webkit-appearance:none;appearance:none;outline:none}
    .like-btn:hover{opacity:.9}
    .like-count{font-variant-numeric:tabular-nums;color:#cbd5e1}
    .like-btn[disabled]{opacity:.6;cursor:default}
    .like-btn .icon{display:inline-block;font-size:1.35em;line-height:1;color:#ff3b4e}
    .share{display:flex;gap:16px;justify-content:center;align-items:center;margin-top:16px}
    .share .label{color:var(--muted);font-size:14px}
    .share a{color:var(--fg)}
    .share a:hover{color:var(--link-hover)}
    .share img{width:22px;height:22px;display:block}
    .share svg{width:22px;height:22px;display:block}
    .share img.icon-x{filter: invert(1)}
    .share svg{width:22px;height:22px;display:block}
    .share img.icon-x{filter: invert(1)}
    .share svg{width:22px;height:22px;display:block}
    .share img.icon-x{filter: invert(1)}
    .share svg{width:22px;height:22px;display:block}
    .share img.icon-x{filter: invert(1)}
    .share svg{width:22px;height:22px;display:block}
    .share img.icon-x{filter: invert(1)}
    .desc{margin-top:8px;max-width:800px;color:#d0d4d9;text-align:center}
    /* Title + inline likes */
    /* Title centered */
    .desc{display:block}
    .desc strong{display:inline-block;margin:0 auto}
    /* Likes block below title, centered */
    .likes{display:inline-flex;align-items:center;gap:8px;margin:6px auto 0}
    .like-btn{position:relative}
    .like-btn .heart{display:inline-block;font-size:4.0em;line-height:1;color:#ff2d55}
    .plus-one{position:absolute;top:-6px;left:50%;transform:translate(-50%,0);color:#ff6b81;font-weight:700;opacity:0;animation:plus1 450ms ease-out forwards;pointer-events:none;z-index:2}
    @keyframes plus1{0%{opacity:0;transform:translate(-50%,0)}20%{opacity:1}100%{opacity:0;transform:translate(-50%,-22px)}}
    details.expl{margin-top:12px;max-width:800px;text-align:left;background:#111521;border:1px solid #1f2633;border-radius:8px;overflow:hidden}
    details.expl summary{cursor:pointer;list-style:none;padding:10px 12px;font-weight:600;color:#dbe3ff;background:#0f1420}
    details.expl[open] summary{border-bottom:1px solid #1f2633}
    details.expl .content{padding:10px 12px;color:#c9ced6;line-height:1.6}
    details.expl .content p{margin:0 0 10px}
    a{color:var(--link);text-decoration:none}
    a:hover{color:var(--link-hover)}
    .nav-btn{position:absolute;top:-36px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:16px;background:#151922;border:1px solid #222937;color:#dbe3ff;text-decoration:none}
    .nav-btn:hover{background:#1a2030}
    .nav-btn.prev{left:0}
    .nav-btn.next{right:0}
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
    /* Search */
    .search{margin-top:8px;display:flex;justify-content:center}
    .search .box{position:relative;width:min(520px,92vw)}
    .search input[type="search"]{width:100%;padding:8px 10px;border-radius:8px;border:1px solid #222937;background:#0e1220;color:#e6e6e6;outline:none}
    .search input[type="search"]::placeholder{color:#8b93a7}
    .search .dd{position:absolute;top:100%;left:0;right:0;background:#0b0f1a;border:1px solid #20263b;border-top:none;border-radius:0 0 8px 8px;max-height:280px;overflow:auto;z-index:20;display:none}
    .search .dd.open{display:block}
    .search .item{padding:8px 10px;cursor:pointer}
    .search .item em{font-style:normal;color:#93c5fd}
    .search .item:hover{background:#0b1f4b;color:#ffffff}
    .search .item.active{background:#0b1f4b;color:#ffffff;border-left:3px solid #3b82f6}
    .search .item.active em{color:#bfdbfe}
    """

    # Optional collapsible explanation block (from description)
    explanation_html = ""
    _desc = (comic.get("description") or "").strip()
    if _desc:
        expl_label = cfg.get("explanation_label") or "Explanation"
        explanation_html = (
            f'<details class="expl">'
            f'<summary>{expl_label}</summary>'
            f'<div class="content">{comic.get("description", "")}</div>'
            f'</details>'
        )

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n  <title>{title}</title>
  <meta name=\"description\" content=\"{desc}\">\n  <link rel=\"canonical\" href=\"{canonical}\">\n  <meta property=\"og:type\" content=\"website\">\n  <meta property=\"og:title\" content=\"{title}\">\n  <meta property=\"og:description\" content=\"{desc}\">\n  <meta property=\"og:image\" content=\"{og_image}\">\n  <meta property=\"og:url\" content=\"{canonical}\">\n  {og_extras_block}\n  <meta name=\"twitter:card\" content=\"summary_large_image\">\n  <meta name=\"twitter:title\" content=\"{title}\">\n  <meta name=\"twitter:description\" content=\"{desc}\">\n  <meta name=\"twitter:image\" content=\"{og_image}\">\n  <meta name=\"twitter:image:alt\" content=\"{comic['title']}\">\n  {twitter_site_tag}<style>{css}</style>
</head>
<body>
  <header>
    <div class=\"title\">{site_name}</div>
    <div class=\"meta\">Comic #{index}</div>
    <div class=\"search\">
      <div class=\"box\">
        <input id=\"q\" type=\"search\" placeholder=\"Search comics...\" autocomplete=\"off\" aria-label=\"Search comics\"/>
        <div class=\"dd\" role=\"listbox\" aria-label=\"Search suggestions\"></div>
      </div>
    </div>
  </header>
  <main>
    <div class=\"comic\">
      <img src=\"{image_url}\" alt=\"{comic['title']}\" loading=\"eager\">\n      <div class=\"desc\"><strong>{comic['title']}</strong></div>\n      {explanation_html}
      <div class=\"meta\"><a href=\"{direct_image_link}\">Direct image link</a> • <a href=\"{page_url}\">Permalink</a></div>
    </div>
    <nav class=\"nav\" aria-label=\"Comic navigation\">
      <a href=\"/{prev_index}/\" rel=\"prev\" aria-label=\"Previous comic\">← Previous</a>
      <a href=\"/{next_index}/\" rel=\"next\" aria-label=\"Next comic\">Next →</a>
    </nav>
    <div class=\"share\">
      <span>Share:</span>
      <a href=\"{x_url}\" target=\"_blank\" rel=\"noopener noreferrer\">X</a>
      <a href=\"{bsky_url}\" target=\"_blank\" rel=\"noopener noreferrer\">Bluesky</a>
      <a href=\"{reddit_url}\" target=\"_blank\" rel=\"noopener noreferrer\">Reddit</a>
    </div>
  </main>
  
</body>
</html>"""
    return html


def render_page_html2(cfg, comic, index, total, prev_slug, next_slug, image_url, page_url, canonical_url, og_image_url, width=None, height=None, path_prefix="/", og_width=None, og_height=None, og_mime=None):
    site_name = cfg["site_name"]
    title = f"{site_name} — #{index}: {comic['title']}"
    desc = comic.get("description") or cfg.get("description") or comic['title']
    og_image = to_absolute(cfg["base_url"], og_image_url)
    canonical = to_absolute(cfg["base_url"], canonical_url)

    share_text = f"{comic['title']}"
    share_url = canonical
    x_url = f"https://twitter.com/intent/tweet?text={quote_plus(share_text)}&url={quote_plus(share_url)}"
    bsky_url = f"https://bsky.app/intent/compose?text={quote_plus(share_text + ' ' + share_url)}"
    reddit_url = f"https://www.reddit.com/submit?url={quote_plus(share_url)}&title={quote_plus(share_text)}"

    direct_image_link = image_url
    

    css = """
    :root{--fg:#e6e6e6;--bg:#0b0b0f;--muted:#9aa0a6;--link:#7aa2ff;--link-hover:#a7c0ff;--img-max-h:75vh}
    *{box-sizing:border-box}
    body{margin:0;font:16px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg)}
    header,footer{padding:12px 16px}
    header{border-bottom:1px solid #1f232a;display:flex;flex-direction:column;align-items:center;gap:4px}
    header .title{font-weight:700;font-size:20px;text-align:center}
    header .meta{font-size:14px;color:var(--muted)}
    main{padding:24px 16px;max-width:980px;margin:0 auto}
    .comic{display:flex;flex-direction:column;align-items:center;width:100%}
    .comic .img-wrap{position:relative;display:inline-block}
    .comic img{max-width:100%;height:auto;max-height:var(--img-max-h);object-fit:contain;border-radius:2px}
    .meta{margin-top:8px;color:var(--muted);text-align:center}
    .share{display:flex;gap:16px;justify-content:center;align-items:center;margin-top:16px}
    .share .label{color:var(--muted);font-size:14px}
    .share a{color:var(--fg)}
    .share a:hover{color:var(--link-hover)}
    .share img{width:22px;height:22px;display:block}
    .desc{margin-top:8px;max-width:800px;color:#d0d4d9;text-align:center}
    a{color:var(--link);text-decoration:none}
    a:hover{color:var(--link-hover)}
    .nav-btn{position:absolute;top:-36px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:16px;background:#151922;border:1px solid #222937;color:#dbe3ff;text-decoration:none}
    .nav-btn:hover{background:#1a2030}
    .nav-btn.prev{left:0}
    .nav-btn.next{right:0}
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
    """

    # Optional Twitter handle
    twitter_site_tag = ""
    if cfg.get("twitter_handle"):
        twitter_site_tag = f'<meta name="twitter:site" content="{cfg.get("twitter_handle")}">'

    # OG image extra tags
    og_extras = []
    if og_width:
        og_extras.append(f'<meta property="og:image:width" content="{int(og_width)}">')
    if og_height:
        og_extras.append(f'<meta property="og:image:height" content="{int(og_height)}">')
    if og_mime:
        og_extras.append(f'<meta property="og:image:type" content="{og_mime}">')
    og_extras_block = "\n  ".join(og_extras)

    # Build optional explanation block from description
    explanation_html = ""
    desc_val = (comic.get('description') or '').strip()
    if desc_val:
        expl_label2 = cfg.get("explanation_label") or "Explanation"
        explanation_html = (
            f'<details class="expl">'
            f'<summary>{expl_label2}</summary>'
            f'<div class="content">{comic.get("description","")}</div>'
            f'</details>'
        )

    size_attrs = ""
    if width and height:
        size_attrs = f" width=\"{int(width)}\" height=\"{int(height)}\""

    html = f"""<!doctype html>
<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n  <title>{title}</title>
  <meta name=\"description\" content=\"{desc}\">\n  <link rel=\"canonical\" href=\"{canonical}\">\n  <meta property=\"og:type\" content=\"website\">\n  <meta property=\"og:title\" content=\"{title}\">\n  <meta property=\"og:description\" content=\"{desc}\">\n  <meta property=\"og:image\" content=\"{og_image}\">\n  <meta property=\"og:url\" content=\"{canonical}\">\n  {og_extras_block}\n  <meta name=\"twitter:card\" content=\"summary_large_image\">\n  <meta name=\"twitter:title\" content=\"{title}\">\n  <meta name=\"twitter:description\" content=\"{desc}\">\n  <meta name=\"twitter:image\" content=\"{og_image}\">\n  <meta name=\"twitter:image:alt\" content=\"{comic['title']}\">\n  {twitter_site_tag}<style>{css}</style>
</head>
<body>
  <header>
    <div class=\"title\">{site_name}</div>
    <div class=\"meta\">Comic #{index}</div>
    <div class=\"search\">\n      <div class=\"box\">\n        <input id=\"q\" type=\"search\" placeholder=\"Search comics...\" autocomplete=\"off\" aria-label=\"Search comics\"/>\n        <div class=\"dd\" role=\"listbox\" aria-label=\"Search suggestions\"></div>\n      </div>\n    </div>
  </header>
  <main>
    <div class=\"comic\">\n      <div class=\"img-wrap\">\n        <a class=\"nav-btn prev\" href=\"{path_prefix}c/{prev_slug}/\" aria-label=\"Previous comic\">&#8592;</a>
        <a class=\"nav-btn next\" href=\"{path_prefix}c/{next_slug}/\" aria-label=\"Next comic\">&#8594;</a>
        <img src=\"{image_url}\" alt=\"{comic['title']}\" loading=\"eager\"{size_attrs}>\n      </div>\n      <div class=\"desc\"><strong>{comic['title']}</strong></div>\n      <div class=\"likes\" data-slug=\"{comic['slug']}\"><button class=\"like-btn\" type=\"button\" aria-pressed=\"false\" aria-label=\"Like this comic\"><span class=\"heart\" aria-hidden=\"true\">❤</span></button> <span class=\"like-count\" aria-live=\"polite\">0</span></div>\n      {explanation_html}
      <div class=\"meta\"><a href=\"{direct_image_link}\">Direct image link</a> • <a href=\"{canonical_url}\">Permalink</a></div>
      <div class=\"share\">\n+        <span class=\"label\">share on</span>
        <a href=\"{x_url}\" target=\"_blank\" rel=\"noopener noreferrer\" aria-label=\"Share on X\" title=\"Share on X\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 4l16 16M20 4L4 20\"/></svg></a>
        <a href=\"{bsky_url}\" target=\"_blank\" rel=\"noopener noreferrer\" aria-label=\"Share on Bluesky\" title=\"Share on Bluesky\"><svg viewBox=\"0 0 24 24\" fill=\"currentColor\"><path d=\"M6 7c1.5 1.8 3.8 3 6 6 2.2-3 4.5-4.2 6-6-1 3-2.5 5-6 8-3.5-3-5-5-6-8z\"/></svg></a>
        <a href=\"{reddit_url}\" target=\"_blank\" rel=\"noopener noreferrer\" aria-label=\"Share on Reddit\" title=\"Share on Reddit\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\"><circle cx=\"12\" cy=\"13\" r=\"7\"/><circle cx=\"9\" cy=\"12\" r=\"1\" fill=\"currentColor\"/><circle cx=\"15\" cy=\"12\" r=\"1\" fill=\"currentColor\"/><path d=\"M9 15c1.5 1 4.5 1 6 0\"/></svg></a>
      </div>
      <div class=\"copyright\">© <a href=\"https://www.dileeplearning.com\" target=\"_blank\" rel=\"noopener noreferrer\">Dileep George</a> • <a href=\"https://blog.dileeplearning.com\" target=\"_blank\" rel=\"noopener noreferrer\">AGI blog</a></div>
    </div>
  </main>
  
  <script>(function(){{
    var LIKE_API_BASE = "{(cfg.get('likes_api_base') or '').strip()}"; // optional Worker API; fallback to CountAPI
    function adjustMaxImageHeight(){{
      var h = window.innerHeight;
      var header = document.querySelector('header');
      var footer = document.querySelector('footer');
      var nav = document.querySelector('.nav');
      var share = document.querySelector('.share');
      var desc = document.querySelector('.desc');
      var r = 0; [header,footer,nav,share,desc].forEach(function(el){{ if(el) r += el.offsetHeight; }});
      r += 40; // breathing room
      var m = Math.max(120, h - r);
      document.documentElement.style.setProperty('--img-max-h', m + 'px');
    }}
    window.addEventListener('load', adjustMaxImageHeight);
    window.addEventListener('resize', adjustMaxImageHeight);

    // Keyboard navigation: Left/Right arrows (and h/l) go prev/next
    function go(href){{ if(href) window.location.href = href; }}
    document.addEventListener('keydown', function(e){{
      if (e.defaultPrevented) return;
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      var prev = document.querySelector('a.nav-btn.prev') || document.querySelector('a[rel="prev"]');
      var next = document.querySelector('a.nav-btn.next') || document.querySelector('a[rel="next"]');
      if (e.key === 'ArrowLeft' || e.key === 'h') {{ if (prev) {{ e.preventDefault(); go(prev.getAttribute('href')); }} }}
      else if (e.key === 'ArrowRight' || e.key === 'l') {{ if (next) {{ e.preventDefault(); go(next.getAttribute('href')); }} }}
    }});
    // Search autocomplete (titles)
    (function(){{
      var PATH_PREFIX = "{path_prefix}";
      function norm(s){{ return (s||'').toLowerCase().replace(/[^a-z0-9]+/g,''); }}
      function fuzzyScore(q, t){{
        var nq = norm(q), nt = norm(t);
        if (!nq) return 1e9;
        var idx = nt.indexOf(nq);
        if (idx >= 0) return idx;
        var qi=0, score=0;
        for (var i=0;i<nt.length && qi<nq.length;i++){{ if (nt[i]===nq[qi]){{ qi++; score+=i; }} }}
        if (qi===nq.length) return 500+score;
        return 1e9;
      }}
      var box = document.querySelector('.search .box');
      if (!box) return;
      var input = box.querySelector('#q');
      var dd = box.querySelector('.dd');
      var data = null; var active = -1;
      function openDD(){{ dd.classList.add('open'); }}
      function closeDD(){{ dd.classList.remove('open'); active=-1; }}
      function render(list, q){{
        dd.innerHTML='';
        // Render full result set; .dd limits visible height so ~10 show at once
        list.forEach(function(it,i){{
          var div=document.createElement('div');
          div.className='item'+(i===active?' active':'');
          div.setAttribute('role','option');
          var title=it.t; var nq=(q||'').trim().toLowerCase();
          var pos=title.toLowerCase().indexOf(nq);
          if(nq && pos>=0){{
            div.innerHTML=title.slice(0,pos)+'<em>'+title.slice(pos,pos+nq.length)+'</em>'+title.slice(pos+nq.length);
          }} else {{ div.textContent=title; }}
          div.addEventListener('mousedown', function(ev){{ ev.preventDefault(); window.location.href = PATH_PREFIX+'c/'+it.s+'/'; }});
          dd.appendChild(div);
        }});
        if (list.length) openDD(); else closeDD();
      }}
      function update(){{ if(!data) return; var q=input.value; var scored=data.map(function(it){{return {{it:it,s:fuzzyScore(q,it.t)}};}}).filter(function(x){{return x.s<1e9;}}); scored.sort(function(a,b){{return a.s-b.s;}}); render(scored.map(function(x){{return x.it;}}), q); }}
      function showAll(){{ if(!data) return; active=-1; render(data.slice(0, data.length), ''); }}
      function fetchIndex(){{ fetch(PATH_PREFIX+'search-index.json',{{cache:'no-store'}}).then(function(r){{return r.ok?r.json():[];}}).then(function(j){{ data=Array.isArray(j)?j:[]; if (document.activeElement===input && !(input.value||'').trim()) {{ showAll(); }} else {{ update(); }} }}).catch(function(){{ data=[]; }}); }}
      input.addEventListener('input', function(){{ active=-1; update(); }});
      input.addEventListener('focus', function(){{ if(!data) fetchIndex(); else if(!(input.value||'').trim()) showAll(); }});
      input.addEventListener('click', function(){{ if(data && !(input.value||'').trim()) showAll(); }});
      input.addEventListener('keydown', function(e){{
        var items=dd.querySelectorAll('.item');
        function highlight(){{
          for (var i=0;i<items.length;i++){{
            items[i].classList.toggle('active', i===active);
            if (i===active){{ items[i].style.background='#0b1f4b'; items[i].style.color='#ffffff'; }}
            else {{ items[i].style.background=''; items[i].style.color=''; }}
          }}
          if (active>=0 && items[active] && typeof items[active].scrollIntoView==='function'){{ try {{ items[active].scrollIntoView({{block:'nearest'}}); }} catch(e){{}} }}
        }}
        if(e.key==='ArrowDown'){{ e.preventDefault(); if(items.length){{ active=(active+1)%items.length; highlight(); }} }}
        else if(e.key==='ArrowUp'){{ e.preventDefault(); if(items.length){{ active=(active-1+items.length)%items.length; highlight(); }} }}
        else if(e.key==='Enter'){{ if(items.length){{ e.preventDefault(); if (active<0) active=0; items[active].dispatchEvent(new Event('mousedown')); }} }}
        else if(e.key==='Escape'){{ closeDD(); }}
      }});
      document.addEventListener('click', function(e){{ if(!box.contains(e.target)) closeDD(); }});
      fetchIndex();
    }})();
    // Lightweight global likes using optional Worker API or CountAPI fallback
    function apiGet(slug){{
      if (!LIKE_API_BASE) return null;
      var base = LIKE_API_BASE.replace(/\/$/,'');
      var isGAS = /script\.google\.com\/macros\/s\//.test(base);
      var u = isGAS
        ? base + '?action=likes&slug=' + encodeURIComponent(slug) + '&t=' + Date.now()
        : base + '/likes?slug=' + encodeURIComponent(slug) + '&t=' + Date.now();
      return fetch(u, {{mode:'cors', credentials:'omit', cache:'no-store', referrerPolicy:'no-referrer'}})
        .then(function(r){{ return r.ok ? r.json() : null; }})
        .then(function(d){{
          if (!d) return null;
          if (typeof d.count === 'number') return d.count;
          if (typeof d.value === 'number') return d.value; // tolerate alt format
          return null;
        }})
        .catch(function(){{ return null; }});
    }}
    function apiHit(slug){{
      if (!LIKE_API_BASE) return null;
      var base = LIKE_API_BASE.replace(/\/$/,'');
      var isGAS = /script\.google\.com\/macros\/s\//.test(base);
      var u = isGAS
        ? base + '?action=hit&slug=' + encodeURIComponent(slug) + '&t=' + Date.now()
        : base + '/hit?slug=' + encodeURIComponent(slug) + '&t=' + Date.now();
      return fetch(u, {{mode:'cors', credentials:'omit', cache:'no-store', referrerPolicy:'no-referrer'}})
        .then(function(r){{ return r.ok ? r.json() : null; }})
        .then(function(d){{
          if (!d) return null;
          if (typeof d.count === 'number') return d.count;
          if (typeof d.value === 'number') return d.value;
          return null;
        }})
        .catch(function(){{ return null; }});
    }}
    function countapiGet(ns, key){{
      var u = 'https://api.countapi.xyz/get/' + encodeURIComponent(ns) + '/' + encodeURIComponent(key) + '?t=' + Date.now();
      return fetch(u, {{mode:'cors', credentials:'omit', cache:'no-store', referrerPolicy:'no-referrer'}})
        .then(function(r){{ return r.ok ? r.json() : null; }})
        .then(function(d){{ return d && typeof d.value === 'number' ? d.value : null; }})
        .catch(function(){{ return null; }});
    }}
    function countapiUpdate(ns, key, amount){{
      var u = 'https://api.countapi.xyz/update/' + encodeURIComponent(ns) + '/' + encodeURIComponent(key) + '?amount=' + String(amount) + '&t=' + Date.now();
      return fetch(u, {{mode:'cors', credentials:'omit', cache:'no-store', referrerPolicy:'no-referrer'}})
        .then(function(r){{ return r.ok ? r.json() : null; }})
        .then(function(d){{ return d && typeof d.value === 'number' ? d.value : null; }})
        .catch(function(){{ return null; }});
    }}
    function countapiHit(ns, key){{
      var u = 'https://api.countapi.xyz/hit/' + encodeURIComponent(ns) + '/' + encodeURIComponent(key) + '?t=' + Date.now();
      return fetch(u, {{mode:'cors', credentials:'omit', cache:'no-store', referrerPolicy:'no-referrer'}})
        .then(function(r){{ return r.ok ? r.json() : null; }})
        .then(function(d){{ return d && typeof d.value === 'number' ? d.value : null; }})
        .catch(function(){{ return null; }});
    }}
    function countapiCreate(ns, key){{
      var u = 'https://api.countapi.xyz/create?namespace=' + encodeURIComponent(ns) + '&key=' + encodeURIComponent(key) + '&value=0&t=' + Date.now();
      return fetch(u, {{mode:'cors', credentials:'omit', cache:'no-store', referrerPolicy:'no-referrer'}})
        .then(function(r){{ return r.ok ? r.json() : null; }})
        .then(function(d){{ return d && typeof d.value === 'number' ? d.value : 0; }})
        .catch(function(){{ return 0; }});
    }}
    function setupCountApiLikes(){{
      function showPlusOne(btn){{
        try {{
          var bubble = document.createElement('span');
          bubble.className = 'plus-one';
          bubble.textContent = '+1';
          if (!btn) return;
          btn.appendChild(bubble);
          setTimeout(function(){{ if (bubble && bubble.parentNode) bubble.parentNode.removeChild(bubble); }}, 600);
        }} catch(e) {{}}
      }}
      var wrap = document.querySelector('.likes');
      if (!wrap) return;
      var NS = 'agicomics';
      var slug = wrap.getAttribute('data-slug') || '';
      if (!slug) return;
      var key = 'like-' + slug;
      var btn = wrap.querySelector('.like-btn');
      var cnt = wrap.querySelector('.like-count');
      btn.setAttribute('aria-pressed', 'false');
      // Try Worker API first if configured; otherwise use CountAPI
      var init = apiGet(slug);
      if (init && typeof init.then === 'function'){{
        init.then(function(v){{
          if (typeof v === 'number') cnt.textContent = String(v);
          else {{
            countapiGet(NS, key).then(function(v2){{ if (typeof v2 === 'number') cnt.textContent = String(v2); else {{
              countapiCreate(NS, key).then(function(v3){{ cnt.textContent = String(v3 || 0); }});
            }} }});
          }}
        }});
      }} else {{
        countapiGet(NS, key).then(function(v){{
          if (v === null) {{
            return countapiCreate(NS, key).then(function(v2){{ cnt.textContent = String(v2 || 0); }});
          }} else {{
            cnt.textContent = String(v);
          }}
        }});
      }}
      btn.addEventListener('click', function(){{
        // Immediate feedback: float +1 and optimistic increment
        showPlusOne(btn);
        var cur = parseInt(cnt.textContent, 10) || 0;
        cnt.textContent = String(cur + 1);
        var inc = apiHit(slug);
        if (inc && typeof inc.then === 'function'){{
          inc.then(function(v){{
            if (typeof v === 'number') cnt.textContent = String(v);
            else countapiGet(NS, key).then(function(v2){{ if (typeof v2 === 'number') cnt.textContent = String(v2); }});
          }});
        }} else {{
          // CountAPI fallback
          countapiHit(NS, key).then(function(v){{
            if (typeof v === 'number') cnt.textContent = String(v);
            else countapiGet(NS, key).then(function(v2){{ if (typeof v2 === 'number') cnt.textContent = String(v2); }});
          }});
        }}
      }});
    }}
    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', setupCountApiLikes);
    }} else {{
      setupCountApiLikes();
    }}
  }})();</script>
</body>
</html>"""
    return html


def swap_brand_icons(html: str, avail: dict, path_prefix: str = "/") -> str:
    # Replace inline placeholder SVGs with external brand SVG images if present
    import re as _re
    # Ensure prefix ends with a single slash or is empty
    pp = path_prefix or "/"
    if not pp.endswith('/'):
        pp += '/'
    if avail.get('x'):
        html = _re.sub(r'(<a[^>]*title="Share on X"[^>]*>)(.*?)(</a>)', lambda m: m.group(1) + f'<img class="icon icon-x" src="{pp}icons/x.svg" alt="X" style="filter:invert(1)">' + m.group(3), html, flags=_re.DOTALL)
    if avail.get('bluesky'):
        html = _re.sub(r'(<a[^>]*title="Share on Bluesky"[^>]*>)(.*?)(</a>)', lambda m: m.group(1) + f'<img class="icon icon-bluesky" src="{pp}icons/bluesky.svg" alt="Bluesky">' + m.group(3), html, flags=_re.DOTALL)
    if avail.get('reddit'):
        html = _re.sub(r'(<a[^>]*title="Share on Reddit"[^>]*>)(.*?)(</a>)', lambda m: m.group(1) + f'<img class="icon icon-reddit" src="{pp}icons/reddit.svg" alt="Reddit">' + m.group(3), html, flags=_re.DOTALL)
    # Also fix any accidental leading '+' artifacts in the label line
    html = html.replace('\n+        <span class="label"', '\n        <span class="label"')
    return html

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    comics_path = os.path.join(root, "comics.json")
    comics_dir = os.path.join(root, "comics")
    out_dir = os.path.join(root, "public")

    if not os.path.exists(comics_path):
        print("ERROR: comics.json not found. Run scripts/generate_comics_json.py first.", file=sys.stderr)
        sys.exit(1)

    data = read_json(comics_path)
    comics = data.get("comics", [])
    # Filter out comics marked invisible
    comics = [c for c in comics if not (isinstance(c.get('visible'), bool) and c.get('visible') is False)]
    # Optional ordering: if an integer field 'order' exists, sort ascending by it.
    # Comics without 'order' keep their original relative order and appear after those with an order.
    def _sort_key(item_with_index):
        idx, c = item_with_index
        v = c.get('order')
        try:
            val = int(v)
        except Exception:
            val = None
        # Items with no valid order go after ordered ones (use a large sentinel),
        # and preserve original order via the original index as tiebreaker.
        return (val if val is not None else 10_000_000, idx)

    comics = [c for _, c in sorted(list(enumerate(comics)), key=_sort_key)]
    if not comics:
        print("ERROR: No comics in comics.json", file=sys.stderr)
        sys.exit(1)

    cfg = load_site_config(root)

    # Prepare output directories
    ensure_dir(out_dir)
    images_out = os.path.join(out_dir, "images")
    ensure_dir(images_out)

    # Optional optimization: create webp alongside originals if Pillow is available
    try:
        from PIL import Image  # type: ignore
        have_pillow = True
    except Exception:
        have_pillow = False

    # Copy images under slug.ext for stable URLs
    for c in comics:
        src = os.path.join(comics_dir, c["file"])
        if not os.path.isfile(src):
            print(f"WARNING: Missing file {src}, skipping copy", file=sys.stderr)
            continue
        dest_name = f"{c['slug']}{c['ext']}"
        dest = os.path.join(images_out, dest_name)
        # Copy if changed or not exists
        if not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(src):
            shutil.copy2(src, dest)
        if have_pillow:
            try:
                img = Image.open(src)
                webp_dest = os.path.join(images_out, f"{c['slug']}.webp")
                save_kwargs = {"optimize": True, "quality": 80}
                img.convert("RGBA" if img.mode in ("RGBA", "LA") else "RGB").save(webp_dest, format="WEBP", **save_kwargs)
            except Exception as e:
                print(f"NOTE: Could not generate webp for {src}: {e}", file=sys.stderr)

    total = len(comics)

    # Prepare icons before generating pages so replacements know availability
    icons_src = os.path.join(root, 'assets', 'icons')
    icons_out = os.path.join(out_dir, 'icons')
    ensure_dir(icons_out)
    available_icons = {}
    if os.path.isdir(icons_src):
        for name in os.listdir(icons_src):
            if name.lower().endswith('.svg'):
                try:
                    shutil.copy2(os.path.join(icons_src, name), os.path.join(icons_out, name))
                    available_icons[os.path.splitext(name)[0].lower()] = True
                except Exception:
                    pass

    # Generate a lightweight search index (title + slug) for client-side autocomplete
    try:
        search_index = [{"t": c.get("title", ""), "s": c.get("slug", "")} for c in comics]
        with open(os.path.join(out_dir, "search-index.json"), "w", encoding="utf-8") as f:
            json.dump(search_index, f, ensure_ascii=False)
    except Exception:
        pass

    # Generate per-index pages and slug permalinks
    latest_index = total
    latest_html = None
    homepage_slug = (cfg.get('homepage_slug') or '').strip() if isinstance(cfg.get('homepage_slug'), str) else None
    homepage_html = None
    path_prefix = cfg.get('base_path', '/')
    for i, c in enumerate(comics, start=1):
        prev_index = total if i == 1 else i - 1
        next_index = 1 if i == total else i + 1
        prev_slug = comics[prev_index - 1]["slug"]
        next_slug = comics[next_index - 1]["slug"]

        original_image_rel = f"{path_prefix}images/{c['slug']}{c['ext']}"
        webp_rel = f"{path_prefix}images/{c['slug']}.webp"
        image_rel = webp_rel if os.path.exists(os.path.join(images_out, f"{c['slug']}.webp")) else original_image_rel

        width = height = None
        if os.path.exists(os.path.join(images_out, f"{c['slug']}.webp")):
            try:
                from PIL import Image  # type: ignore
                with Image.open(os.path.join(images_out, f"{c['slug']}.webp")) as im:
                    width, height = im.size
            except Exception:
                pass

        numeric_page_rel = f"{path_prefix}{i}/"
        slug_page_rel = f"{path_prefix}c/{c['slug']}/"

        # Determine OG image dimensions and mime type from original image
        og_width = og_height = None
        og_mime = None
        try:
            ext = (c.get('ext') or '').lower()
            og_mime = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png' if ext == '.png' else 'image/webp' if ext == '.webp' else None
            orig_path = os.path.join(images_out, f"{c['slug']}{c['ext']}")
            from PIL import Image  # type: ignore
            with Image.open(orig_path) as im:
                og_width, og_height = im.size
        except Exception:
            pass

        # Numeric page that canonicals to slug
        html_numeric = render_page_html2(
            cfg, c, i, total, prev_slug, next_slug,
            image_url=image_rel,
            page_url=numeric_page_rel,
            canonical_url=slug_page_rel,
            og_image_url=original_image_rel,
            width=width,
            height=height,
            og_width=og_width,
            og_height=og_height,
            og_mime=og_mime,
            path_prefix=path_prefix,
        )
        html_numeric = swap_brand_icons(html_numeric, available_icons, path_prefix)
        page_dir = os.path.join(out_dir, str(i))
        ensure_dir(page_dir)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_numeric)

        # Slug permalink page
        html_slug = render_page_html2(
            cfg, c, i, total, prev_slug, next_slug,
            image_url=image_rel,
            page_url=slug_page_rel,
            canonical_url=slug_page_rel,
            og_image_url=original_image_rel,
            width=width,
            height=height,
            og_width=og_width,
            og_height=og_height,
            og_mime=og_mime,
            path_prefix=path_prefix,
        )
        html_slug = swap_brand_icons(html_slug, available_icons, path_prefix)
        slug_dir = os.path.join(out_dir, "c", c["slug"])
        ensure_dir(slug_dir)
        with open(os.path.join(slug_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_slug)

        if i == latest_index:
            latest_html = html_slug
        if homepage_slug and c.get('slug') == homepage_slug:
            homepage_html = html_slug

    # The homepage mirrors a chosen slug if provided, otherwise the latest comic
    chosen_home = homepage_html or latest_html
    if chosen_home:
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(chosen_home)

    # robots.txt and a lightweight 404
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n")

    with open(os.path.join(out_dir, "404.html"), "w", encoding="utf-8") as f:
        f.write("<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Not Found</title><p>Page not found. <a href='/'>Go home</a>.</p>")

    # Ensure GitHub Pages does not run Jekyll
    with open(os.path.join(out_dir, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    print(f"Built site with {total} comics into {out_dir}")


if __name__ == "__main__":
    main()
