import streamlit as st
import pandas as pd
import altair as alt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import geopandas as gpd

# ----- Streamlit config -----
st.set_page_config(page_title="College Info Dashboard", layout="wide")
alt.themes.enable("dark")

# ---- CSS for tight spacing & table fixes ----
st.markdown("""
    <style>
    div.block-container {padding-top: 0rem;}
    .css-1v0mbdj {padding-top: 0rem;}
    .stDataFrame div { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    </style>
""", unsafe_allow_html=True)

# ----- Google Sheets -----
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("", scope)
client = gspread.authorize(creds)
sheet = client.open("dashboard_data").sheet1  
data = sheet.get_all_records()
original_df = pd.DataFrame(data)

original_df.columns = original_df.columns.str.strip()
original_df.columns = original_df.columns.str.replace('\u00a0', '', regex=True)
original_df.columns = original_df.columns.str.encode('ascii', 'ignore').str.decode('ascii')

df = original_df.copy()

# ----- GeoData -----
gdf = gpd.read_file("maharshtra_shapefiles/2001_Dist.shp")
gdf = gdf[gdf['ST_NM'].str.upper() == 'MAHARASHTRA']    
gdf['DISTRICT'] = gdf['DISTRICT'].str.strip().str.upper()
df['District'] = df['District'].str.strip().str.upper()

# ----- Sidebar -----
with st.sidebar:
    st.image("iribl_logo.jpeg", use_container_width=False , width=200)

    districts = sorted(df['District'].dropna().unique())
    selected_district = st.selectbox("Select District", ["ALL"] + districts)
    if selected_district != "ALL":
        df = df[df['District'] == selected_district]

    talukas = sorted(df['Taluka'].dropna().unique())
    selected_taluka = st.selectbox("Select Taluka", ["ALL"] + talukas)
    if selected_taluka != "ALL":
        df = df[df['Taluka'] == selected_taluka]

    universities = sorted(df['University Name'].dropna().unique())
    selected_university = st.selectbox("Select University", ["ALL"] + universities)
    if selected_university != "ALL":
        df = df[df['University Name'] == selected_university]

    College_Type = sorted(df['College Type'].dropna().unique())
    selected_type = st.selectbox("Select a Type", ["ALL"] + College_Type)
    if selected_type != "ALL":
        df = df[df['College Type'] == selected_type]

    Area_Type = sorted(df['College Types'].dropna().unique())
    selected_area_type = st.selectbox("Select an area type", ["ALL"] + Area_Type)
    if selected_area_type != "ALL":
        df = df[df['College Types'] == selected_area_type]

    exc_Type = sorted(df['Exclusively in Womens Colleges'].dropna().unique())
    exc_selected_type = st.selectbox("Select exclusive type", ["ALL"] + exc_Type)
    if exc_selected_type != "ALL":
        df = df[df['Exclusively in Womens Colleges'] == exc_selected_type]

# ----- KPIs and Graphs -----
with st.container():
    col1, col2, col3 = st.columns([0.7, 2.8, 1.5])

    with col1:
        st.markdown("<h4 style='margin-top: 0;'>KPIs</h4>", unsafe_allow_html=True)
        current_colleges = df['College Name'].nunique()
        current_universities = df['University Name'].nunique()
        current_talukas = df['Taluka'].nunique()
        current_districts = df['District'].nunique()

        def custom_metric_card(label, value):
            st.markdown(
                f"""
                <div style="
                    background-color: #26272e;
                    width: 150px;
                    height: 150px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    border: 1px solid #444;
                ">
                    <div style="font-size: 1.4em; color: #aaa; font-weight: bold;">{label}</div>
                    <div style="font-size: 2.3em; font-weight: bold; color: #eee; margin-top: 5px;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        custom_metric_card("COLLEGES", current_colleges)
        custom_metric_card("UNIVERSITIES", current_universities)
        custom_metric_card("TALUKAS", current_talukas)
        custom_metric_card("DISTRICTS", current_districts)

    with col2:
        st.markdown("<h4>Choropleth Map</h4>", unsafe_allow_html=True)

        # Group by district
        college_count_df = df.groupby('District').size().reset_index(name='Colleges')
        university_count_df = df.groupby('District')['University Name'].nunique().reset_index(name='Universities')

        # Merge both metrics into one DataFrame
        map_df = pd.merge(college_count_df, university_count_df, on='District', how='outer')

        # Merge with GeoDataFrame
        gdf = gdf.merge(map_df, left_on='DISTRICT', right_on='District', how='left')
        gdf['Colleges'] = gdf['Colleges'].fillna(0)
        gdf['Universities'] = gdf['Universities'].fillna(0)

        fig = px.choropleth(
            gdf,
            geojson=gdf.geometry,
            locations=gdf.index,
            color="Colleges",
            projection="mercator",
            color_continuous_scale="Viridis",
            hover_name="DISTRICT",
            hover_data={"Colleges": True, "Universities": True}
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            autosize=False,
            height=700,
            width=1200,  # bigger size
            margin=dict(l=0, r=0, t=10, b=10),
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )

        st.plotly_chart(fig, use_container_width=False)


    with col3:
        st.markdown("#### Universities by Number of Colleges")

        uni_df = df['University Name'].value_counts().reset_index()
        uni_df.columns = ['University', 'College Count']
        uni_df = uni_df.sort_values(by='College Count', ascending=False)

        st.dataframe(
            uni_df,
            column_order=("University", "College Count"),
            hide_index=True,
            height=300,
            use_container_width=True,
            column_config={
                "University": st.column_config.TextColumn("University"),
                "College Count": st.column_config.ProgressColumn(
                    "Colleges",
                    format="%d",
                    min_value=0,
                    max_value=int(uni_df["College Count"].max()),
                ),
            },
        )

        st.markdown("#### Urban vs Rural Distribution")

        def make_donut(input_response, input_text, input_color):
            if input_color == 'urban':
                chart_color = ['#00cc96', '#333333']
            elif input_color == 'rural':
                chart_color = ['#EF553B', '#333333']
            else:
                chart_color = ['#29b5e8', '#155F7A']

            source = pd.DataFrame({
                "Topic": ['', input_text],
                "% value": [100 - input_response, input_response]
            })

            source_bg = pd.DataFrame({
                "Topic": ['', input_text],
                "% value": [100, 0]
            })

            plot = alt.Chart(source).mark_arc(innerRadius=65, cornerRadius=25).encode(
                theta="% value",
                color=alt.Color(
                    "Topic:N",
                    scale=alt.Scale(
                        domain=[input_text, ''],
                        range=chart_color
                    ),
                    legend=None
                ),
            ).properties(width=200, height=200)

            text = plot.mark_text(
                align='center',
                color=chart_color[0],
                font="Lato",
                fontSize=26,
                fontWeight=700,
                fontStyle="italic"
            ).encode(
                text=alt.value(f'{input_response}%')
            )

            plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=65, cornerRadius=20).encode(
                theta="% value",
                color=alt.Color(
                    "Topic:N",
                    scale=alt.Scale(
                        domain=[input_text, ''],
                        range=chart_color
                    ),
                    legend=None
                ),
            ).properties(width=200, height=200)

            return plot_bg + plot + text

        urban_count = df[df['College Types'] == 'Urban'].shape[0]
        rural_count = df[df['College Types'] == 'Rural'].shape[0]
        total = urban_count + rural_count

        if total > 0:
            urban_percent = round((urban_count / total) * 100, 1)
            rural_percent = round((rural_count / total) * 100, 1)

            donut1, donut2 = st.columns(2)
            with donut1:
                st.markdown("##### Urban")
                st.altair_chart(make_donut(urban_percent, 'Urban', 'urban'), use_container_width=True)
            with donut2:
                st.markdown("##### Rural")
                st.altair_chart(make_donut(rural_percent, 'Rural', 'rural'), use_container_width=True)

# --- College Type & Women's Exclusivity ---
with st.container():
    col_bar, col_women = st.columns(2)

    with col_bar:
        st.markdown("#### Number of Colleges by Type")
        college_type_df = df['College Type'].value_counts().reset_index()
        college_type_df.columns = ['College Type', 'Count']

        bar_fig = px.bar(
            college_type_df,
            x='College Type',
            y='Count',
            color='College Type',
            color_discrete_sequence=px.colors.qualitative.Set3,
            labels={'Count': 'Number of Colleges'},
        )

        bar_fig.update_layout(
            height=350,
            margin=dict(t=30, b=50, l=10, r=10),
            xaxis_title="College Type",
            yaxis_title="Number of Colleges",
            yaxis_title_standoff=30,  # shifts label out of the axis
            xaxis_tickangle=-40,      # rotates x-axis labels to avoid overlap
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=False
        )


        st.plotly_chart(bar_fig, use_container_width=True)

    with col_women:
        st.markdown("### Women’s Exclusivity Area Chart")

        # Prepare data
        exclusive_df = df['Exclusively in Womens Colleges'].value_counts().reset_index()
        exclusive_df.columns = ['Exclusivity', 'Count']

        # Sort for smoother curve
        exclusive_df = exclusive_df.sort_values('Exclusivity')

        # Create colorful area chart using Plotly
        area_fig = px.area(
            exclusive_df,
            x='Exclusivity',
            y='Count',
            color='Exclusivity',
            line_group='Exclusivity',
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Pastel  # You can change palette here
        )

        area_fig.update_layout(
            height=350,
            margin=dict(t=30, b=50, l=10, r=10),
            xaxis_title="Exclusivity Type",
            yaxis_title="Number of Colleges",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend_title_text='Exclusivity'
        )

        st.plotly_chart(area_fig, use_container_width=True)

