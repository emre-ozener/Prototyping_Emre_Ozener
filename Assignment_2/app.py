import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from pytube import Search
import re


st.set_page_config(page_title="Scout Dashboard", layout="wide", page_icon="⚽️")


if 'recommendation_history' not in st.session_state:
    st.session_state.recommendation_history = []


st.markdown("""
<style>
    .stTextArea textarea { margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("./Assignments/Assignment_2/final_players.csv")
    return df

df = load_data()


position_map = {
    'G': 'Goalkeeper',
    'D': 'Defender',
    'M': 'Midfielder',
    'F': 'Forward'
}
df['position_full'] = df['position'].map(position_map)


client = OpenAI(api_key="api_key" )


def get_openai_response(prompt, tokens=800):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


st.markdown("<h1 style='text-align: center; font-size: 48px;'>Scout Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'>Find new talents based on your needs, see their performance, watch their highlights.</p>", unsafe_allow_html=True)


with st.sidebar:
    st.header("Filter Players")
    player_filter = st.selectbox("Player Name", ["Any"] + sorted(df["name"].dropna().unique().tolist()))
    foot_filter = st.selectbox("Preferred Foot", ["Any"] + sorted(df["preferredFoot"].dropna().unique().tolist()))
    position_filter = st.selectbox("Position", ["Any"] + sorted(df["position_full"].dropna().unique().tolist()))
    age_filter = st.slider("Age Range", int(df["age"].min()), int(df["age"].max()), (18, 30))
    height_filter = st.slider("Height Range (cm)", int(df["height"].min()), int(df["height"].max()), (160, 200))

    value_min, value_max = float(df["value"].min()), float(df["value"].max())
    value_filter = st.slider("Market Value (€M)", value_min, value_max, (value_min, value_max))

additional_notes = st.text_area("Additional Comments to Help Choosing the Best Talent (optional)")


filtered_df = df.copy()
if player_filter != "Any":
    filtered_df = filtered_df[filtered_df["name"] == player_filter]
if foot_filter != "Any":
    filtered_df = filtered_df[filtered_df["preferredFoot"] == foot_filter]
if position_filter != "Any":
    filtered_df = filtered_df[filtered_df["position_full"] == position_filter]

filtered_df = filtered_df[(filtered_df["age"].between(age_filter[0], age_filter[1])) &
                          (filtered_df["height"].between(height_filter[0], height_filter[1])) &
                          (filtered_df["value"].between(value_filter[0], value_filter[1]))]


st.subheader("Filtered Players")
st.dataframe(filtered_df[["name", "position_full", "preferredFoot", "age", "height", "value"]], use_container_width=True)

fig = px.scatter(filtered_df, x="age", y="value", color="position_full", hover_data=["name", "preferredFoot"],
                 labels={"age": "Age", "value": "Market Value (€M)"},
                 title="Player Market Value by Age and Position")
st.plotly_chart(fig, use_container_width=True)


if st.button("Get Recommendation"):
    if filtered_df.empty:
        st.warning("No players found matching your criteria.")
    else:
        player_list = filtered_df['name'].tolist()
        prompt = f"""
        From these players: {', '.join(player_list)}, recommend the best player considering these scout comments: '{additional_notes}'.
        Provide:
        Player Name: [name]
        Justification: [brief reasoning based on your knowledge with pros and cons. also mention his possibility of transfer]
        """

        recommendation = get_openai_response(prompt)
        player_match = re.search(r"Player Name: (.+)", recommendation)

        if player_match:
            recommended_player = player_match.group(1).strip()
            player_row = df[df['name'] == recommended_player]
            if not player_row.empty:
                player_id = player_row.iloc[0]['player_id']
                iframe_url = f"https://widgets.sofascore.com/en/embed/player/{player_id}?widgetTheme=dark"
                st.markdown(f"### Recommended Player: {recommended_player}")
                justification = recommendation.split("Justification:")[-1].strip()
                st.markdown(f"**Reasoning:** {justification}")
                st.components.v1.iframe(iframe_url, height=800, scrolling=True)

                # YouTube Search
                try:
                    videosSearch = Search(f"{recommended_player} Highlights")
                    video_id = str(videosSearch.results[0]).split("videoId=")[1][:-1]
                
                    video_url = f"https://www.youtube.com/embed/" + video_id
                    st.markdown("#### Player Highlights")
                    st.components.v1.iframe(video_url, height=800)
                except Exception as e:
                    st.info("YouTube video could not be loaded.")
                    print(e)

                st.session_state.recommendation_history.append({
                    "Player": recommended_player,
                    "Justification": justification
                })
            else:
                st.error("Player ID not found.")
        else:
            st.markdown(recommendation)


if st.session_state.recommendation_history:
    st.markdown("---")
    st.subheader("Recommendation History")
    history_df = pd.DataFrame(st.session_state.recommendation_history)

    st.dataframe(history_df, width=1500, height=500)

    csv_data = history_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Recommendation History as CSV",
        data=csv_data,
        file_name="recommendation_history.csv",
        mime="text/csv"
    )


st.markdown("---")
st.markdown("<p style='text-align:center; font-size:14px;'>Scout Dashboard | Emre Ozener | Assignment 2</p>", unsafe_allow_html=True)