import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================
# PAGE CONFIGURATION
# =====================================

# CUSTOM STADIUM BACKGROUND
import base64
from pathlib import Path

image_path = Path(__file__).parent / "staduim.png"

with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

st.markdown(f"""
<style>

/* =====================================
   STADIUM BACKGROUND
   ===================================== */

.stApp {{
    background-image:
        linear-gradient(
            rgba(5, 10, 25, 0.45),
            rgba(5, 10, 25, 0.65)
        ),
        url("data:image/png;base64,{encoded_image}");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: white;
    min-height: 100vh;
}}

/* =====================================
   SIDEBAR
   ===================================== */

[data-testid="stSidebar"] {{
    background: rgba(10, 20, 40, 0.94);
}}

/* =====================================
   DASHBOARD LAYOUT
   ===================================== */

.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}}

/* =====================================
   ANIMATION KEYFRAMES
   ===================================== */

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(18px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes goldGlow {{
    0%, 100% {{
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.12);
    }}
    50% {{
        box-shadow: 0 8px 28px rgba(212, 175, 55, 0.30);
    }}
}}

/* =====================================
   ANIMATED HEADINGS
   ===================================== */

h1, h2, h3 {{
    animation: fadeInUp 0.7s ease-out both;
}}

h1 {{
    color: #FFD166;
    font-weight: 800;
}}

h2 {{
    color: #FFB84D;
    font-weight: 700;
}}

h3 {{
    color: #FFFFFF;
    font-weight: 600;
}}

/* =====================================
   PROFESSIONAL KPI CARDS
   ===================================== */

[data-testid="stMetric"] {{
    background: linear-gradient(
        135deg,
        rgba(12, 25, 50, 0.96),
        rgba(35, 55, 85, 0.94)
    );
    border: 1px solid rgba(255, 193, 7, 0.65);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.30);
    backdrop-filter: blur(12px);
    transition: transform 0.3s ease,
                border-color 0.3s ease,
                box-shadow 0.3s ease;
}}

[data-testid="stMetric"]:hover {{
    transform: translateY(-6px);
    border-color: #FFD700;
    animation: goldGlow 2s ease-in-out infinite;
}}

[data-testid="stMetricLabel"] {{
    color: #FFD166;
    font-weight: 600;
}}

[data-testid="stMetricValue"] {{
    color: #FFFFFF;
    font-weight: 800;
}}

/* =====================================
   CHART CONTAINERS
   ===================================== */

[data-testid="stPlotlyChart"] {{
    background: rgba(10, 15, 30, 0.78);
    border: 1px solid rgba(100, 149, 237, 0.18);
    border-radius: 14px;
    padding: 10px;
    animation: fadeInUp 0.9s ease-out both;
    transition: border-color 0.3s ease,
                box-shadow 0.3s ease;
}}

[data-testid="stPlotlyChart"]:hover {{
    border-color: rgba(255, 193, 7, 0.65);
    box-shadow: 0 0 18px rgba(59, 130, 246, 0.20);
}}

/* =====================================
   PROFESSIONAL FILTER DESIGN
   ===================================== */

div[data-testid="stExpander"] {{
    background: rgba(12, 25, 50, 0.82);
    border: 1px solid rgba(255, 193, 7, 0.35);
    border-radius: 12px;
    transition: border-color 0.3s ease,
                box-shadow 0.3s ease;
}}

div[data-testid="stExpander"]:hover {{
    border-color: #FFD166;
    box-shadow: 0 0 12px rgba(255, 193, 7, 0.12);
}}

div[data-baseweb="select"] > div {{
    background-color: #111827 !important;
    border: 1px solid #486581 !important;
    border-radius: 8px !important;
}}

div[data-baseweb="tag"] {{
    background-color: #1D4ED8 !important;
    border: 1px solid #60A5FA !important;
    border-radius: 5px !important;
}}

div[data-baseweb="tag"] span {{
    color: #FFFFFF !important;
}}

/* =====================================
   SIDEBAR TEXT
   ===================================== */

section[data-testid="stSidebar"] h2 {{
    color: #FFD700;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.20);
}}

/* =====================================
   MAIN CONTENT TEXT
   ===================================== */

.stMarkdown, .stCaption {{
    color: #FFFFFF;
}}

/* =====================================
   ACCESSIBILITY
   ===================================== */

@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
    }}
}}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOAD IPL DATA
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"


@st.cache_data
def load_data():

    matches_path = DATA_DIR / "matches.csv"
    teams_path = DATA_DIR / "teams.csv"
    venues_path = DATA_DIR / "venues.csv"

    matches = pd.read_csv(matches_path)
    teams = pd.read_csv(teams_path)
    venues = pd.read_csv(venues_path)

    return matches, teams, venues


matches, teams, venues = load_data()

# =====================================
# INTERACTIVE FILTERS
# =====================================

st.sidebar.title("🎛️ IPL Dashboard Filters")

# Detect columns
season_col = next(
    (c for c in matches.columns
     if c.strip().lower() in ["season", "year"]),
    None
)

winner_col = next(
    (c for c in matches.columns
     if c.strip().lower() in [
         "winner", "winning_team", "match_winner",
         "winningteam", "winner_team"
     ]),
    None
)

venue_match_col = next(
    (c for c in matches.columns
     if c.strip().lower() in ["venue", "stadium"]),
    None
)

team1_col = next(
    (c for c in matches.columns
     if c.strip().lower() in [
         "team1", "team_1", "team one"
     ]),
    None
)

team2_col = next(
    (c for c in matches.columns
     if c.strip().lower() in [
         "team2", "team_2", "team two"
     ]),
    None
)

filtered_matches = matches.copy()

# Dashboard-wide filters remain available for high-level overview(s)
def get_filtered_dataframe(df, selected_seasons=None, selected_teams=None, selected_venues=None):
    filtered_df = df.copy()

    if selected_seasons is not None and season_col:
        filtered_df = filtered_df[
            filtered_df[season_col].astype(str).isin(
                [str(s) for s in selected_seasons]
            )
        ]

    if selected_teams is not None:
        if team1_col or team2_col or winner_col:
            team_mask = pd.Series(False, index=filtered_df.index)
            for col in [team1_col, team2_col, winner_col]:
                if col:
                    team_mask |= filtered_df[col].astype(str).isin(
                        [str(team) for team in selected_teams]
                    )
            filtered_df = filtered_df[team_mask]

    if selected_venues is not None and venue_match_col:
        filtered_df = filtered_df[
            filtered_df[venue_match_col].astype(str).isin(
                [str(v) for v in selected_venues]
            )
        ]

    return filtered_df


# =====================================
## =====================================
# INITIALIZE MATCH DATA
# =====================================

filtered_matches = matches.copy()


# =====================================
# FILTER HELPER FUNCTIONS
# =====================================

def normalize_filter_columns(columns):
    if columns is None:
        return []

    if isinstance(columns, str):
        return [columns]

    return [col for col in columns if col]


def apply_chart_filters(
    df,
    section_name,
    season_col=None,
    team_cols=None,
    venue_col=None
):
    filtered_df = df.copy()

    season_fields = normalize_filter_columns(season_col)
    team_fields = normalize_filter_columns(team_cols)
    venue_fields = normalize_filter_columns(venue_col)

    # Separate filters for each chart
    with st.expander(
        f"🔎 Filter {section_name}",
        expanded=True
    ):

        # Season filter
        if season_fields:
            season_field = season_fields[0]

            season_options = sorted(
                filtered_df[season_field]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_seasons = st.multiselect(
                "📅 Select Season",
                options=season_options,
                default=season_options,
                key=f"{section_name}_season_filter"
            )

            if selected_seasons:
                filtered_df = filtered_df[
                    filtered_df[season_field]
                    .astype(str)
                    .isin(selected_seasons)
                ]
            else:
                return filtered_df.iloc[0:0]

        # Team filter
        if team_fields:
            team_options = sorted({
                str(value)
                for col in team_fields
                for value in filtered_df[col]
                .dropna()
                .unique()
            })

            selected_teams = st.multiselect(
                "🏏 Select Team",
                options=team_options,
                default=team_options,
                key=f"{section_name}_team_filter"
            )

            if selected_teams:
                team_mask = pd.Series(
                    False,
                    index=filtered_df.index
                )

                for col in team_fields:
                    team_mask |= (
                        filtered_df[col]
                        .astype(str)
                        .isin(selected_teams)
                    )

                filtered_df = filtered_df[team_mask]

            else:
                return filtered_df.iloc[0:0]

        # Venue filter
        if venue_fields:
            venue_field = venue_fields[0]

            venue_options = sorted(
                filtered_df[venue_field]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_venues = st.multiselect(
                "📍 Select Venue",
                options=venue_options,
                default=venue_options,
                key=f"{section_name}_venue_filter"
            )

            if selected_venues:
                filtered_df = filtered_df[
                    filtered_df[venue_field]
                    .astype(str)
                    .isin(selected_venues)
                ]

            else:
                return filtered_df.iloc[0:0]

    return filtered_df


def normalize_filter_columns(columns):
    if columns is None:
        return []
    if isinstance(columns, str):
        return [columns]
    return [col for col in columns if col]


def apply_chart_filters(df, section_name, season_col=None, team_cols=None, venue_col=None):
    filtered_df = df.copy()
    season_fields = normalize_filter_columns(season_col)
    team_fields = normalize_filter_columns(team_cols)
    venue_fields = normalize_filter_columns(venue_col)

    if not any([season_fields, team_fields, venue_fields]):
        return filtered_df

    with st.expander(f"🔎 Filter {section_name}", expanded=True):
        if season_fields:
            season_field = season_fields[0]
            season_options = sorted(
                filtered_df[season_field].dropna().astype(str).unique()
            )
            selected_seasons = st.multiselect(
                "Select Season",
                options=season_options,
                default=season_options,
                key=f"{section_name.lower().replace(' ', '_')}_season"
            )
            if selected_seasons:
                filtered_df = filtered_df[
                    filtered_df[season_field].astype(str).isin(selected_seasons)
                ]
            else:
                return filtered_df.iloc[0:0]

        if team_fields:
            team_options = sorted({
                str(value)
                for col in team_fields
                for value in filtered_df[col].dropna().astype(str).unique()
            })
            selected_teams = st.multiselect(
                "Select Team",
                options=team_options,
                default=team_options,
                key=f"{section_name.lower().replace(' ', '_')}_team"
            )
            if selected_teams:
                team_mask = pd.Series(False, index=filtered_df.index)
                for col in team_fields:
                    team_mask |= filtered_df[col].astype(str).isin(selected_teams)
                filtered_df = filtered_df[team_mask]
            else:
                return filtered_df.iloc[0:0]

        if venue_fields:
            venue_field = venue_fields[0]
            venue_options = sorted(
                filtered_df[venue_field].dropna().astype(str).unique()
            )
            selected_venues = st.multiselect(
                "Select Venue",
                options=venue_options,
                default=venue_options,
                key=f"{section_name.lower().replace(' ', '_')}_venue"
            )
            if selected_venues:
                filtered_df = filtered_df[
                    filtered_df[venue_field].astype(str).isin(selected_venues)
                ]
            else:
                return filtered_df.iloc[0:0]

    return filtered_df
# =====================================
# SIDEBAR - DASHBOARD INFORMATION
# =====================================

st.sidebar.markdown(
    """
    <div style="text-align:center; padding:15px 5px;">
        <h2 style="color:#FFD700;">🏏 IPL Dashboard</h2>
        <p style="color:#FFFFFF; font-size:14px;">
            Cricket Analytics
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    <h3 style="color:#FFA500;">📊 Dashboard Information</h3>
    """,
    unsafe_allow_html=True
)

st.sidebar.info(
    """
    **🏏 Match Analytics**

    Analyze IPL matches, seasons,
    team wins and toss decisions.

    **🏆 Team Performance**

    Explore team statistics and
    compare team performance.

    **📈 Data Visualization**

    Understand IPL data through
    interactive charts.
    """
)

st.sidebar.markdown("---")

st.sidebar.caption("IPL Cricket Analytics Dashboard")



# =====================================
# DASHBOARD HEADER
# =====================================

st.markdown("""
# 🏏 IPL INSIGHTS

### BEYOND THE BOUNDARIES

Explore IPL matches, teams and venues through data.
""")

st.divider()

# =====================================
# KPI CARDS
# =====================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🏏 Total Matches", f"{len(filtered_matches):,}")

with col2:
    st.metric("🏆 Total Teams", f"{len(teams):,}")

with col3:
    st.metric("📍 Total Venues", f"{len(venues):,}")

with col4:
    season_column = next(
        (
            c for c in matches.columns
            if c.lower() in ["season", "year"]
        ),
        None
    )

    total_seasons = (
    filtered_matches[season_column].nunique()
    if season_column else 0
)

    st.metric("📅 Total Seasons", f"{total_seasons:,}")

st.divider()

st.success("IPL Insights dashboard loaded successfully!")
# =====================================
# MATCH ANALYTICS
# =====================================

st.divider()

st.header("📊 Match Analytics")

# Season column
season_col = next(
    (c for c in matches.columns if c.lower() in ["season", "year"]),
    None
)

# Team column
winner_col = next(
    (
        c for c in matches.columns
        if c.strip().lower() in [
            "winner",
            "winning_team",
            "match_winner",
            "winningteam",
            "winner_team"
        ]
    ),
    None
)

toss_col = next(
    (c for c in matches.columns if c.lower() == "toss_decision"),
    None
)

# =====================================
# SEASON-WISE MATCHES
# =====================================

if season_col:
    st.subheader("🏏 Matches by Season")

    # Separate filters for this chart
    chart_df = apply_chart_filters(
        matches.copy(),
        "Season Matches",
        season_col=season_col,
        team_cols=[team1_col, team2_col, winner_col],
        venue_col=venue_match_col
    )

    if not chart_df.empty:

        # Count matches for each season
        season_data = (
            chart_df.groupby(season_col)
            .size()
            .reset_index(name="Matches")
            .sort_values(season_col)
        )

        season_data[season_col] = season_data[season_col].astype(str)

        fig = px.bar(
            season_data,
            x=season_col,
            y="Matches",
            title="Number of Matches Played in Each Season",
            labels={
                season_col: "Season",
                "Matches": "Total Matches"
            },
            text="Matches",
            color="Matches",
            template="plotly_dark"
        )

        fig.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            xaxis_tickangle=-45,
            yaxis_rangemode="tozero"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No match data available for the selected filters.")

else:
    st.warning("Season column not found.")
    # =====================================
# TEAM-WISE WINS
# =====================================

if winner_col:
    st.subheader("🏆 Matches Won by Each Team")
    chart_df = apply_chart_filters(
        filtered_matches,
        "Team Wins",
        season_col=season_col,
        team_cols=[team1_col, team2_col, winner_col],
        venue_col=venue_match_col
    )

    team_wins = (
        chart_df[winner_col]
        .dropna()
        .value_counts()
        .reset_index()
    )

    team_wins.columns = ["Team", "Wins"]

    fig = px.bar(
    team_wins.sort_values("Wins", ascending=True),
    x="Wins",
    y="Team",
    orientation="h",
    title="Total Matches Won by Each Team",
    labels={
        "Team": "IPL Team",
        "Wins": "Total Wins"
    },
    color="Wins",
    template="plotly_dark"
)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Winner column not found in matches.csv")

# =====================================
# TOSS DECISION ANALYSIS
# =====================================

if toss_col:
    st.subheader("🪙 Toss Decision Analysis")

    # Separate filters for this chart
    chart_df = apply_chart_filters(
        matches,
        "Toss Decisions",
        season_col=season_col,
        team_cols=[team1_col, team2_col, winner_col],
        venue_col=venue_match_col
    )

    if not chart_df.empty:
        toss_data = (
            chart_df[toss_col]
            .dropna()
            .value_counts()
            .reset_index()
        )

        toss_data.columns = ["Decision", "Count"]

        if not toss_data.empty:
            fig3 = px.pie(
                toss_data,
                names="Decision",
                values="Count",
                title="Batting vs Fielding After Winning the Toss",
                hole=0.45,
                template="plotly_dark"
            )

            fig3.update_traces(
                textinfo="percent+label",
                textposition="inside"
            )

            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                showlegend=True
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )
        else:
            st.warning("No toss decision data available for these filters.")
    else:
        st.warning("No matches available for the selected filters.")

else:
    st.warning("Toss decision column not found.")

st.success("Match Analytics loaded successfully!")
# =====================================
# TEAM ANALYSIS
# =====================================

st.divider()

st.header("🏆 Team Performance Analysis")

# Find required columns
team_col = next(
    (c for c in teams.columns if c.lower() in ["team", "team_name", "name"]),
    None
)

winner_col = next(
    (
        c for c in matches.columns
        if c.strip().lower() in [
            "winner",
            "winning_team",
            "match_winner",
            "winningteam",
            "winner_team"
        ]
    ),
    None
)

if winner_col:

    # Calculate team wins
    chart_df = apply_chart_filters(
        filtered_matches,
        "Team Performance",
        season_col=season_col,
        team_cols=[team1_col, team2_col, winner_col],
        venue_col=venue_match_col
    )

    team_wins = (
        chart_df[winner_col]
        .dropna()
        .value_counts()
        .reset_index()
    )

    team_wins.columns = ["Team", "Wins"]

    # Team-wise wins chart
    st.subheader("🥇 Matches Won by Team")

    fig_team = px.bar(
        team_wins.sort_values("Wins", ascending=True),
        x="Wins",
        y="Team",
        orientation="h",
        color="Wins",
        title="Team-wise IPL Match Wins",
        template="plotly_dark",
        text="Wins"
    )

    fig_team.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        yaxis_title="Team",
        xaxis_title="Total Wins"
    )

    st.plotly_chart(fig_team, use_container_width=True)
    # =====================================
# =====================================
# INDIVIDUAL TEAM ANALYSIS
# =====================================

st.divider()
st.subheader("🔎 Explore Individual Team")

if winner_col and not filtered_matches.empty:

    # Calculate wins from filtered matches
    team_wins = (
        filtered_matches[winner_col]
        .dropna()
        .value_counts()
        .reset_index()
    )

    team_wins.columns = ["Team", "Wins"]

    if not team_wins.empty:

        selected_team = st.selectbox(
            "🏏 Select a Team",
            options=team_wins["Team"].tolist(),
            key="individual_team_select"
        )

        selected_wins = int(
            team_wins.loc[
                team_wins["Team"] == selected_team,
                "Wins"
            ].iloc[0]
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("🏏 Selected Team", selected_team)

        with col2:
            st.metric("🏆 Matches Won", selected_wins)

    else:
        st.warning("No team wins available for the selected filters.")

else:
    st.warning("No matches available for the selected filters.")                            
# =====================================
# TEAMS DASHBOARD
# =====================================

st.divider()

st.header("🏏 Teams Dashboard")

# Find team name column
team_col = next(
    (
        c for c in teams.columns
        if c.strip().lower() in [
            "team", "team_name", "name",
            "team1", "team2", "team_name"
        ]
    ),
    None
)

if team_col:
    team_names = (
        teams[team_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🏆 Total Teams", len(team_names))

    with col2:
        st.metric(
            "📊 Teams with Match Wins",
            matches[winner_col].nunique()
            if winner_col else 0
        )

    st.subheader("Team List")

    st.dataframe(
        pd.DataFrame({"Team Name": sorted(team_names)}),
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("Team name column not found in teams.csv")


# =====================================
# VENUES DASHBOARD
# =====================================

st.divider()

st.header("🏟️ Venues Dashboard")

# Find venue name column
venue_col = next(
    (
        c for c in venues.columns
        if c.strip().lower() in [
            "venue", "venue_name", "name",
            "stadium", "stadium_name"
        ]
    ),
    None
)

if venue_col:
    venue_names = (
        venues[venue_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🏟️ Total Venues", len(venue_names))

    with col2:
        st.metric(
            "📍 Unique Venue Names",
            len(venue_names)
        )

    st.subheader("Venue List")

    st.dataframe(
        pd.DataFrame({"Venue Name": sorted(venue_names)}),
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("Venue name column not found in venues.csv")

    # =====================================
# MATCH EXPLORER
# =====================================

st.divider()
st.header("🔎 IPL Match Explorer")

st.write("Explore match details using the selected filters.")

# Use filtered match data
if not filtered_matches.empty:
    st.dataframe(
        filtered_matches,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Showing {len(filtered_matches)} matches"
    )
else:
    st.warning("No matches found for the selected filters.")

    # =====================================
#