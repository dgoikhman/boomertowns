"""BoomerTowns — the Succession Index site builder.

Renders the full static site from data/mainstreet_cities.csv:
  /                      the Succession Index (ranked cities)
  /<city-slug>/          city succession pages
  /methodology/          how the Succession Score works
  404.html, sitemap.xml, robots.txt, llms.txt, favicon.svg, og/ share cards

Run: python site/build.py [--base-url https://boomertowns.com]
"""
import csv, json, os, sys, datetime
from jinja2 import Environment, DictLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine.scoring import compute  # noqa: E402

OUT = os.path.join(ROOT, "out")
BASE_URL = "https://dgoikhman.github.io/boomertowns"
STRIPE = os.environ.get("STRIPE_LINK_ANNUAL", "")
FORM_ENDPOINT = os.environ.get("FORM_ENDPOINT", "")
if "--base-url" in sys.argv:
    BASE_URL = sys.argv[sys.argv.index("--base-url") + 1].rstrip("/")
TODAY = datetime.date.today().strftime("%B %Y")
YEAR = datetime.date.today().year

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

BASE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>
<meta name="description" content="{{ description }}">
<link rel="canonical" href="{{ canonical }}">
<link rel="icon" href="{{ base }}/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{{ title }}"><meta property="og:description" content="{{ description }}">
<meta property="og:url" content="{{ canonical }}"><meta property="og:site_name" content="BoomerTowns">
{% if og_image %}<meta property="og:image" content="{{ og_image }}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{{ og_image }}">{% endif %}
{% for ld in jsonld %}<script type="application/ld+json">{{ ld }}</script>
{% endfor %}<style>
:root{--paper:#EDEBE4;--ink:#232019;--muted:#6E675A;--line:#D4CFC2;--accent:#8A5A2B;--deep:#3F5A36}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:"Avenir Next","Segoe UI",system-ui,sans-serif;line-height:1.55;font-variant-numeric:tabular-nums}
.wrap{max-width:760px;margin:0 auto;padding:20px 16px 60px}
header a{color:var(--ink);text-decoration:none;font-weight:700;letter-spacing:.03em;font-size:15px}
header span{color:var(--accent)}
.nav{font-size:13px;margin-top:6px;color:var(--muted)} .nav a{color:var(--muted);text-decoration:none;margin-right:10px}
h1{font-size:clamp(24px,5.5vw,34px);line-height:1.15;margin:14px 0 10px;max-width:26ch}
h2{font-size:19px;margin:26px 0 8px}
p{margin:10px 0;max-width:64ch}
.lede{font-size:16.5px} .lede b{color:var(--deep)}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600;font-size:13px}
td.n,th.n{text-align:right}
a{color:var(--deep)}
.chip{display:inline-block;min-width:2.2em;text-align:center;color:#fff;border-radius:4px;padding:1px 6px;font-weight:700}
.b-green{background:#3F5A36}.b-gold{background:#8A5A2B}.b-mid{background:#8B8578}.b-red{background:#9C4A34}
.scorebadge{float:right;margin:0 0 8px 12px;width:82px;height:82px;border-radius:50%;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:700}
.scorebadge .n{font-size:30px;line-height:1}.scorebadge .l{font-size:8px;letter-spacing:.08em;margin-top:3px}
.note{background:#F5F3EC;border:1px solid var(--line);border-radius:6px;padding:12px 14px;margin:14px 0;font-size:14px}
.meta{color:var(--muted);font-size:13px;border-top:1px solid var(--line);margin-top:26px;padding-top:12px}
nav.crumbs{font-size:13px;color:var(--muted);margin-top:8px}
.faq h3{font-size:15.5px;margin-top:14px}.faq p{margin:4px 0 14px}
.tcard{border:1px solid var(--line);border-left:3px solid var(--accent);background:#fff;border-radius:4px;padding:11px 12px;margin:10px 0}
.tcard .blurline{height:15px;width:58%;border-radius:3px;background:repeating-linear-gradient(90deg,#DAD5C8 0 22px,#CBC5B6 22px 44px);filter:blur(2.5px);margin:2px 0}
.tcard .mline{font-size:13px;color:var(--muted)} .tcard .p{font-size:15px;font-weight:700;margin:2px 0}
.unlock{border:2px solid var(--accent);border-radius:6px;background:#fff;padding:16px;margin:16px 0}
button{font:inherit;font-size:14px;font-weight:700;padding:11px 16px;border-radius:5px;cursor:pointer;border:1px solid var(--ink);background:var(--ink);color:var(--paper);min-height:44px}
.mapctl{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:10px 0;font-size:13px}
.mapctl select{font:inherit;font-size:13px;padding:5px;border:1px solid var(--line);border-radius:4px;background:#fff}
.srch{position:relative;margin-top:8px}.srch input{width:100%;max-width:340px;font:inherit;font-size:14px;padding:8px 10px;border:1px solid var(--line);border-radius:5px;background:#fff}
#qr{position:absolute;z-index:9;background:#fff;border:1px solid var(--line);border-radius:5px;max-width:340px;width:100%}
#qr a{display:block;padding:8px 10px;font-size:14px;text-decoration:none;color:var(--ink);border-bottom:1px solid var(--line)}#qr a:last-child{border-bottom:none}
.field input{font:inherit;font-size:14px;padding:9px;border:1px solid var(--line);border-radius:4px}
</style></head><body><div class="wrap">
<header><a href="{{ base }}/">BOOMER<span>TOWNS</span></a>
<div class="nav"><a href="{{ base }}/targets/"><b>Targets</b></a><a href="{{ base }}/">Succession Index</a><a href="{{ base }}/partners/">Partners</a><a href="{{ base }}/methodology/">Methodology</a></div>
<div class="srch"><input id="q" placeholder="Search towns &amp; verticals…" autocomplete="off"><div id="qr"></div></div></header>
<script>
var SIDX={{ sidx_json }};
(function(){var q=document.getElementById("q"),qr=document.getElementById("qr");
function render(){var s=q.value.toLowerCase().trim();if(!s){qr.innerHTML="";return;}
var hits=SIDX.filter(function(m){return m.n.toLowerCase().indexOf(s)>-1}).slice(0,8);
qr.innerHTML=hits.length?hits.map(function(m){return '<a href="{{ base }}'+m.u+'">'+m.n+'</a>'}).join(""):'<a>no match</a>';}
q.addEventListener("input",render);q.addEventListener("focus",render);
document.addEventListener("click",function(e){if(e.target&&e.target.closest&&!e.target.closest(".srch"))qr.innerHTML="";});})();
</script>
{{ body }}
<div class="meta"><p>Source: state Secretary of State public business registries (entity status and original filing dates), aggregated at city level. Scores describe registry data patterns, never any owner's intent. No individual businesses or owners are identified on public pages. Last reviewed {{ today }}. <a href="{{ base }}/methodology/">Methodology</a>.</p></div>
</div></body></html>"""

TARGETS = """
<nav class="crumbs"><a href="{{ base }}/">BoomerTowns</a> › Targets</nav>
<h1>Succession targets: the businesses most likely to sell next</h1>
<p class="lede">Individual long-tenured businesses surfaced from public registries and scored on succession signals — before they're listed anywhere. {% if targets %}Filter the feed below; <b>names and full profiles unlock with membership.</b>{% else %}The first classification sweep is running — the feed goes live when it lands. The city-level <a href="{{ base }}/">Succession Index</a> is open now.{% endif %}</p>
{% if targets %}<div class="mapctl">
<label>City <select id="t-c"><option value="">all</option></select></label>
<label>Vertical <select id="t-v"><option value="">all</option></select></label>
<label>Min age <select id="t-a"><option value="0">any</option><option value="20">20+ yrs</option><option value="30">30+ yrs</option><option value="40">40+ yrs</option></select></label>
</div>
<p class="quick" id="t-count"></p><div id="t-list"></div>
<div class="unlock"><b>Unlock the full target list — names, ages, filters, exports</b><br>
Every scored business statewide, vertical roll-up lists, and thesis alerts when new targets match your criteria. Founding members: <b>$490/yr locked for life</b> (first 20). Letter-first outreach tooling; permanent opt-out honored.<br>
<a href="{{ stripe or (base + '/methodology/') }}"><button style="margin-top:10px">Unlock BoomerTowns Pro</button></a></div>
<div class="note"><b>Save your thesis.</b> Tell us vertical × geography and get alerted as new targets qualify.
{% if form_endpoint %}<form action="{{ form_endpoint }}" method="POST" style="margin-top:8px"><input type="hidden" name="type" value="thesis"><input type="email" name="email" required placeholder="you@fund.com" style="width:44%"><input type="text" name="thesis" required placeholder="e.g. HVAC roll-up, Front Range CO" style="width:50%;margin-left:4px"><button type="submit" style="margin-top:8px">Save my thesis</button></form>
{% else %}<span style="color:var(--muted);font-size:13.5px"> Alert signups open shortly.</span>{% endif %}</div>
<script>
var T={{ targets_json }};
var C=[...new Set(T.map(t=>t.city))].sort(),V=[...new Set(T.map(t=>t.vertical))].sort();
document.getElementById("t-c").innerHTML+=C.map(c=>"<option>"+c+"</option>").join("");
document.getElementById("t-v").innerHTML+=V.map(v=>"<option>"+v+"</option>").join("");
function draw(){var c=document.getElementById("t-c").value,v=document.getElementById("t-v").value,a=+document.getElementById("t-a").value;
var f=T.filter(t=>(!c||t.city==c)&&(!v||t.vertical==v)&&t.age>=a);
document.getElementById("t-count").textContent=f.length+" locked targets match";
document.getElementById("t-list").innerHTML=f.slice(0,40).map(t=>
 '<div class="tcard">'+(t.boom?'<span style="float:right;color:#8A5A2B;font-weight:700">Boom Meter '+t.boom+' · '+t.band+'</span>':'')+'<div class="blurline"></div><div class="p">'+t.vertical.replace(/-/g," ")+' · ~'+t.age+' years in business</div>'+
 '<div class="mline">'+t.city+', CO · one of '+t.pool+' aged '+t.vertical.replace(/-/g," ")+' businesses here · typical independent revenue: '+t.rev_band+' (modeled, industry-level)</div>'+
 '<div class="mline">Name, exact age &amp; profile unlock with membership</div></div>').join("");}
["t-c","t-v","t-a"].forEach(i=>document.getElementById(i).addEventListener("change",draw));draw();
</script>{% endif %}
{% if radar %}<h2>The Roll-up Radar</h2>
<p>Fragmentation by city × vertical — the count of aged independents, i.e. roll-up raw material:</p>
<table><tr><th>City</th><th>Vertical</th><th class="n">Aged independents</th></tr>
{% for r in radar %}<tr><td>{{ r.city }}</td><td>{{ r.vertical }}</td><td class="n">{{ r.aged_independents }}</td></tr>
{% endfor %}</table>{% endif %}
<p class="quick">Sources: public registry filing dates; industry classification is model-scored with low-confidence entries excluded. Revenue bands are industry-typical modeled figures, never a claim about a specific business.</p>"""

PARTNERS = """
<nav class="crumbs"><a href="{{ base }}/">BoomerTowns</a> › Partners</nav>
<h1>Get featured where business buyers hunt</h1>
<p class="lede">Searchers and roll-up teams use BoomerTowns to find tomorrow's sellers. They need brokers with inventory, SBA lenders, and diligence pros. Apply below — founding partners lock founding terms.</p>
<h2 id="brokers">Brokers — free distribution for your listings</h2>
<p>Submit deals for listing on target pages (with permission and provenance) and receive matched buyer interest from your markets.</p>
{% if form_endpoint %}<form action="{{ form_endpoint }}" method="POST"><input type="hidden" name="partner_type" value="broker"><input type="email" name="email" required placeholder="you@brokerage.com" style="width:46%"><input type="text" name="market" required placeholder="Markets / verticals covered" style="width:48%;margin-left:4px"><button type="submit" style="margin-top:8px">Apply as a broker partner</button></form>{% else %}<div class="note">Applications open shortly.</div>{% endif %}
<h2 id="lenders">SBA &amp; acquisition lenders</h2>
<p>Buyers arrive with a target attached. Referrals route to matched lenders per-funded.</p>
{% if form_endpoint %}<form action="{{ form_endpoint }}" method="POST"><input type="hidden" name="partner_type" value="lender"><input type="email" name="email" required placeholder="you@lender.com" style="width:46%"><input type="text" name="market" required placeholder="States + products (SBA 7a, conventional…)" style="width:48%;margin-left:4px"><button type="submit" style="margin-top:8px">Apply as a lending partner</button></form>{% else %}<div class="note">Applications open shortly.</div>{% endif %}
<h2 id="diligence">QoE, legal &amp; diligence providers</h2>
<p>Every serious buyer needs quality-of-earnings and deal counsel; matched referrals by deal size and geography.</p>
{% if form_endpoint %}<form action="{{ form_endpoint }}" method="POST"><input type="hidden" name="partner_type" value="diligence"><input type="email" name="email" required placeholder="you@firm.com" style="width:46%"><input type="text" name="market" required placeholder="Services + typical deal size" style="width:48%;margin-left:4px"><button type="submit" style="margin-top:8px">Apply as a diligence partner</button></form>{% else %}<div class="note">Applications open shortly.</div>{% endif %}
<p class="quick">Partners are verified; investor and owner trust is the product.</p>"""

CITY = """
<nav class="crumbs"><a href="{{ base }}/">Succession Index</a> › {{ c.city }}</nav>
<div class="scorebadge {{ band }}"><span class="n">{{ score }}</span><span class="l">SUCCESSION</span></div>
<h1>{{ c.city }}, {{ c.state }}: business succession outlook ({{ year }})</h1>
<p class="lede">{{ "{:,}".format(c.total_active) }} active registered businesses operate in {{ c.city }}, and <b>{{ "{:,}".format(c.over20) }} — {{ c.share20 }}%</b> — have been registered for 20+ years, per Secretary of State records. {{ "{:,}".format(c.over30) }} ({{ c.share30 }}%) pass 30 years. Succession Score: <b>{{ score }}/100</b>, #{{ rank }} of {{ total }} cities tracked.</p>
<p>Long-tenured, founder-owned businesses are where ownership transitions concentrate as owners retire — the silver tsunami. A high score means a deep bench of aged businesses relative to the market: exactly where acquisition-minded buyers focus.</p>
<h2>The numbers</h2>
<table><tr><th>Metric</th><th class="n">Value</th></tr>
<tr><td>Active registered businesses</td><td class="n">{{ "{:,}".format(c.total_active) }}</td></tr>
<tr><td>Registered 20+ years</td><td class="n">{{ "{:,}".format(c.over20) }} ({{ c.share20 }}%)</td></tr>
<tr><td>Registered 30+ years</td><td class="n">{{ "{:,}".format(c.over30) }} ({{ c.share30 }}%)</td></tr>
<tr><td>Succession Score</td><td class="n">{{ score }}/100</td></tr></table>
<div class="note"><b>Own a business in {{ c.city }}?</b> This page shows only city-level registry aggregates — no individual businesses are named. Corrections and opt-outs will be honored permanently once business-level tools launch.</div>
<div class="faq"><h2>Frequently asked questions</h2>
<h3>What does {{ c.city }}'s Succession Score mean?</h3>
<p>A {{ score }}/100 means {{ c.city }}'s share of businesses aged 20+ years ({{ c.share20 }}%) ranks it #{{ rank }} of {{ total }} tracked cities — a measure of how concentrated the coming ownership handover is, from public filing dates.</p>
<h3>Where does this data come from?</h3>
<p>The state's public business registry: entity status and original filing dates, aggregated by city. Nothing here identifies an individual business or owner.</p>
</div>"""

INDEX = """
<h1>The businesses most likely to sell next — found before they're listed</h1>
<p class="lede">BoomerTowns maps the silver tsunami — long-tenured, founder-owned businesses approaching ownership transition. Launch state: Colorado. <b>{{ top.c.city }}</b> leads with {{ top.c.share20 }}% of {{ "{:,}".format(top.c.total_active) }} active businesses registered 20+ years (Succession Score {{ top.score }}/100), per Secretary of State records.</p>
{% if teaser %}<h2 style="margin-top:18px">Today's top succession targets</h2>
{% for t in teaser %}<div class="tcard">{% if t.boom %}<span style="float:right;color:var(--accent);font-weight:700">Boom Meter {{ t.boom }} · {{ t.band }}</span>{% endif %}<div class="blurline"></div><div class="p">{{ t.vertical.replace("-", " ") }} · ~{{ t.age }} years in business</div>
<div class="mline">{{ t.city }}, CO · typical independent revenue {{ t.rev_band }} (modeled)</div></div>
{% endfor %}<p class="quick"><b><a href="{{ base }}/targets/">See all targets — names unlock with membership →</a></b></p>{% endif %}
<h2>Explore the towns behind the targets</h2>
<table><tr><th>#</th><th>City</th><th class="n">Active</th><th class="n">20+ yrs</th><th class="n">Share</th><th class="n">Score</th></tr>
{% for r in rows %}<tr><td>{{ loop.index }}</td><td><a href="{{ base }}/{{ r.c.slug }}/">{{ r.c.city }}, {{ r.c.state }}</a></td><td class="n">{{ "{:,}".format(r.c.total_active) }}</td><td class="n">{{ "{:,}".format(r.c.over20) }}</td><td class="n">{{ r.c.share20 }}%</td><td class="n"><span class="chip {{ r.band }}">{{ r.score }}</span></td></tr>
{% endfor %}</table>
<h2>What's coming</h2>
<p>Business-level succession signals, vertical roll-up radars, and buyer tools are in build; more states follow Colorado. Brokers who want deals distributed here, and buyers with a thesis, can watch this space — the free Index stays free.</p>"""

METHOD = """
<h1>Succession Score methodology</h1>
<p class="lede">The Succession Score is a 0-100 city index of how concentrated the coming business-ownership handover is, computed from public registry filing dates: the share of active businesses registered 20+ years ago (45%), 30+ years (25%), and the absolute depth of aged businesses (30%).</p>
<h2>The Boom Meter</h2>
<p>Individual businesses carry a <b>Boom Meter</b> reading (0-100): how loudly the succession signals are ringing. v1 weighs tenure (45%), silver-wave industry (30%), and market fragmentation (25%); as verified-operator layers land (license boards, carrier registries, SBA history, digital-decay signals, owner-age context), weights rebalance per the published spec. Bands: Quiet, Building, Loud, <b>Boom</b>. As everywhere on this site: a reading describes registry-data patterns, never an owner's intent.</p>
<h2>Sources & limits</h2>
<p>State Secretary of State registries (currently Colorado). Registration age is a proxy for operating tenure — it can overstate (shelf entities) or understate (re-registrations) individual cases; at city scale these wash toward signal. Revenue figures, when they appear in future tools, are modeled bands from IRS Statistics of Income and Census County Business Patterns benchmarks — individual private-company revenue is not public data, from anyone.</p>
<h2>What it is not</h2>
<p>Not a claim about any owner's plans. Not a listing service. Scores describe registry data patterns; every future business-level tool ships with a claim, correction, and permanent opt-out flow.</p>"""

env = Environment(loader=DictLoader({"base": BASE, "city": CITY, "index": INDEX, "method": METHOD, "targets": TARGETS, "partners": PARTNERS}))


def _font(sz):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)
    except Exception:
        return ImageFont.load_default()


def make_og(fname, heading, stat, score=None, band=None):
    if not HAVE_PIL:
        return None
    os.makedirs(os.path.join(OUT, "og"), exist_ok=True)
    im = Image.new("RGB", (1200, 630), "#EDEBE4")
    d = ImageDraw.Draw(im)
    d.text((60, 48), "BOOMER", font=_font(38), fill="#232019")
    d.text((232, 48), "TOWNS", font=_font(38), fill="#8A5A2B")
    for i, line in enumerate(heading[:2]):
        d.text((60, 180 + i * 78), line, font=_font(62), fill="#232019")
    d.text((60, 388), stat, font=_font(32), fill="#6E675A")
    d.text((60, 540), "boomertowns.com", font=_font(30), fill="#3F5A36")
    if score is not None:
        colors = {"b-green": "#3F5A36", "b-gold": "#8A5A2B", "b-mid": "#8B8578", "b-red": "#9C4A34"}
        cx, cy, rr = 1010, 300, 130
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=colors.get(band, "#8A5A2B"))
        d.text((cx, cy - 26), str(score), font=_font(84), fill="#FFFFFF", anchor="mm")
        d.text((cx, cy + 52), "SUCCESSION", font=_font(20), fill="#FFFFFF", anchor="mm")
    im.save(os.path.join(OUT, "og", fname), "PNG", optimize=True)
    return f"{BASE_URL}/og/{fname}"


def page(path, title, description, body_html, jsonld=None, og_image=None):
    full = env.get_template("base").render(
        title=title, description=description, body=body_html, sidx_json=SIDX_JSON,
        canonical=f"{BASE_URL}{path}", base=BASE_URL, today=TODAY,
        og_image=og_image, jsonld=[json.dumps(x) for x in (jsonld or [])])
    d = os.path.join(OUT, path.strip("/")) if path != "/404.html" else OUT
    os.makedirs(d, exist_ok=True)
    fn = "404.html" if path == "/404.html" else "index.html"
    open(os.path.join(d, fn), "w").write(full)
    return path


TARGETS_DATA = []
SIDX_JSON = "[]"

def main():
    global TARGETS_DATA
    tp = os.path.join(ROOT, "data", "succession_targets.json")
    TARGETS_DATA = json.load(open(tp)) if os.path.exists(tp) else []
    raw = list(csv.DictReader(open(os.path.join(ROOT, "data", "mainstreet_cities.csv"))))
    rows = []
    for r in raw:
        c = dict(r)
        for k in ("total_active", "over20", "over30"):
            c[k] = int(c[k])
        for k in ("share20", "share30"):
            c[k] = float(c[k])
        sc, _ = compute("mainstreet", c)
        band = "b-green" if sc >= 70 else "b-gold" if sc >= 55 else "b-mid" if sc >= 40 else "b-red"
        rows.append({"c": type("C", (), c)(), "score": round(sc), "band": band})
    rows.sort(key=lambda x: -x["score"])
    urls = []

    for i, r in enumerate(rows):
        c = r["c"]
        og = make_og(f"{c.slug}.png", [f"{c.city}, {c.state}", "Succession Outlook"],
                     f"{c.share20}% of {c.total_active:,} businesses aged 20+ years",
                     r["score"], r["band"])
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question",
             "name": f"What does {c.city}'s Succession Score mean?",
             "acceptedAnswer": {"@type": "Answer",
                "text": f"{c.city} scores {r['score']}/100: {c.share20}% of its {c.total_active:,} active businesses have been registered 20+ years, per public registry data."}}]}
        body = env.get_template("city").render(c=c, score=r["score"], band=r["band"],
                                               rank=i + 1, total=len(rows),
                                               base=BASE_URL, year=YEAR)
        urls.append(page(f"/{c.slug}/",
                         f"{c.city}, {c.state} Business Succession Outlook {YEAR}: Succession Score {r['score']}",
                         f"{c.total_active:,} active businesses in {c.city}; {c.share20}% registered 20+ years. Succession Score {r['score']}/100 from public registry data.",
                         body, [faq_ld], og_image=og))

    global SIDX_JSON
    SIDX_JSON = json.dumps(
        [{"n": f"{r['c'].city}, {r['c'].state}", "u": f"/{r['c'].slug}/"} for r in rows]
        + [{"n": v.replace("-", " ") + " — succession targets", "u": "/targets/"} for v in
           sorted({t["vertical"] for t in TARGETS_DATA})]
        + [{"n": "Succession targets (all)", "u": "/targets/"},
           {"n": "The Succession Index", "u": "/"},
           {"n": "Partners — brokers, lenders, diligence", "u": "/partners/"}])
    tpath = os.path.join(ROOT, "data", "rollup_radar.csv")
    radar_rows = list(csv.DictReader(open(tpath)))[:25] if os.path.exists(tpath) else []
    urls.append(page("/targets/",
        "Succession Targets: Businesses Most Likely to Sell Next",
        "Long-tenured businesses surfaced from public registries and scored on succession signals — filterable by city, vertical and age. Names unlock with membership.",
        env.get_template("targets").render(base=BASE_URL, targets=bool(TARGETS_DATA),
            targets_json=json.dumps(TARGETS_DATA), radar=radar_rows,
            stripe=STRIPE, form_endpoint=FORM_ENDPOINT)))
    urls.append(page("/partners/", "Partner With BoomerTowns: Brokers, Lenders, Diligence",
        "Brokers, SBA lenders and diligence providers: apply to receive matched buyers from the succession-hunting audience.",
        env.get_template("partners").render(base=BASE_URL, form_endpoint=FORM_ENDPOINT)))
    top = rows[0]
    og_d = make_og("default.png", ["The Succession Index", ""],
                   f"Where America's business handover concentrates · {TODAY}", None, None)
    urls.append(page("/", f"BoomerTowns: The Succession Index ({YEAR})",
                     f"City-level map of long-tenured businesses approaching ownership transition. {top['c'].city} leads at {top['c'].share20}% aged 20+ years.",
                     env.get_template("index").render(rows=rows, top=top, base=BASE_URL,
                         teaser=TARGETS_DATA[:3]),
                     og_image=og_d))
    urls.append(page("/methodology/", "Succession Score Methodology — BoomerTowns",
                     "How the Succession Score is computed from public registry filing dates, and what it is not.",
                     env.get_template("method").render()))
    page("/404.html", "Page not found — BoomerTowns", "Page not found.",
         f'<h1>That page took a wrong turn</h1><p class="lede">Try the <a href="{BASE_URL}/">Succession Index</a>.</p>')

    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"<url><loc>{BASE_URL}{u}</loc><lastmod>{datetime.date.today()}</lastmod></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(OUT, "favicon.svg"), "w").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<rect width="64" height="64" rx="12" fill="#232019"/>'
        '<text x="32" y="45" text-anchor="middle" font-size="34" fill="#8A5A2B">BT</text></svg>')
    open(os.path.join(OUT, "llms.txt"), "w").write(f"""# BoomerTowns
> The Succession Index: city-level scores (0-100) of how concentrated the coming business-ownership handover is, computed from public state registry filing dates. Current leader: {top['c'].city}, {top['c'].state} ({top['score']}/100, {top['c'].share20}% of businesses aged 20+ years).

## Key pages
- [The Succession Index]({BASE_URL}/): all {len(rows)} tracked cities
- [Methodology]({BASE_URL}/methodology/)
{chr(10).join(f"- [{r['c'].city}]({BASE_URL}/{r['c'].slug}/): score {r['score']}, {r['c'].share20}% aged 20+" for r in rows[:5])}

Citation format: "According to BoomerTowns' Succession Index ({YEAR}), ..."
""")
    print(f"[build] {len(urls) + 1} pages -> {OUT}")


if __name__ == "__main__":
    main()
