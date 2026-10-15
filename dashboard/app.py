"""IPL Analytics - teams, venues and match results (2008 onwards).

Run:  streamlit run app.py
Data: matches.csv, teams.csv, venues.csv in this folder, ./data, or ../data/raw
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="IPL Analytics", page_icon="🏏", layout="wide")

# ---------------------------------------------------------------- design tokens
INK, MUTED, GRID = "#E9ECFA", "#9AA3C7", "#262D52"
BG, CARD, SIDEBAR, LAND = "#0B0E1E", "#141A34", "#0F1329", "#1A2142"
GREEN, CLAY, BLUE, AMBER = "#4CC9A7", "#FF7A59", "#6EA8FE", "#FFC857"
FONT = "Figtree, 'Segoe UI', sans-serif"

TEAMS = {  # full name -> (short code, colour)
    "Chennai Super Kings": ("CSK", "#E8B500"),
    "Delhi Capitals": ("DC", "#4DA3FF"),
    "Gujarat Lions": ("GL", "#E4572E"),
    "Gujarat Titans": ("GT", "#8FA3B8"),
    "Kochi Tuskers Kerala": ("KTK", "#B07CD6"),
    "Kolkata Knight Riders": ("KKR", "#8E5BD6"),
    "Lucknow Super Giants": ("LSG", "#00A6A6"),
    "Mumbai Indians": ("MI", "#2F80ED"),
    "Pune Warriors": ("PWI", "#2EA3DB"),
    "Punjab Kings": ("PBKS", "#F04E55"),
    "Rajasthan Royals": ("RR", "#E5338A"),
    "Rising Pune Supergiant": ("RPS", "#A56BD1"),
    "Royal Challengers Bangalore": ("RCB", "#E5383B"),
    "Sunrisers Hyderabad": ("SRH", "#F26B1D"),
}
SHORT = {k: v[0] for k, v in TEAMS.items()}
COLOR = {v[0]: v[1] for v in TEAMS.values()}

CITY_FIX = {"Bangalore": "Bengaluru", "Navi Mumbai": "Mumbai", "Chandigarh": "Mohali"}
UAE = {"Abu Dhabi", "Dubai", "Sharjah"}
SOUTH_AFRICA = {"Bloemfontein", "Cape Town", "Centurion", "Durban", "East London",
                "Johannesburg", "Kimberley", "Port Elizabeth"}
COORDS = {
    "Abu Dhabi": (24.47, 54.37), "Ahmedabad": (23.02, 72.57), "Bengaluru": (12.97, 77.59),
    "Bloemfontein": (-29.12, 26.21), "Cape Town": (-33.92, 18.42), "Centurion": (-25.86, 28.19),
    "Chennai": (13.08, 80.27), "Cuttack": (20.46, 85.88), "Delhi": (28.61, 77.21),
    "Dharamsala": (32.22, 76.32), "Dubai": (25.20, 55.27), "Durban": (-29.86, 31.02),
    "East London": (-33.02, 27.91), "Guwahati": (26.14, 91.74), "Hyderabad": (17.39, 78.49),
    "Indore": (22.72, 75.86), "Jaipur": (26.91, 75.79), "Johannesburg": (-26.20, 28.04),
    "Kanpur": (26.45, 80.33), "Kimberley": (-28.74, 24.77), "Kochi": (9.93, 76.27),
    "Kolkata": (22.57, 88.36), "Lucknow": (26.85, 80.95), "Mohali": (30.69, 76.74),
    "Mumbai": (19.08, 72.88), "Nagpur": (21.15, 79.09), "New Chandigarh": (30.80, 76.70),
    "Port Elizabeth": (-33.96, 25.60), "Pune": (18.52, 73.86), "Raipur": (21.25, 81.63),
    "Rajkot": (22.30, 70.80), "Ranchi": (23.34, 85.31), "Sharjah": (25.35, 55.40),
    "Visakhapatnam": (17.69, 83.22),
}
VENUE_ALIAS = {
    "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "Feroz Shah Kotla": "Arun Jaitley Stadium",
    "Sardar Patel Stadium": "Narendra Modi Stadium",
    "Punjab Cricket Association Stadium": "Punjab Cricket Association IS Bindra Stadium",
    "Zayed Cricket Stadium": "Sheikh Zayed Stadium",
    "Rajiv Gandhi International Stadium": "Rajiv Gandhi International Stadium",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {{ font-family: {FONT}; }}
.stApp {{ color: {INK}; }}
h1, h2, h3, h4 {{ font-family: 'Bricolage Grotesque', {FONT}; letter-spacing: -0.01em; color: {INK}; }}
.block-container {{ padding-top: 2.2rem; max-width: 1400px; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] {{ background: {SIDEBAR}; border-right: 1px solid {GRID}; }}
.masthead h1 {{ font-size: 2.6rem; font-weight: 800; margin: 0; line-height: 1.05; }}
.masthead p {{ color: {MUTED}; margin: .35rem 0 0; font-size: 1.02rem; }}
.kpi {{ background: {CARD}; border: 1px solid {GRID}; border-left: 5px solid {AMBER};
        border-radius: 6px; padding: .8rem 1rem; height: 100%; color: {INK}; }}
.kpi .v {{ font-family: 'Bricolage Grotesque', {FONT}; font-size: 2rem; font-weight: 800; line-height: 1.1; }}
.kpi .l {{ color: {MUTED}; font-size: .88rem; }}
.kpi .s {{ color: {MUTED}; font-size: .78rem; margin-top: .1rem; }}
.insight {{ background: {CARD}; border: 1px solid {GRID}; border-radius: 6px; padding: .7rem 1rem;
            margin: .4rem 0 1rem; font-size: .95rem; color: {INK}; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {GRID}; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; padding: .6rem 1rem; }}
.stTabs [aria-selected="true"] {{ color: {AMBER}; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: {AMBER}; }}

/* ===== cricket motif + motion ===== */
.stApp {{ background-color: {BG}; background-image: radial-gradient(520px 340px at 12% -4%, rgba(255,200,87,.14), transparent 70%), radial-gradient(520px 340px at 88% -4%, rgba(110,168,254,.12), transparent 70%), url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 1000' fill='none' stroke='rgba(233,236,250,0.06)'><circle cx='500' cy='500' r='470' stroke-width='3'/><circle cx='500' cy='500' r='452' stroke-width='1'/><circle cx='500' cy='500' r='290' stroke-width='2' stroke-dasharray='10 14'/><rect x='470' y='385' width='60' height='230' stroke-width='2'/><line x1='462' y1='405' x2='538' y2='405' stroke-width='2'/><line x1='462' y1='595' x2='538' y2='595' stroke-width='2'/></svg>"); background-repeat: no-repeat; background-position: 0 0, 0 0, center 55%; background-size: auto, auto, 1300px; background-attachment: fixed; }}

/* masthead */
.masthead {{ position: relative; display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 0; padding-bottom: 1rem; margin-bottom: .9rem; }}
.masthead::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 3px;
  background: repeating-linear-gradient(90deg, {AMBER} 0 12px, transparent 12px 19px);
  background-size: 19px 3px; animation: stitch 1.4s linear infinite; opacity: .9; }}
@keyframes stitch {{ to {{ background-position: 19px 0; }} }}
.mh-text {{ position: relative; z-index: 1; }}
.scene {{ position: relative; width: 270px; height: 86px; flex: none; margin-bottom: 4px; }}
.scene .ground {{ position: absolute; left: 0; right: 8px; bottom: 18px; height: 2px;
  background: repeating-linear-gradient(90deg, {GRID} 0 6px, transparent 6px 12px); }}
.scene .stumps {{ position: absolute; right: 14px; bottom: 18px; width: 22px; height: 38px; }}
.scene .stumps i {{ position: absolute; bottom: 0; width: 4px; height: 38px; background: {INK}; border-radius: 1px; opacity: .9; }}
.scene .stumps i:nth-child(1) {{ left: 0; }} .scene .stumps i:nth-child(2) {{ left: 9px; }} .scene .stumps i:nth-child(3) {{ left: 18px; }}
.scene .bail {{ position: absolute; top: -3px; width: 10px; height: 3px; background: {AMBER}; border-radius: 1px; animation: bails 4.2s ease-out infinite; }}
.scene .b1 {{ left: 0; }} .scene .b2 {{ left: 11px; animation-name: bails2; }}
@keyframes bails {{ 0%, 69% {{ transform: none; opacity: 1; }} 80% {{ transform: translate(-10px,-22px) rotate(-50deg); opacity: 1; }} 94%, 100% {{ transform: translate(-22px,-4px) rotate(-120deg); opacity: 0; }} }}
@keyframes bails2 {{ 0%, 69% {{ transform: none; opacity: 1; }} 80% {{ transform: translate(8px,-26px) rotate(40deg); opacity: 1; }} 94%, 100% {{ transform: translate(20px,-6px) rotate(110deg); opacity: 0; }} }}
.scene .travel {{ position: absolute; left: 4px; bottom: 18px; width: 0; height: 0; animation: travel 4.2s linear infinite; }}
.scene .bounce {{ animation: bounce 4.2s infinite; }}
@keyframes travel {{ 0% {{ transform: translateX(0); opacity: 1; }} 68% {{ transform: translateX(212px); opacity: 1; }} 69%, 100% {{ transform: translateX(212px); opacity: 0; }} }}
@keyframes bounce {{ 0% {{ transform: translateY(-38px); animation-timing-function: ease-in; }}
  36% {{ transform: translateY(0); animation-timing-function: ease-out; }} 68% {{ transform: translateY(-17px); }} 100% {{ transform: translateY(-17px); }} }}
.ball {{ position: relative; width: 15px; height: 15px; margin: -15px 0 0 -7px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #ff9b85, #d63a1f 55%, #8a1f0d); box-shadow: 0 0 12px rgba(255,122,89,.55);
  animation: ballspin .7s linear infinite; }}
.ball::before {{ content: ""; position: absolute; inset: 1px 4px; border-radius: 50%;
  border-left: 1.5px dashed rgba(255,255,255,.85); border-right: 1.5px dashed rgba(255,255,255,.85); }}
@keyframes ballspin {{ to {{ transform: rotate(360deg); }} }}
.brand {{ display: flex; align-items: center; gap: .55rem; font-family: 'Bricolage Grotesque', {FONT};
  font-size: 1.35rem; font-weight: 800; margin: .2rem 0 .6rem; }}
.brand .ball {{ margin: 0; animation-duration: 5s; width: 20px; height: 20px; }}
.brand .ball::before {{ inset: 1px 6px; }}

/* latest-results ticker */
.ticker {{ display: flex; align-items: stretch; background: {CARD}; border: 1px solid {GRID}; border-radius: 6px;
  overflow: hidden; margin-bottom: 1rem; font-size: .88rem; }}
.tk-label {{ display: flex; align-items: center; gap: .5rem; padding: .5rem .9rem; background: {AMBER}; color: #1B1500;
  font-weight: 700; white-space: nowrap; }}
.tk-label .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #C8321A; animation: pulse 1.6s ease-out infinite; }}
@keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(200,50,26,.7); }} 100% {{ box-shadow: 0 0 0 9px rgba(200,50,26,0); }} }}
.tk-track {{ flex: 1; overflow: hidden; display: flex; align-items: center;
  mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent); -webkit-mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent); }}
.tk-move {{ display: inline-flex; white-space: nowrap; animation: marquee 70s linear infinite; }}
.ticker:hover .tk-move {{ animation-play-state: paused; }}
.tk {{ padding: 0 1.4rem; color: {INK}; }} .tk b {{ font-weight: 700; }} .tk i {{ color: {MUTED}; font-style: normal; margin-left: .5rem; }}
.tk::after {{ content: "\2022"; color: {GRID}; margin-left: 1.4rem; }}
@keyframes marquee {{ to {{ transform: translateX(-50%); }} }}

/* cards */
.kpi {{ transition: transform .25s ease, box-shadow .25s ease; animation: rise .7s cubic-bezier(.2,.7,.2,1) both; }}
.kpi:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(255,200,87,.12); }}
[data-testid="stColumn"]:nth-child(2) .kpi {{ animation-delay: .08s; }} [data-testid="stColumn"]:nth-child(3) .kpi {{ animation-delay: .16s; }}
[data-testid="stColumn"]:nth-child(4) .kpi {{ animation-delay: .24s; }} [data-testid="stColumn"]:nth-child(5) .kpi {{ animation-delay: .32s; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
@media (max-width: 900px) {{ .scene {{ display: none; }} }}
@media (prefers-reduced-motion: reduce) {{ .masthead::after, .scene *, .ball, .tk-move, .tk-label .dot, .kpi {{ animation: none !important; }} }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- data
@st.cache_data
def load_data() -> pd.DataFrame:
    here = Path(__file__).resolve().parent
    for d in (here, here / "data", here.parent / "data" / "raw", here.parent / "data"):
        if (d / "matches.csv").exists():
            m = pd.read_csv(d / "matches.csv")
            break
    else:
        st.error("matches.csv not found. Put it next to app.py or in a `data/` folder.")
        st.stop()

    m["match_date"] = pd.to_datetime(m["match_date"])
    m["season"] = m["match_date"].dt.year.astype(int)  # '2020/21' -> 2020 (played in UAE)

    # venues: merge renamed / duplicated grounds
    base = m["venue"].str.split(",").str[0].str.strip()
    m["venue"] = base.replace(VENUE_ALIAS)
    m["city"] = m["city"].replace(CITY_FIX)
    city_by_venue = m.dropna(subset=["city"]).groupby("venue")["city"].agg(lambda s: s.mode().iat[0])
    m["city"] = m["city"].fillna(m["venue"].map(city_by_venue))
    m["city"] = m["venue"].map(city_by_venue).fillna(m["city"])  # one city per ground
    m["region"] = m["city"].map(lambda c: "UAE" if c in UAE else "South Africa" if c in SOUTH_AFRICA else "India")

    for c in ("team1", "team2", "toss_winner", "match_winner"):
        m[c + "_s"] = m[c].map(SHORT)

    # result handling: no-result matches carry a stray winner -> blank it
    m["decided"] = m["result"].isin(["win", "tie"]) & m["match_winner"].notna()
    m.loc[~m["decided"], ["match_winner", "match_winner_s"]] = None
    m["super_over"] = m["result"].eq("tie")
    m["stage"] = m["match_number"].isna().map({True: "Playoff", False: "League"})

    # batting order: toss winner bats first if they chose bat, else the other side
    other = m["team1"].where(m["toss_winner"].eq(m["team2"]), m["team2"])
    m["bat_first"] = m["toss_winner"].where(m["toss_decision"].eq("bat"), other)
    m["bat_first_s"] = m["bat_first"].map(SHORT)
    m["bat_first_won"] = (m["bat_first"] == m["match_winner"]).where(m["decided"])
    m["toss_winner_won"] = (m["toss_winner"] == m["match_winner"]).where(m["decided"])
    m["margin_type"] = m["win_by_runs"].notna().map({True: "runs", False: "wickets"}).where(m["result"].eq("win"))
    return m.sort_values("match_date").reset_index(drop=True)


@st.cache_data
def champions(m: pd.DataFrame) -> pd.DataFrame:
    po = m[m["stage"].eq("Playoff") & m["decided"]]
    final = po.sort_values("match_date").groupby("season").tail(1)
    return final[["season", "match_winner", "match_winner_s", "team1_s", "team2_s"]].set_index("season")


def long_form(m: pd.DataFrame) -> pd.DataFrame:
    """One row per team per match."""
    a = m.assign(team=m["team1"], team_s=m["team1_s"], opp=m["team2_s"])
    b = m.assign(team=m["team2"], team_s=m["team2_s"], opp=m["team1_s"])
    t = pd.concat([a, b], ignore_index=True)
    t["won"] = (t["team"] == t["match_winner"]).where(t["decided"])
    t["batted_first"] = t["team"] == t["bat_first"]
    t["won_toss"] = t["team"] == t["toss_winner"]
    return t


def layout(fig, h=380, legend=True):
    fig.update_layout(
        height=h, margin=dict(l=10, r=10, t=30, b=10), font=dict(family=FONT, color=INK, size=13),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=legend,
        legend=dict(orientation="h", y=1.12, x=0, title=None), hoverlabel=dict(font_family=FONT),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    return fig


def chart(fig, **kw):
    st.plotly_chart(layout(fig, **kw), width="stretch", config={"displaylogo": False})


def kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="v">{value}</div><div class="l">{label}</div>'
                 f'<div class="s">{sub}</div></div>', unsafe_allow_html=True)


def pct(x):
    return f"{x:.0%}" if pd.notna(x) else "-"


def note(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- filters
M = load_data()
CH = champions(M)
years = sorted(M["season"].unique())

with st.sidebar:
    st.markdown('<div class="brand"><span class="ball"></span>Filters</div>', unsafe_allow_html=True)
    yr = st.slider("Seasons", years[0], years[-1], (years[0], years[-1]))
    regions = st.multiselect("Host region", ["India", "UAE", "South Africa"],
                             default=["India", "UAE", "South Africa"])
    stage = st.radio("Stage", ["All matches", "League only", "Playoffs only"], horizontal=False)
    all_teams = sorted(set(M["team1"]) | set(M["team2"]), key=lambda t: SHORT[t])
    focus = st.multiselect("Teams (matches involving)", all_teams, format_func=lambda t: f"{SHORT[t]} · {t}",
                           placeholder="All teams")
    st.caption("2026 is a partial season (data up to 1 May 2026). No-result matches are excluded "
               "from win statistics. Super-over wins count as wins.")

F = M[M["season"].between(*yr) & M["region"].isin(regions)]
if stage != "All matches":
    F = F[F["stage"].eq("League" if stage.startswith("League") else "Playoff")]
if focus:
    F = F[F["team1"].isin(focus) | F["team2"].isin(focus)]
if F.empty:
    st.warning("No matches fit these filters. Widen the season range, region or team selection.")
    st.stop()

T = long_form(F)
if focus:
    T = T[T["team"].isin(focus)]
D = F[F["decided"]]

# ---------------------------------------------------------------- masthead + KPIs
st.markdown(f"""<div class="masthead"><div class="mh-text"><h1>IPL Analytics</h1>
<p>Team form, ground behaviour and toss effects across {F['season'].nunique()} seasons
({yr[0]}–{yr[1]}), {len(F):,} matches.</p></div>
<div class="scene" aria-hidden="true"><div class="ground"></div><div class="stumps"><i></i><i></i><i></i><b class="bail b1"></b><b class="bail b2"></b></div><div class="travel"><div class="bounce"><div class="ball"></div></div></div></div></div>""", unsafe_allow_html=True)

def _ticker(m: pd.DataFrame) -> str:
    items = []
    for r in m[m["decided"]].tail(12).iloc[::-1].itertuples():
        w = r.match_winner_s
        l = r.team1_s if w == r.team2_s else r.team2_s
        how = (f"by {int(r.win_by_runs)} runs" if pd.notna(r.win_by_runs)
               else f"by {int(r.win_by_wickets)} wkts" if pd.notna(r.win_by_wickets) else "in a super over")
        d = f"{r.match_date.day} {r.match_date:%b %Y}"
        items.append(f'<span class="tk"><b style="color:{COLOR[w]}">{w}</b> beat {l} {how}<i>{d}</i></span>')
    row = "".join(items)
    return (f'<div class="ticker"><div class="tk-label"><span class="dot"></span>Latest results</div>'
            f'<div class="tk-track"><div class="tk-move">{row}{row}</div></div></div>')

st.markdown(_ticker(M), unsafe_allow_html=True)

k = st.columns(5)
kpi(k[0], "Matches", f"{len(F):,}", f"{F['stage'].eq('Playoff').sum()} playoffs")
kpi(k[1], "Teams / grounds", f"{T['team'].nunique()} / {F['venue'].nunique()}", f"{F['city'].nunique()} cities")
kpi(k[2], "Chasing side wins", pct(1 - D["bat_first_won"].mean()), f"bat-first win {pct(D['bat_first_won'].mean())}")
kpi(k[3], "Toss winner wins", pct(D["toss_winner_won"].mean()), "of decided matches")
kpi(k[4], "Chose to field", pct(F["toss_decision"].eq("field").mean()), "of all toss winners")
st.write("")

tab_ov, tab_team, tab_ven, tab_h2h, tab_toss, tab_exp = st.tabs(
    ["Overview", "Teams", "Venues", "Head to head", "Toss & chasing", "Match explorer"])

# ================================================================ OVERVIEW
with tab_ov:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Matches per season")
        s = F.groupby(["season", "region"]).size().reset_index(name="matches")
        fig = px.bar(s, x="season", y="matches", color="region",
                     color_discrete_map={"India": GREEN, "UAE": CLAY, "South Africa": BLUE})
        fig.update_xaxes(dtick=1, title=None); fig.update_yaxes(title=None)
        chart(fig)
    with c2:
        st.subheader("Do chasing sides win more often?")
        w = D.groupby("season")["bat_first_won"].mean().reset_index()
        w["Chasing"] = 1 - w["bat_first_won"]
        w = w.rename(columns={"bat_first_won": "Batting first"})
        fig = px.line(w.melt("season", var_name="side", value_name="win %"), x="season", y="win %",
                      color="side", markers=True, color_discrete_map={"Batting first": CLAY, "Chasing": GREEN})
        fig.add_hline(y=0.5, line_dash="dot", line_color=MUTED)
        fig.update_yaxes(tickformat=".0%", range=[0.3, 0.7], title=None); fig.update_xaxes(dtick=1, title=None)
        chart(fig)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Toss decision by season")
        td = F.groupby(["season", "toss_decision"]).size().reset_index(name="n")
        td["share"] = td["n"] / td.groupby("season")["n"].transform("sum")
        td["toss_decision"] = td["toss_decision"].map({"field": "Field first", "bat": "Bat first"})
        fig = px.bar(td, x="season", y="share", color="toss_decision",
                     color_discrete_map={"Field first": GREEN, "Bat first": CLAY})
        fig.update_yaxes(tickformat=".0%", title=None); fig.update_xaxes(dtick=1, title=None)
        chart(fig)
    with c4:
        st.subheader("Most wins")
        wins = T[T["won"] == True].groupby("team_s").size().sort_values().reset_index(name="wins")
        fig = px.bar(wins, y="team_s", x="wins", orientation="h", text="wins", color="team_s",
                     color_discrete_map=COLOR)
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(title=None); fig.update_xaxes(title=None)
        chart(fig, legend=False)

    st.subheader("Champions")
    ch = CH[CH.index.isin(F["season"].unique())]
    if ch.empty:
        st.caption("No completed seasons in the current selection.")
    else:
        cc = ch.reset_index().rename(columns={"match_winner": "Champion", "season": "Season"})
        counts = cc.groupby("Champion").size().sort_values(ascending=False)
        cols = st.columns(min(len(counts), 6))
        for i, (team, n) in enumerate(counts.head(6).items()):
            cols[i].markdown(
                f'<div class="kpi" style="border-left-color:{COLOR[SHORT[team]]}"><div class="v">{n}</div>'
                f'<div class="l">{team}</div><div class="s">{", ".join(map(str, cc[cc.Champion == team].Season))}</div></div>',
                unsafe_allow_html=True)
        st.caption("Champion = winner of the last match of each completed season. "
                   "Titles are not affected by the team filter.")

# ================================================================ TEAMS
with tab_team:
    rec = T.groupby("team_s").agg(
        Matches=("decided", "size"), Wins=("won", lambda s: int((s == True).sum())),
        Losses=("won", lambda s: int((s == False).sum())),
        Toss_won=("won_toss", "mean"),
    )
    dt = T[T["decided"]]
    rec["Win %"] = rec["Wins"] / (rec["Wins"] + rec["Losses"])
    rec["Win % batting first"] = dt[dt["batted_first"]].groupby("team_s")["won"].mean()
    rec["Win % chasing"] = dt[~dt["batted_first"]].groupby("team_s")["won"].mean()
    rec["Titles"] = CH[CH.index.isin(F["season"].unique())].groupby("match_winner_s").size()
    rec["Titles"] = rec["Titles"].fillna(0).astype(int)
    rec = rec.sort_values("Win %", ascending=False)

    a, b = st.columns([1.1, 1])
    with a:
        st.subheader("Win percentage")
        r = rec.reset_index().sort_values("Win %")
        fig = px.bar(r, y="team_s", x="Win %", orientation="h", color="team_s", color_discrete_map=COLOR,
                     text=r["Win %"].map(pct), hover_data=["Matches", "Wins", "Losses"])
        fig.add_vline(x=0.5, line_dash="dot", line_color=MUTED)
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(tickformat=".0%", range=[0, 0.8], title=None); fig.update_yaxes(title=None)
        chart(fig, h=470, legend=False)
    with b:
        st.subheader("Batting first vs chasing")
        r = rec.reset_index().melt("team_s", ["Win % batting first", "Win % chasing"], "mode", "win")
        r["mode"] = r["mode"].str.replace("Win % ", "").str.capitalize()
        fig = px.bar(r, x="team_s", y="win", color="mode", barmode="group",
                     color_discrete_map={"Batting first": CLAY, "Chasing": GREEN})
        fig.add_hline(y=0.5, line_dash="dot", line_color=MUTED)
        fig.update_yaxes(tickformat=".0%", title=None); fig.update_xaxes(title=None)
        chart(fig, h=470)

    st.subheader("Team record")
    show = rec.reset_index().rename(columns={"team_s": "Team", "Toss_won": "Toss won %"})
    show.insert(1, "Franchise", show["Team"].map({v: k for k, v in SHORT.items()}))
    st.dataframe(show[["Team", "Franchise", "Matches", "Wins", "Losses", "Win %", "Win % batting first",
                       "Win % chasing", "Toss won %", "Titles"]], hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(c, format="percent")
                                for c in ["Win %", "Win % batting first", "Win % chasing", "Toss won %"]})

    st.subheader("Team profile")
    team = st.selectbox("Pick a team", list(rec.index), format_func=lambda t: f"{t} · {dict((v, k) for k, v in SHORT.items())[t]}")
    tt = T[(T["team_s"] == team) & T["decided"]]
    p1, p2 = st.columns(2)
    with p1:
        yearly = tt.groupby("season").agg(wins=("won", "sum"), played=("won", "size")).reset_index()
        yearly["losses"] = yearly["played"] - yearly["wins"]
        fig = go.Figure([go.Bar(x=yearly["season"], y=yearly["wins"], name="Wins", marker_color=COLOR[team]),
                         go.Bar(x=yearly["season"], y=yearly["losses"], name="Losses", marker_color=GRID)])
        fig.update_layout(barmode="stack", title=f"{team}: wins and losses by season")
        fig.update_xaxes(dtick=1)
        chart(fig, h=340)
    with p2:
        gv = tt.groupby("venue").agg(played=("won", "size"), wins=("won", "sum")).query("played >= 3")
        gv["win"] = gv["wins"] / gv["played"]
        gv = gv.sort_values("win").tail(10).reset_index()
        fig = px.bar(gv, y="venue", x="win", orientation="h", text=gv["win"].map(pct),
                     hover_data=["played"], title=f"{team}: best grounds (min. 3 matches)")
        fig.update_traces(marker_color=COLOR[team], textposition="outside", cliponaxis=False)
        fig.update_xaxes(tickformat=".0%", range=[0, 1.1], title=None); fig.update_yaxes(title=None)
        chart(fig, h=340, legend=False)

# ================================================================ VENUES
with tab_ven:
    ven = F.groupby(["venue", "city", "region"]).agg(
        Matches=("match_id", "size"), first=("season", "min"), last=("season", "max"),
        bat_first_win=("bat_first_won", "mean"),
        toss_field=("toss_decision", lambda s: (s ==
        
         "field").mean()),
        avg_runs_margin=("win_by_runs", "mean"), avg_wkts_margin=("win_by_wickets", "mean"),
    ).reset_index()
    ven["chase_win"] = 1 - ven["bat_first_win"]

    a, b = st.columns([1, 1.1])
    with a:
        st.subheader("Busiest grounds")
        top = ven.sort_values("Matches").tail(12)
        fig = px.bar(top, y="venue", x="Matches", orientation="h", text="Matches", color="region",
                     color_discrete_map={"India": GREEN, "UAE": CLAY, "South Africa": BLUE})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(title=None); fig.update_xaxes(title=None)
        chart(fig, h=440)
    with b:
        st.subheader("Where matches were played")
        cm = F.groupby("city").size().reset_index(name="matches")
        cm["lat"] = cm["city"].map(lambda c: COORDS.get(c, (None, None))[0])
        cm["lon"] = cm["city"].map(lambda c: COORDS.get(c, (None, None))[1])
        fig = px.scatter_geo(cm.dropna(), lat="lat", lon="lon", size="matches", hover_name="city",
                             size_max=34, color_discrete_sequence=[GREEN])
        fig.update_geos(showcountries=True, countrycolor=GRID, showland=True, landcolor=LAND,
                        showocean=True, oceancolor=BG, showframe=False, projection_type="natural earth",
                        lataxis_range=[-38, 38], lonaxis_range=[10, 100])
        fig.update_traces(marker=dict(opacity=.7, line=dict(color="white", width=1)))
        chart(fig, h=440, legend=False)

    st.subheader("Batting first or chasing: which works at each ground?")
    sel = ven[ven["Matches"] >= 10].sort_values("chase_win")
    fig = go.Figure(go.Bar(y=sel["venue"], x=sel["chase_win"] - 0.5, base=0.5, orientation="h",
                           marker_color=[GREEN if v > .5 else CLAY for v in sel["chase_win"]],
                           customdata=sel[["Matches", "chase_win"]],
                           hovertemplate="%{y}<br>Chasing wins %{customdata[1]:.0%} of %{customdata[0]} matches<extra></extra>"))
    fig.add_vline(x=0.5, line_color=INK)
    fig.update_xaxes(tickformat=".0%", range=[0.25, 0.75], title="Chasing side's win %  (green = favours chasing, orange = favours batting first)")
    fig.update_yaxes(title=None)
    chart(fig, h=max(320, 26 * len(sel) + 80), legend=False)
    st.caption("Grounds with at least 10 matches in the current selection.")

    st.subheader("Venue profile")
    vsel = st.selectbox("Pick a ground", ven.sort_values("Matches", ascending=False)["venue"])
    vm = F[F["venue"] == vsel]
    vd = vm[vm["decided"]]
    r0 = ven[ven["venue"] == vsel].iloc[0]
    kk = st.columns(4)
    kpi(kk[0], "Matches", int(r0["Matches"]), f"{r0['city']} · {int(r0['first'])}–{int(r0['last'])}")
    kpi(kk[1], "Chasing side wins", pct(1 - vd["bat_first_won"].mean()), f"{len(vd)} decided")
    kpi(kk[2], "Toss winners chose to field", pct(r0["toss_field"]), "")
    kpi(kk[3], "Typical winning margin",
        f"{vd['win_by_runs'].median():.0f} runs" if vd["win_by_runs"].notna().any() else "-",
        f"{vd['win_by_wickets'].median():.0f} wkts when chasing" if vd["win_by_wickets"].notna().any() else "")
    st.write("")
    v1, v2 = st.columns(2)
    with v1:
        vt = long_form(vm)
        vt = vt[vt["decided"]].groupby("team_s").agg(played=("won", "size"), wins=("won", "sum"))
        vt = vt[vt["played"] >= 3].assign(win=lambda d: d["wins"] / d["played"]).sort_values("win").reset_index()
        fig = px.bar(vt, y="team_s", x="win", orientation="h", color="team_s", color_discrete_map=COLOR,
                     text=vt["win"].map(pct), hover_data=["played"], title="Team win % here (min. 3 matches)")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(tickformat=".0%", range=[0, 1.1], title=None); fig.update_yaxes(title=None)
        chart(fig, h=340, legend=False)
    with v2:
        sc = vm.groupby("season").size().reset_index(name="matches")
        fig = px.bar(sc, x="season", y="matches", title="Matches hosted by season")
        fig.update_traces(marker_color=GREEN); fig.update_xaxes(dtick=1, title=None); fig.update_yaxes(title=None)
        chart(fig, h=340, legend=False)

# ================================================================ HEAD TO HEAD
with tab_h2h:
    st.subheader("Rivalry matrix")
    st.caption("Row team's win % against column team (current filters). Hover for matches played.")
    order = sorted(set(D["team1_s"]) | set(D["team2_s"]))
    both = pd.concat([
        D.assign(a=D["team1_s"], b=D["team2_s"], aw=D["match_winner_s"].eq(D["team1_s"])),
        D.assign(a=D["team2_s"], b=D["team1_s"], aw=D["match_winner_s"].eq(D["team2_s"]))])
    g = both.groupby(["a", "b"])["aw"].agg(["mean", "size"])
    z = g["mean"].unstack().reindex(index=order, columns=order)
    n = g["size"].unstack().reindex(index=order, columns=order)
    z = z.where(n >= 3)
    fig = go.Figure(go.Heatmap(z=z.values, x=z.columns, y=z.index, zmin=0, zmax=1, customdata=n.values,
                               colorscale=[[0, CLAY], [0.5, BG], [1, GREEN]],
                               text=z.map(lambda v: "" if pd.isna(v) else f"{v:.0%}").values, texttemplate="%{text}",
                               hovertemplate="%{y} vs %{x}<br>%{z:.0%} over %{customdata} matches<extra></extra>",
                               colorbar=dict(tickformat=".0%", thickness=10)))
    fig.update_yaxes(autorange="reversed"); fig.update_xaxes(side="top")
    chart(fig, h=560, legend=False)
    st.caption("Pairs with fewer than 3 decided matches are left blank.")

    st.subheader("Compare two teams")
    names = sorted(set(F["team1"]) | set(F["team2"]), key=lambda t: SHORT[t])
    if len(names) < 2:
        st.info("Select at least two teams' worth of data (clear the team filter) to compare.")
    else:
        c1, c2 = st.columns(2)
        ta = c1.selectbox("Team A", names, index=0, format_func=lambda t: SHORT[t] + " · " + t)
        tb = c2.selectbox("Team B", names, index=min(1, len(names) - 1) if names[0] != ta else 1,
                          format_func=lambda t: SHORT[t] + " · " + t)
        if ta == tb:
            st.info("Pick two different teams.")
        else:
            hh = F[((F["team1"] == ta) & (F["team2"] == tb)) | ((F["team1"] == tb) & (F["team2"] == ta))]
            hd = hh[hh["decided"]]
            wa, wb = int((hd["match_winner"] == ta).sum()), int((hd["match_winner"] == tb).sum())
            if hh.empty:
                st.info("These two teams have not met under the current filters.")
            else:
                kk = st.columns(4)
                kpi(kk[0], "Matches", len(hh), f"{len(hh) - len(hd)} no result")
                kpi(kk[1], f"{SHORT[ta]} wins", wa, pct(wa / max(wa + wb, 1)))
                kpi(kk[2], f"{SHORT[tb]} wins", wb, pct(wb / max(wa + wb, 1)))
                last = hd.iloc[-1] if len(hd) else None
                kpi(kk[3], "Last meeting", SHORT.get(last["match_winner"], "-") + " won" if last is not None else "-",
                    last["match_date"].strftime("%d %b %Y") if last is not None else "")
                st.write("")
                by = hd.groupby(["season", "match_winner_s"]).size().reset_index(name="wins")
                fig = px.bar(by, x="season", y="wins", color="match_winner_s", color_discrete_map=COLOR,
                             title=f"{SHORT[ta]} vs {SHORT[tb]}: wins by season")
                fig.update_xaxes(dtick=1, title=None); fig.update_yaxes(dtick=1, title=None)
                chart(fig, h=320)
                tbl = hh[["match_date", "season", "stage", "venue", "match_winner", "win_by_runs", "win_by_wickets", "player_of_match"]].copy()
                tbl["match_date"] = tbl["match_date"].dt.date
                tbl["Margin"] = tbl.apply(lambda r: f"{int(r.win_by_runs)} runs" if pd.notna(r.win_by_runs)
                                          else f"{int(r.win_by_wickets)} wkts" if pd.notna(r.win_by_wickets) else "", axis=1)
                st.dataframe(tbl.drop(columns=["win_by_runs", "win_by_wickets"]).rename(columns={
                    "match_date": "Date", "season": "Season", "stage": "Stage", "venue": "Venue",
                    "match_winner": "Winner", "player_of_match": "Player of the match"})
                    .sort_values("Date", ascending=False), hide_index=True, width="stretch")

# ================================================================ TOSS & CHASING
with tab_toss:
    note(f"Toss winners won <b>{pct(D['toss_winner_won'].mean())}</b> of decided matches, so the toss is worth "
         f"about a {abs(D['toss_winner_won'].mean() - .5) * 100:.0f}-point edge. "
         f"Chasing sides won <b>{pct(1 - D['bat_first_won'].mean())}</b>.")
    a, b = st.columns(2)
    with a:
        st.subheader("What toss winners chose, and how it went")
        x = D.groupby("toss_decision")["toss_winner_won"].agg(["mean", "size"]).reset_index()
        x["Choice"] = x["toss_decision"].map({"field": "Chose to field", "bat": "Chose to bat"})
        fig = px.bar(x, x="Choice", y="mean", text=x["mean"].map(pct), hover_data=["size"],
                     color="Choice", color_discrete_map={"Chose to field": GREEN, "Chose to bat": CLAY})
        fig.add_hline(y=.5, line_dash="dot", line_color=MUTED)
        fig.update_traces(textposition="outside")
        fig.update_yaxes(tickformat=".0%", range=[0, .75], title="Toss winner's match win %"); fig.update_xaxes(title=None)
        chart(fig, legend=False)
    with b:
        st.subheader("Toss winner win % by team")
        tw = T[T["won_toss"] & T["decided"]].groupby("team_s")["won"].agg(["mean", "size"]).reset_index()
        tw = tw[tw["size"] >= 5].sort_values("mean")
        fig = px.bar(tw, y="team_s", x="mean", orientation="h", color="team_s", color_discrete_map=COLOR,
                     text=tw["mean"].map(pct), hover_data=["size"])
        fig.add_vline(x=.5, line_dash="dot", line_color=MUTED)
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(tickformat=".0%", range=[0, .85], title=None); fig.update_yaxes(title=None)
        chart(fig, legend=False)

    c, d = st.columns(2)
    with c:
        st.subheader("How matches are won")
        r = F[F["result"].eq("win")]
        fig = px.histogram(r.dropna(subset=["win_by_runs"]), x="win_by_runs", nbins=25,
                           title="Margin when the team batting first wins (runs)")
        fig.update_traces(marker_color=CLAY); fig.update_xaxes(title=None); fig.update_yaxes(title=None)
        chart(fig, h=320, legend=False)
    with d:
        st.subheader("\u00a0")
        r = F[F["result"].eq("win")]
        wk = r.dropna(subset=["win_by_wickets"])["win_by_wickets"].astype(int).value_counts().sort_index().reset_index()
        wk.columns = ["wickets", "matches"]
        fig = px.bar(wk, x="wickets", y="matches", title="Margin when the chasing side wins (wickets in hand)")
        fig.update_traces(marker_color=GREEN); fig.update_xaxes(dtick=1, title=None); fig.update_yaxes(title=None)
        chart(fig, h=320, legend=False)

    st.subheader("Toss influence by season")
    ts = D.groupby("season")["toss_winner_won"].mean().reset_index()
    fig = px.line(ts, x="season", y="toss_winner_won", markers=True)
    fig.add_hline(y=.5, line_dash="dot", line_color=MUTED)
    fig.update_traces(line_color=INK)
    fig.update_yaxes(tickformat=".0%", range=[.3, .7], title="Toss winner's match win %"); fig.update_xaxes(dtick=1, title=None)
    chart(fig, h=300, legend=False)
    st.caption(f"{int(F['super_over'].sum())} matches in this selection went to a super over; "
               f"{int((F['result'] == 'no result').sum())} had no result.")

# ================================================================ MATCH EXPLORER
with tab_exp:
    st.subheader("Player of the match")
    pm = F.dropna(subset=["player_of_match"]).groupby("player_of_match").size().sort_values(ascending=False).head(12)
    fig = px.bar(pm.sort_values().reset_index(name="awards"), y="player_of_match", x="awards", orientation="h",
                 text="awards")
    fig.update_traces(marker_color=GREEN, textposition="outside", cliponaxis=False)
    fig.update_xaxes(title=None); fig.update_yaxes(title=None)
    chart(fig, h=400, legend=False)

    st.subheader("All matches")
    q1, q2, q3 = st.columns([2, 1, 1])
    text = q1.text_input("Search team, ground, city or player", placeholder="e.g. Wankhede, Kohli, CSK")
    res = q2.selectbox("Result", ["All", "Decided", "Super over", "No result"])
    sd = q3.selectbox("Batting first", ["Any", "Won", "Lost"])
    X = F.copy()
    if text:
        s = text.lower()
        blob = (X["team1"] + " " + X["team2"] + " " + X["team1_s"] + " " + X["team2_s"] + " " + X["venue"] + " "
                + X["city"].fillna("") + " " + X["player_of_match"].fillna("")).str.lower()
        X = X[blob.str.contains(s, regex=False)]
    if res == "Decided": X = X[X["result"].eq("win")]
    elif res == "Super over": X = X[X["super_over"]]
    elif res == "No result": X = X[X["result"].eq("no result")]
    if sd == "Won": X = X[X["bat_first_won"] == True]
    elif sd == "Lost": X = X[X["bat_first_won"] == False]

    out = pd.DataFrame({
        "Date": X["match_date"].dt.date, "Season": X["season"], "Stage": X["stage"],
        "Match": X["team1_s"] + " vs " + X["team2_s"], "Venue": X["venue"], "City": X["city"],
        "Toss": X["toss_winner_s"] + " chose to " + X["toss_decision"],
        "Winner": X["match_winner_s"].fillna("No result"),
        "Margin": X.apply(lambda r: f"{int(r.win_by_runs)} runs" if pd.notna(r.win_by_runs)
                          else f"{int(r.win_by_wickets)} wkts" if pd.notna(r.win_by_wickets)
                          else "Super over" if r.super_over else "", axis=1),
        "Player of the match": X["player_of_match"],
    }).sort_values("Date", ascending=False)
    st.caption(f"{len(out):,} matches")
    st.dataframe(out, hide_index=True, width="stretch", height=460)
    st.download_button("Download as CSV", out.to_csv(index=False).encode(), "ipl_matches_filtered.csv", "text/csv")
