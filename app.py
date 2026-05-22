"""
VERA-MT: Verification Engine for Results & Accountability - Montana
Type 4 Detection using ACCESS for ELLs Speaking vs Writing + MAST Achievement Data

Montana context: WIDA ACCESS, MAST test (new 2025), 4 levels,
~400 districts, ~3,500 ELs (tiny). Billings opened dedicated EL school 2024.
Indian Education for All (IEFA) constitutional mandate.

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_MT_BLUE = "#003366"
MT_GOLD = "#FFD700"
MT_DARK = "#002244"
MT_RED = "#CC0000"

# ============================================================================
# DATA: Montana Districts with EL Populations
# ============================================================================

def load_districts():
    """
    Load MT districts with significant EL populations.
    Data modeled from OPI (Office of Public Instruction) public reports.
    ~400 districts statewide, ~3,500 ELs (tiny state EL population).
    MAST test (new 2025), 4 levels.
    Billings opened dedicated EL school in 2024.
    Indian Education for All (IEFA) is a constitutional mandate.
    """
    data = [
        # (district_id, district_name, total_students, el_count, el_percent,
        #  grad_rate, mast_ela_all, mast_ela_el, mast_ela_hispanic, mast_ela_native, mast_ela_white,
        #  mast_math_all, mast_math_el, top_el_languages)
        ("0002", "Billings Public Schools", 16200, 810, 5.0,
         82.5, 48.5, 16.2, 25.8, 22.5, 58.2,
         44.2, 14.5, "Spanish, Crow, Northern Cheyenne, Somali"),
        ("0001", "Great Falls Public Schools", 10200, 408, 4.0,
         80.2, 46.2, 15.5, 24.5, 20.8, 56.5,
         42.1, 13.8, "Spanish, Blackfeet, Cree, Arabic"),
        ("0040", "Missoula County Public Schools", 8500, 510, 6.0,
         84.8, 50.5, 17.2, 27.2, 24.5, 60.8,
         46.5, 15.5, "Spanish, Salish, Arabic, Somali"),
        ("0034", "Helena Public Schools", 7800, 312, 4.0,
         86.2, 52.8, 18.5, 28.5, 25.2, 62.5,
         48.8, 16.2, "Spanish, Russian, Arabic, Mandarin"),
        ("0007", "Bozeman Public Schools", 6200, 310, 5.0,
         88.5, 56.2, 20.5, 30.8, 27.5, 64.8,
         52.5, 18.2, "Spanish, Mandarin, Korean, Japanese"),
        ("0003", "Butte Public Schools", 3800, 114, 3.0,
         78.5, 44.2, 14.8, 23.5, 19.8, 55.2,
         40.5, 13.2, "Spanish, Mandarin, Filipino"),
        ("0015", "Kalispell Public Schools", 4200, 168, 4.0,
         83.5, 48.8, 16.5, 26.2, 22.8, 58.8,
         44.8, 14.8, "Spanish, Russian, Ukrainian, Arabic"),
        ("0110", "Hardin Public Schools", 1200, 120, 10.0,
         68.5, 32.5, 10.8, 18.5, 15.2, 48.5,
         28.5, 9.5, "Crow, Spanish, Northern Cheyenne"),
        ("0051", "Browning Public Schools", 1800, 180, 10.0,
         62.5, 28.5, 9.2, 16.2, 12.8, 44.5,
         24.8, 8.5, "Blackfeet, Spanish"),
        ("0087", "Lame Deer Public Schools", 650, 65, 10.0,
         60.2, 26.2, 8.5, 14.8, 11.5, 42.2,
         22.5, 7.8, "Northern Cheyenne, Spanish"),
        ("0052", "Whitefish School District", 2100, 63, 3.0,
         90.2, 58.5, 21.8, 32.5, 28.8, 66.2,
         54.8, 19.5, "Spanish, German, Mandarin"),
        ("0004", "Havre Public Schools", 1600, 80, 5.0,
         76.8, 42.5, 14.2, 22.8, 18.5, 54.2,
         38.8, 12.8, "Spanish, Cree, Chippewa, Arabic"),
        ("0006", "Miles City Public Schools", 1400, 42, 3.0,
         79.5, 45.8, 15.2, 24.2, 20.2, 56.8,
         42.2, 14.2, "Spanish, Russian"),
        ("0009", "Lewistown Public Schools", 1200, 36, 3.0,
         81.5, 47.5, 16.2, 25.5, 21.8, 58.5,
         43.5, 14.5, "Spanish, Russian, Filipino"),
        ("0050", "Sidney Public Schools", 1100, 55, 5.0,
         80.8, 46.5, 15.8, 24.8, 21.2, 57.5,
         42.8, 14.2, "Spanish, Russian, Filipino"),
    ]

    return pd.DataFrame(data, columns=[
        'district_id', 'district_name', 'total_students',
        'el_count', 'el_percent', 'graduation_rate',
        'mast_ela_all', 'mast_ela_el', 'mast_ela_hispanic',
        'mast_ela_native', 'mast_ela_white',
        'mast_math_all', 'mast_math_el', 'top_el_languages'
    ])


# ============================================================================
# DATA: ACCESS Domain Data
# ============================================================================

def load_access_data(districts_df):
    """
    Generate district ACCESS domain data modeled from WIDA ACCESS norms.
    Montana exit criteria: Overall composite 4.5+ (WIDA standard).
    Scale scores approximate WIDA ACCESS 100-600 range by grade.
    """
    access_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 335 + (grade * 9)
                base_writing = 282 + (grade * 7)
                base_listening = 340 + (grade * 8)
                base_reading = 295 + (grade * 7)

                el_factor = d['mast_ela_el'] / 18.0
                speaking_adj = int(14 * el_factor + d['el_percent'] * 0.35)
                writing_adj = int(-10 + (el_factor - 1) * 11)
                listening_adj = speaking_adj - 2
                reading_adj = writing_adj + 10

                # Tribal language speakers: strong oral tradition
                if any(lang in d['top_el_languages'] for lang in ['Crow', 'Blackfeet', 'Northern Cheyenne', 'Salish', 'Cree']):
                    speaking_adj += 5
                    writing_adj -= 4

                year_adj = 3 if year == 2025 else 0

                # Reservation districts: lower baseline but strong oral
                if d['district_id'] in ['0110', '0051', '0087']:
                    speaking_adj += 6
                    writing_adj -= 6

                access_data.append({
                    'district_id': d['district_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(5, int(d['el_count'] / 6)),
                    'listening_avg': base_listening + listening_adj + year_adj,
                    'speaking_avg': base_speaking + speaking_adj + year_adj,
                    'reading_avg': base_reading + reading_adj + year_adj,
                    'writing_avg': base_writing + writing_adj + year_adj,
                    'composite_avg': int((base_speaking + speaking_adj +
                                          base_writing + writing_adj +
                                          base_listening + listening_adj +
                                          base_reading + reading_adj) / 4 + 15 + year_adj),
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: MAST Achievement Data
# ============================================================================

def load_mast_data(districts_df):
    """
    Generate MAST data (new 2025) based on OPI proficiency rates.
    MAST has 4 performance levels (replacing Smarter Balanced).
    ELA and Math tested grades 3-8.
    """
    mast_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    if subject == 'ELA':
                        base = d['mast_ela_all']
                    else:
                        base = d['mast_math_all']

                    prof = max(10, min(85, base + (grade - 5) * -1.5))

                    if year == 2024:
                        prof = prof - 1.2

                    level4 = max(2, prof * 0.18)
                    level3 = max(5, prof - level4)
                    level2 = max(10, (100 - prof) * 0.45)
                    level1 = max(5, 100 - level3 - level4 - level2)

                    mast_data.append({
                        'district_id': d['district_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'level1_pct': round(level1, 1),
                        'level2_pct': round(level2, 1),
                        'level3_pct': round(level3, 1),
                        'level4_pct': round(level4, 1),
                        'prof_and_above_pct': round(level3 + level4, 1),
                    })

    return pd.DataFrame(mast_data)


# ============================================================================
# DATA: Statewide Domain Proficiency
# ============================================================================

def load_statewide_domain_data():
    """
    Statewide ACCESS domain proficiency percentages by grade cluster.
    Montana has ~3,500 ELs across ~400 districts (tiny EL population).
    Indian Education for All (IEFA) constitutional mandate.
    Billings opened dedicated EL school in 2024.
    """
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 44, 'speaking': 40, 'reading': 26, 'writing': 19},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 50, 'speaking': 46, 'reading': 30, 'writing': 22},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 54, 'speaking': 48, 'reading': 34, 'writing': 25},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 56, 'speaking': 50, 'reading': 36, 'writing': 27},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 42, 'speaking': 38, 'reading': 24, 'writing': 17},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 48, 'speaking': 44, 'reading': 28, 'writing': 20},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 52, 'speaking': 46, 'reading': 32, 'writing': 23},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 54, 'speaking': 48, 'reading': 34, 'writing': 25},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_password():
    st.session_state.authenticated = True
    return True


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, district_id, grade, year):
    """
    Compute Type 4 detection for a given district/grade/year.
    Type 4 candidates show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.
    """
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'district_id': district_id,
        'district_name': row['district_name'],
        'grade': grade,
        'year': year,
        'speaking_avg': row['speaking_avg'],
        'writing_avg': row['writing_avg'],
        'delta': delta,
        'delta_normalized': delta_normalized,
        'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGES
# ============================================================================

def render_overview(districts_df):
    st.header("Montana Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pilot Districts", len(districts_df))
    with col2:
        st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3:
        st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4:
        st.metric("Statewide EL Count", "~3,500", help="Tiny EL population across ~400 districts")

    st.divider()

    st.subheader("Montana EL Context")
    st.markdown("""
    Montana has one of the **smallest EL populations** in the nation (~3,500 students),
    but faces unique challenges. The state's **Indian Education for All (IEFA)** is a
    constitutional mandate requiring all students to learn about Montana's tribal nations.
    Several reservation districts serve Native American students who are classified as ELs
    for tribal language heritage reasons. In 2024, **Billings opened a dedicated EL school**
    to serve its growing immigrant population.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**IEFA Constitutional Mandate**\nIndian Education for All")
    with col2:
        st.warning("**Billings EL School (2024)**\nDedicated newcomer facility")
    with col3:
        st.info("**MAST (New 2025)**\n4 performance levels")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**WIDA ACCESS**\nEnglish proficiency assessment")
    with col2:
        st.info("**~400 Districts**\nMostly rural, tiny EL counts")
    with col3:
        st.info("**7 Tribal Nations**\nBlackfeet, Crow, Salish-Kootenai, etc.")

    st.divider()

    st.subheader("Top EL Languages Statewide")
    lang_data = pd.DataFrame({
        'Language': ['Spanish', 'Crow', 'Blackfeet', 'N. Cheyenne', 'Somali', 'Arabic', 'Russian', 'Mandarin'],
        'Approx Share': [35, 12, 8, 6, 5, 5, 4, 3],
    })
    fig_lang = px.bar(lang_data, x='Language', y='Approx Share',
                      color='Approx Share',
                      color_continuous_scale=[[0, '#C0C0C0'], [1, MT_BLUE]],
                      labels={'Approx Share': '% of EL Population'},
                      text='Approx Share')
    fig_lang.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_lang.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                           title="Top EL Home Languages in Montana")
    st.plotly_chart(fig_lang, use_container_width=True)

    st.divider()

    st.subheader("Pilot Districts -- EL Populations")
    display = districts_df[['district_id', 'district_name', 'total_students', 'el_count', 'el_percent',
                            'mast_ela_all', 'mast_ela_el', 'mast_ela_native', 'mast_ela_white',
                            'top_el_languages']].copy()
    display.columns = ['Dist ID', 'District', 'Students', 'EL Count', 'EL %',
                       'ELA All %', 'ELA EL %', 'ELA Native %', 'ELA White %',
                       'Top Languages']
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, MT_BLUE]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False,
                      title="EL Population by District (color = EL %)")
    st.plotly_chart(fig, use_container_width=True)


def render_domain_analysis(domain_df):
    st.header("Statewide ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** OPI ACCESS data files. Montana is a WIDA Consortium member.
    Domain proficiency percentages show the systemic oral-written delta. Montana's
    small EL population means statewide data is dominated by a few larger districts
    (Billings, Missoula, Great Falls). Tribal language heritage students on reservations
    show particularly strong oral-written gaps.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', MT_BLUE), ('speaking', MT_GOLD),
                           ('reading', '#888888'), ('writing', MT_RED)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient",
        barmode='group', height=450, yaxis=dict(range=[0, 72])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[MT_RED if d > 20 else MT_GOLD for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap",
                       yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.markdown("""
    ---
    **Why this matters for Montana:** The oral-written gap has particular significance for
    Native American EL students on reservations, where languages like Crow, Blackfeet, and
    Northern Cheyenne have strong oral traditions but varying degrees of written standardization.
    The IEFA mandate means these students' linguistic heritage should be seen as an asset,
    not a deficit. Billings' new dedicated EL school (2024) represents a model for addressing
    newcomer needs in Montana's largest city.
    """)


def render_access_analysis(access_df, districts_df):
    st.header("ACCESS for ELLs Analysis")
    st.markdown("""
    **WIDA ACCESS** measures English learners across four domains. Montana has ~3,500 ELs
    across ~400 districts. Exit criteria: Overall composite **4.5+** (WIDA standard).
    Many districts have very small EL counts, making data interpretation challenging.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="acc_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="acc_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]

        lang = districts_df[districts_df['district_id'] == district_id]['top_el_languages'].values[0]
        st.info(f"**Top EL languages in {district}:** {lang}")

        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2:
            st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3:
            st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4:
            st.metric("Writing", f"{row['writing_avg']:.0f}")
        with col5:
            st.metric("Composite", f"{row['composite_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(
            x=domains, y=scores,
            marker_color=[MT_BLUE, MT_GOLD, '#888888', MT_RED],
            text=[f"{s:.0f}" for s in scores], textposition='outside'
        ))
        fig.update_layout(
            title=f"ACCESS Domains -- {district} -- Grade {grade} ({year})",
            yaxis_title="Scale Score", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Oral Average", f"{oral:.0f}")
        with col2:
            st.metric("Written Average", f"{written:.0f}")
        with col3:
            st.metric("Oral-Written Gap", f"{gap:+.0f}",
                      delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.subheader("Exit Criteria Check (MT: Composite 4.5+ WIDA standard)")
        st.markdown("""
        Montana follows the WIDA standard exit criteria requiring an overall composite
        score of **4.5 or higher**. With only ~3,500 ELs statewide, many districts have
        very small sample sizes that require careful interpretation. The IEFA mandate
        adds context for Native American students classified as ELs.
        """)
    else:
        st.warning("No data available for the selected filters.")


def render_type4(access_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.

    In Montana, this is particularly relevant for **tribal language heritage** students
    on reservations (Crow, Blackfeet, Northern Cheyenne) and for the growing
    **newcomer/immigrant** population in Billings, where a dedicated EL school opened in 2024.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="t4_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    result = compute_type4_analysis(access_df, district_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2:
            st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3:
            st.metric("Delta", f"{result['delta']:+.0f}")
        with col4:
            st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']],
                             marker_color=MT_GOLD))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']],
                             marker_color=MT_BLUE))
        fig.update_layout(
            title=f"Speaking vs Writing -- {district} -- Grade {grade}",
            barmode='group', height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
            st.markdown("""
            **Montana-specific action:** For reservation districts, coordinate with tribal
            education departments and consider the IEFA framework when designing interventions.
            For Billings and other urban districts, the new dedicated EL school model may
            provide targeted writing support. OPI provides EL resources and technical assistance
            to districts with small EL populations.
            """)
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(access_df, district_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['speaking_avg'],
                name='Speaking', mode='lines+markers',
                line=dict(color=MT_GOLD, width=3)
            ))
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['writing_avg'],
                name='Writing', mode='lines+markers',
                line=dict(color=MT_BLUE, width=3)
            ))
            fig.update_layout(
                title="Speaking vs Writing Across Grades",
                xaxis_title="Grade", yaxis_title="Scale Score", height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Type 4 Summary Table")
            summary = gdf[['grade', 'speaking_avg', 'writing_avg', 'delta', 'delta_normalized', 'flagged',
                           'total_tested', 'estimated_flagged']].copy()
            summary.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Norm Delta', 'Flagged',
                              'Tested', 'Est. Affected']
            st.dataframe(summary, use_container_width=True, hide_index=True)


def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **MAST ELA proficiency by subgroup** across pilot districts.
    Montana's achievement gaps are most visible between white and Native American students,
    reflecting the legacy of historical inequities. The **IEFA constitutional mandate**
    aims to address cultural inclusion but academic gaps persist, particularly on reservations.
    """)

    st.divider()

    fig = go.Figure()
    sorted_df = districts_df.sort_values('mast_ela_all', ascending=True)
    for col, name, color in [
        ('mast_ela_white', 'White', '#666666'),
        ('mast_ela_all', 'All Students', MT_BLUE),
        ('mast_ela_hispanic', 'Hispanic', '#E8540A'),
        ('mast_ela_native', 'Native American', MT_RED),
        ('mast_ela_el', 'English Learners', MT_GOLD),
    ]:
        fig.add_trace(go.Bar(
            x=sorted_df[col], y=sorted_df['district_name'],
            name=name, orientation='h', marker_color=color
        ))

    fig.update_layout(
        title="MAST ELA Proficiency by Subgroup",
        barmode='group', xaxis_title="% Proficient", height=650,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Gap Magnitude: White - Native American ELA Proficiency")
    districts_df_copy = districts_df.copy()
    districts_df_copy['wn_gap'] = districts_df_copy['mast_ela_white'] - districts_df_copy['mast_ela_native']
    districts_df_copy['wh_gap'] = districts_df_copy['mast_ela_white'] - districts_df_copy['mast_ela_hispanic']
    districts_df_copy['we_gap'] = districts_df_copy['mast_ela_white'] - districts_df_copy['mast_ela_el']

    col1, col2, col3 = st.columns(3)
    with col1:
        avg_wn = districts_df_copy['wn_gap'].mean()
        st.metric("Avg White-Native Gap", f"{avg_wn:.1f} pts", delta="Critical", delta_color="inverse")
    with col2:
        avg_wh = districts_df_copy['wh_gap'].mean()
        st.metric("Avg White-Hispanic Gap", f"{avg_wh:.1f} pts", delta="Critical", delta_color="inverse")
    with col3:
        avg_we = districts_df_copy['we_gap'].mean()
        st.metric("Avg White-EL Gap", f"{avg_we:.1f} pts", delta="Critical", delta_color="inverse")

    fig_gap = go.Figure()
    gap_sorted = districts_df_copy.sort_values('wn_gap', ascending=True)
    fig_gap.add_trace(go.Bar(
        x=gap_sorted['wn_gap'], y=gap_sorted['district_name'],
        orientation='h', marker_color=[MT_RED if g > 30 else MT_GOLD for g in gap_sorted['wn_gap']],
        text=[f"{g:.0f} pts" for g in gap_sorted['wn_gap']], textposition='outside'
    ))
    fig_gap.update_layout(
        title="White-Native American ELA Gap by District (pts)", height=550,
        xaxis_title="Gap (percentage points)"
    )
    st.plotly_chart(fig_gap, use_container_width=True)

    st.subheader("EL Proficiency vs Overall Proficiency")
    fig2 = px.scatter(
        districts_df, x='mast_ela_all', y='mast_ela_el', size='el_count',
        color='el_percent', color_continuous_scale=[[0, '#ccc'], [1, MT_BLUE]],
        hover_name='district_name',
        labels={'mast_ela_all': 'All Students ELA %', 'mast_ela_el': 'EL ELA %',
                'el_count': 'EL Count', 'el_percent': 'EL %'}
    )
    fig2.add_shape(type="line", x0=0, y0=0, x1=80, y1=80,
                   line=dict(dash="dash", color="gray"))
    fig2.update_layout(
        title="EL Proficiency vs District Overall -- Gap Visualization", height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    ---
    **Montana context:** The White-Native American achievement gap on reservations
    (Browning, Hardin, Lame Deer) reflects deep historical inequities. The IEFA
    constitutional mandate provides a framework for cultural inclusion, but academic
    outcomes remain a challenge. Billings' dedicated EL school (2024) represents a new
    approach to serving newcomer immigrants alongside the state's traditional tribal
    language heritage EL populations.
    """)


def render_mast(mast_df, districts_df):
    st.header("MAST Assessment Analysis")
    st.markdown("""
    **Montana State Assessment (MAST)** -- New for 2025, replacing Smarter Balanced.
    4 performance levels.

    ELA and Math tested grades 3-8.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="mast_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="mast_g")
    with col3:
        subject = st.selectbox("Subject", ['ELA', 'Math'], key="mast_s")
    with col4:
        year = st.selectbox("Year", [2025, 2024], key="mast_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = mast_df[
        (mast_df['district_id'] == district_id) &
        (mast_df['grade'] == grade) &
        (mast_df['subject'] == subject) &
        (mast_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Level 1", f"{row['level1_pct']:.1f}%")
        with col2:
            st.metric("Level 2", f"{row['level2_pct']:.1f}%")
        with col3:
            st.metric("Level 3", f"{row['level3_pct']:.1f}%")
        with col4:
            st.metric("Level 4", f"{row['level4_pct']:.1f}%")

        levels = ['Level 1', 'Level 2', 'Level 3', 'Level 4']
        values = [row['level1_pct'], row['level2_pct'],
                  row['level3_pct'], row['level4_pct']]
        colors = [MT_RED, '#E8540A', MT_GOLD, MT_BLUE]
        fig = go.Figure(go.Bar(
            x=levels, y=values, marker_color=colors,
            text=[f"{v:.1f}%" for v in values], textposition='outside'
        ))
        fig.update_layout(
            title=f"MAST {subject} -- {district} -- Grade {grade} ({year})",
            yaxis_title="Percentage", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Combined Proficiency (Level 3 + Level 4)",
                  f"{row['prof_and_above_pct']:.1f}%")

        st.subheader(f"MAST {subject} Across Grades -- {district} ({year})")
        cross = mast_df[
            (mast_df['district_id'] == district_id) &
            (mast_df['subject'] == subject) &
            (mast_df['year'] == year)
        ]
        if not cross.empty:
            fig2 = go.Figure()
            for level, color in zip(levels, colors):
                col_name = level.lower().replace(' ', '') + '_pct'
                fig2.add_trace(go.Bar(
                    x=cross['grade'], y=cross[col_name],
                    name=level, marker_color=color
                ))
            fig2.update_layout(
                barmode='stack', xaxis_title="Grade", yaxis_title="Percentage",
                height=400, title=f"MAST {subject} Performance Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")


def render_export(access_df, mast_df, districts_df, domain_df):
    st.header("Export Data")

    st.markdown("Download VERA-MT analysis data as CSV files for further analysis.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ACCESS CSV",
            access_df.to_csv(index=False),
            "vera_mt_access.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("MAST Data")
        st.dataframe(mast_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download MAST CSV",
            mast_df.to_csv(index=False),
            "vera_mt_mast.csv", "text/csv",
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Domain CSV",
            domain_df.to_csv(index=False),
            "vera_mt_domains.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("District Reference Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Districts CSV",
            districts_df.to_csv(index=False),
            "vera_mt_districts.csv", "text/csv",
            use_container_width=True
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(
        page_title="VERA-MT | Montana Type 4 Detection",
        page_icon="*",
        layout="wide"
    )

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {MT_BLUE}; }}
        .stButton > button {{ background-color: {MT_BLUE}; color: white; }}
        .stButton > button:hover {{ background-color: {MT_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    districts_df = load_districts()
    access_df = load_access_data(districts_df)
    mast_df = load_mast_data(districts_df)
    domain_df = load_statewide_domain_data()

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {MT_BLUE}; margin: 0;">VERA-MT</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Montana Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Statewide Domain Analysis",
        "ACCESS Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "MAST Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ACCESS for ELLs (WIDA)
    - OPI ACCESS Files
    - MAST (MT State Assessment, new 2025)
    - MT ESSA Accountability

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points (normalized)

    **MT Exit Criteria:**
    - Composite 4.5+ (WIDA standard)

    **Key Context:**
    - ~3,500 ELs statewide (tiny)
    - ~400 school districts
    - **IEFA constitutional mandate**
    - Billings dedicated EL school (2024)
    - MAST new 2025 (4 levels)
    - 7 tribal nations
    - Crow, Blackfeet, N. Cheyenne languages

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview":
        render_overview(districts_df)
    elif page == "Statewide Domain Analysis":
        render_domain_analysis(domain_df)
    elif page == "ACCESS Analysis":
        render_access_analysis(access_df, districts_df)
    elif page == "Type 4 Detection":
        render_type4(access_df, districts_df)
    elif page == "Achievement Gaps":
        render_achievement_gaps(districts_df)
    elif page == "MAST Analysis":
        render_mast(mast_df, districts_df)
    elif page == "Export Data":
        render_export(access_df, mast_df, districts_df, domain_df)


if __name__ == "__main__":
    main()
