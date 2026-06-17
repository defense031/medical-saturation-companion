#!/usr/bin/env python3
"""Assemble index.html — a single-file briefing with a left-sidebar switcher —
from the section fragments under sections/ plus the standalone sim.html.

Sources:
    sections/01_framing.html  …  sections/06_references.html   (content fragments)
    sim.html                                                    (full standalone app)
Edit a source, then rebuild:
    python3 build_unified.py

The prose fragments are pure panel content (no <head>/<style>). This script wraps
them in one shell: a consolidated stylesheet, KaTeX (math) and Mermaid (the Framing
causal diagrams) both loaded once, a grouped sidebar, the cross-tab citation jumps
(goCite), and the sim's discrete-event engine extracted from sim.html. The sim
canvas refits when its panel is shown and its animation loop pauses while hidden.
index.html is GENERATED — do not edit it directly.
"""
import re, os

D = os.path.dirname(os.path.abspath(__file__))
def rd(f): return open(os.path.join(D, f), encoding="utf-8").read()

# ---- ordered panels: (id, label, sublabel, source file, group, kind) ----
SECTIONS = [
    ("framing",    "Framing",    "the problem · the decision · the levers",    "sections/01_framing.html",    "Overview",   "prose"),
    ("sim",        "Sim",        "the live casualty chain",                    "sections/sim.html",           "Explore",    "sim"),
    ("posture",    "Posture",    "consolidate vs distribute · the crossover",  "sections/posture.html",       "Explore",    "prose"),
    ("plan",       "Plan",       "question · hypotheses · limits",             "sections/02_plan.html",       "Analysis",   "prose"),
    ("methods",    "Methods",    "the queue model · validation",               "sections/03_methods.html",    "Analysis",   "prose"),
    ("results",    "Results",    "the three findings",                         "sections/04_results.html",    "Analysis",   "prose"),
    ("discussion", "Discussion", "so-what · robustness · limits",              "sections/05_discussion.html", "Analysis",   "prose"),
    ("refs",       "References", "sources",                                    "sections/06_references.html", "Back matter","prose"),
]
FIRST = SECTIONS[0][0]

def inner(html, tag):
    m = re.search(r'<' + tag + r'\b[^>]*>(.*?)</' + tag + r'>', html, re.S)
    return m.group(1) if m else ""
def body_script(html):
    cands = [c for c in re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.S) if c.strip()]
    return cands[-1] if cands else ""

# sim styling that the consolidated BASE already provides — drop these, keep the rest
SIM_SHARED = {':root', '*', 'body', 'a', 'header', 'header h1', 'header .sub', 'header a',
              'main', 'h2', 'h3', 'p,li', '.card', 'table', 'th,td', 'th', 'code', '.note', '.legend'}
def strip_shared(css):
    out = []
    for sel, bod in re.findall(r'([^{}]+)\{([^{}]*)\}', css, re.S):
        if sel.strip() in SIM_SHARED:
            continue
        out.append(sel.strip() + "{" + bod.strip() + "}")
    return "\n  ".join(out)

def links(s):  # only the sim's body carries old page hrefs; the primer now lives in Methods
    return (s.replace('href="PLAN.html"',    'href="#" onclick="showPanel(\'methods\');return false"')
             .replace('href="sim.html"',     'href="#" onclick="showPanel(\'sim\');return false"')
             .replace('href="FRAMING.html"', 'href="#" onclick="showPanel(\'framing\');return false"'))

# ---- pull content ----
panels, sim_css, sim_script = [], "", ""
for sid, label, sub, src, group, kind in SECTIONS:
    html = rd(src)
    if kind == "sim":
        content = links(inner(html, "main"))
        sim_css = strip_shared(inner(html, "style"))
        sim_script = body_script(html)
    else:
        content = html  # fragment is already pure panel content
    on = " on" if sid == FIRST else ""
    panels.append(f'<section id="p-{sid}" class="panel{on}"><div class="pmain">{content}</div></section>')

for nm, v in [("sim_css", sim_css), ("sim_script", sim_script)]:
    if not v.strip():
        print("WARN empty:", nm)

# pause the sim animation loop while its panel is hidden
sim_script = sim_script.replace(
    "function frame(ts){\n  const dtReal=",
    "function frame(ts){\n  if(!document.getElementById('p-sim').classList.contains('on')){requestAnimationFrame(frame);return;}\n  const dtReal=")

# ---- sidebar ----
side = ['<div class="side">']
last_group = None
for sid, label, sub, src, group, kind in SECTIONS:
    if group != last_group:
        side.append(f'<div class="grp">{group}</div>')
        last_group = group
    on = " active" if sid == FIRST else ""
    side.append(f'<button class="sbtn{on}" data-p="{sid}" onclick="showPanel(\'{sid}\')">{label}<span class="d">{sub}</span></button>')
side.append('</div>')
side = "\n    ".join(side)

BASE = r"""
:root{--ink:#1a1f25;--mut:#5b6672;--line:#dde3ea;--bg:#f7f9fc;--card:#fff;--accent:#7a1f1f;--accent2:#16607a;--good:#1c6b3c;--warn:#9a6a00;--bad:#9a2020}
*{box-sizing:border-box}
body{margin:0;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent2)}
header{background:linear-gradient(135deg,#7a1f1f,#5a1616);color:#fff;padding:18px 28px}
header h1{margin:0 0 3px;font-size:20px;letter-spacing:.2px}
header .sub{opacity:.92;font-size:13.5px}
header .auth{margin-top:7px;font-size:13.5px;font-weight:600;opacity:.96;letter-spacing:.2px}
header .meta{margin-top:6px;font-size:12px;opacity:.85}
header a{color:#ffd9d9}
.app{display:flex;align-items:flex-start}
.side{flex:0 0 210px;position:sticky;top:0;align-self:flex-start;height:100vh;background:#fff;border-right:1px solid var(--line);padding:14px 10px;overflow:auto}
.side .grp{font-size:10.5px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut);font-weight:700;margin:12px 8px 6px}
.side .grp:first-child{margin-top:2px}
.side button{display:block;width:100%;text-align:left;border:1px solid transparent;background:none;padding:9px 11px;border-radius:8px;font-size:14px;font-weight:700;color:var(--mut);cursor:pointer;margin-bottom:3px}
.side button:hover{background:#f3f5f8;color:var(--ink)}
.side button.active{background:#fbf0f0;border-color:#e3b8b8;color:var(--accent)}
.side button .d{display:block;font-size:11px;font-weight:500;color:var(--mut);margin-top:2px;line-height:1.35}
.content{flex:1;min-width:0}
.panel{display:none}
.panel.on{display:block}
.pmain{max-width:1000px;margin:0 auto;padding:22px 30px 80px}
h2{font-size:20px;margin:8px 0 14px;padding-bottom:8px;border-bottom:2px solid var(--line)}
h3{font-size:16px;margin:22px 0 8px;color:var(--accent2)}
h4{font-size:14px;margin:14px 0 4px;color:var(--ink)}
p,li{color:#27313b}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:14px 0;box-shadow:0 1px 3px rgba(0,0,0,.03)}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.5px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:#eef2f7}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-size:13px}
.note{font-size:13px;color:var(--mut)}
.legend{font-size:12.5px;color:var(--mut);margin-top:6px}
/* framing */
.crux{border-left:5px solid var(--accent);background:#fff}
.crux .q{font-weight:600;font-size:17px;line-height:1.45;margin:6px 0}
.mermaid{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;margin:12px 0;text-align:center}
.chip{display:inline-block;font-size:11px;font-weight:700;padding:1px 8px;border-radius:10px;margin-right:4px}
.c-dec{background:#e3f3e9;color:var(--good)} .c-exo{background:#f6e0e0;color:var(--bad)} .c-st{background:#eef2f7;color:var(--accent2)} .c-out{background:#fdf0d8;color:var(--warn)} .c-con{background:#ece7f5;color:#5b3f8a}
.frame{background:#eef4ee;border:1px solid #bcd6c2;border-radius:8px;padding:14px 18px;margin:14px 0}
.axis{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:13px;background:#f4f7fb;border:1px solid var(--line);border-radius:8px;padding:12px 16px;white-space:pre;overflow-x:auto;color:#2b333c}
/* plan */
.rq{background:#fff;border-left:5px solid var(--accent)}
.rq .lbl{text-transform:uppercase;letter-spacing:.6px;font-size:11px;color:var(--accent);font-weight:700;margin-bottom:6px}
.rq .q{font-weight:600;font-size:18px;line-height:1.45}
.rq .precise{margin:12px 0 0;font-size:14.5px;color:#3a4654}
.tagA{color:var(--good);font-weight:700}.tagB{color:var(--accent2);font-weight:700}.tagC{color:var(--warn);font-weight:700}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;text-transform:uppercase;letter-spacing:.3px}
.pill.done{background:#e3f3e9;color:var(--good)}.pill.prog{background:#fdf0d8;color:var(--warn)}.pill.kill{background:#f6e0e0;color:var(--bad)}
.flag{background:#fdf0d8;border:1px solid #e9cd8f;border-radius:8px;padding:10px 14px;font-size:13.5px;margin:14px 0}
.limit{background:#f6e9e9;border:1px solid #e3b8b8;border-radius:8px;padding:12px 16px;font-size:13.5px;margin:14px 0}
.why{background:#eef4ee;border:1px solid #bcd6c2;border-radius:8px;padding:14px 18px;margin:14px 0;font-size:14px}
.ref{margin:10px 0;padding-left:24px;text-indent:-24px;border-radius:4px}
.verified{color:var(--good);font-weight:700;font-size:11px}
.pending{color:var(--warn);font-weight:700;font-size:11px}
.paywall{color:var(--bad);font-weight:700;font-size:11px}
.hyp{background:#fff;border-left:5px solid var(--accent2);padding:14px 18px;margin:12px 0;border-radius:0 8px 8px 0}
.hyp b{color:var(--accent2)}
.eqbox{background:#f4f7fb;border:1px solid var(--line);border-radius:8px;padding:6px 18px;margin:12px 0}
.prim{margin:14px 0}
.prim .t{font-weight:700;color:var(--accent2)}
sup.cite{font-size:10.5px;line-height:0}
sup.cite a{color:var(--accent2);text-decoration:none;font-weight:700;cursor:pointer;background:#eef2f7;padding:0 4px;border-radius:3px}
sup.cite a:hover{text-decoration:underline}
.hl{background:#fff3d6 !important;transition:background .3s}
.katex{white-space:nowrap}
.katex-display{margin:12px 0;overflow-x:auto;overflow-y:hidden}
.sponsor{background:#fbf6f6;border-left:5px solid var(--accent)}
.verb{margin:10px 0;padding:10px 16px;border-left:3px solid #d9b3b3;background:#fff;border-radius:0 6px 6px 0}
.verb p{margin:0 0 6px;font-style:italic;color:#2b333c}
.verb cite{font-style:normal;font-size:12px;color:var(--mut)}
.cross td:first-child{width:42%;font-style:italic;color:#3a2a2a}
.launch{background:#eef4f7;border:1px solid #b9d4df;border-radius:8px;padding:13px 16px;margin:14px 0;font-size:14px}
.launch b{color:var(--accent2)} .launch a{font-weight:700}
"""

HEAD = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],throwOnError:false});"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>window.addEventListener('load',function(){if(window.mermaid){mermaid.initialize({startOnLoad:false,theme:'base',themeVariables:{fontSize:'14px'},flowchart:{curve:'basis'}});renderMermaidIn('p-%s');}});</script>""" % FIRST

BODY = """<header>
  <h1>Forward Surgical Saturation under Large-Scale Combat Operations</h1>
  <div class="sub">A doctrine-grounded abandonment-queue study of the casualty-treatment cliff.</div>
  <div class="auth">Austin Semmel</div>
  <div class="meta">Origin: KSIL Q187 (The Army Strategy, High-Intensity Conflict) + SSE26 Q522 (Office of the Surgeon General G-33) · Target: <i>Military Operations Research</i></div>
</header>
<div class="app">
    %s
  <div class="content">
    %s
  </div>
</div>""" % (side, "\n    ".join(panels))

SHIM = """
/* ===== top-level panel switcher, citation jumps, deferred Mermaid ===== */
var PANELS=[%s];
function renderMermaidIn(panelId){
  if(!window.mermaid)return;
  var nodes=document.querySelectorAll('#'+panelId+' .mermaid:not([data-processed])');
  if(nodes.length){try{mermaid.run({nodes:nodes});}catch(e){console.warn(e);}}
}
function showPanel(name){
  PANELS.forEach(function(n){var el=document.getElementById('p-'+n);if(el)el.classList.toggle('on',n===name);});
  document.querySelectorAll('.side button').forEach(function(b){b.classList.toggle('active',b.dataset.p===name);});
  renderMermaidIn('p-'+name);
  if(name==='sim'){try{dim=fitCanvas(cv);CW=dim.w;CH=dim.h;dimK=fitCanvas(knee);drawKnee();if(typeof aimCamera==='function'){aimCamera();cam.cx=cam.tcx;cam.cy=cam.tcy;cam.s=cam.ts;}}catch(e){}}
  window.scrollTo(0,0);
}
function goCite(id){
  showPanel('refs');
  var el=document.getElementById(id);
  if(el){el.scrollIntoView({behavior:'smooth',block:'center'});el.classList.add('hl');setTimeout(function(){el.classList.remove('hl');},2200);}
  return false;
}
window.goCite=goCite;
showPanel('%s');
""" % (",".join("'%s'" % s[0] for s in SECTIONS), FIRST)

BANNER = "<!-- GENERATED by build_unified.py from sections/*.html + sim.html. Edit those sources and re-run; do not edit this file directly. -->\n"

html = ("<!DOCTYPE html>\n" + BANNER + '<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>Forward Surgical Saturation · Framing · Plan · Methods · Results · Discussion · Sim</title>\n"
        + HEAD + "\n<style>\n" + BASE + "\n/* === sim sandbox === */\n  " + sim_css +
        "\n</style>\n</head>\n<body>\n" + BODY +
        "\n<script>\n/* ===== SIM engine + animation (from sim.html) ===== */\n" + sim_script +
        "\n" + SHIM + "\n</script>\n</body>\n</html>\n")

open(os.path.join(D, "index.html"), "w", encoding="utf-8").write(html)
print("wrote index.html bytes:", len(html))
print("panels:", ", ".join(s[0] for s in SECTIONS))
