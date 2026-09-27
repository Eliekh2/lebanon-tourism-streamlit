"""
Lebanon Tourism Infrastructure Explorer
MSBA 325 - Interactive Visualizations with Streamlit

An interactive companion to the Plotly assignment, built on the same dataset
(Tourism-Lebanon-2023, AUB PKGCubes portal). It has two LINKED controls:
a governorate selector, and a town selector whose options are drawn from the
governorate you pick, so you drill down within one region rather than filtering
two dimensions independently.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Lebanon Tourism Explorer", page_icon="🗺️", layout="wide")

# ---- Validated colorblind-safe palettes (reused from the Plotly assignment) ----
GOV_ORDER = ["Akkar", "Baalbek-Hermel", "Beqaa", "Mount Lebanon",
             "Nabatieh", "North", "South"]
GOV_COLORS = dict(zip(GOV_ORDER,
    ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#9467BD"]))
TYPE_COLORS = {"Hotels": "#0072B2", "Cafes": "#E69F00",
               "Restaurants": "#009E73", "Guest houses": "#CC79A7"}
TYPES = ["Hotels", "Cafes", "Restaurants", "GuestHouses"]
SOURCE = ("Data: AUB PKGCubes portal (linked.aub.edu.lb), Tourism-Lebanon-2023 cube "
          "- 1,137 towns, from Lebanon IMPACT open data.")


@st.cache_data
def load_data():
    df = pd.read_csv("tourism_lebanon_towns.csv")
    df["Total"] = df[TYPES].sum(axis=1)
    df["Accommodation"] = df["Hotels"] + df["GuestHouses"]
    # towns tagged only at governorate level have no district; label them clearly
    df["Area"] = df["District"].fillna("").replace("", "Area-wide (no district)")
    return df


df = load_data()

# ============================ Header + context ==============================
st.title("Lebanon Tourism Infrastructure Explorer")
st.markdown(
    "This page explores where Lebanon's tourism establishments - **hotels, cafes, "
    "restaurants, and guest houses** - are located across the country's **1,137 towns**. "
    "Each town also carries a composite **Tourism Index** (0-10). Use the two linked "
    "controls below to focus on one governorate and then drill into its towns."
)

# ---- National context: static overview (gives context + the first insight) ----
st.subheader("The national picture")
gov_tot = (df.groupby("Governorate")[TYPES].sum().sum(axis=1)
             .reindex(GOV_ORDER).reset_index(name="Total"))
ctx = px.bar(gov_tot.sort_values("Total"), x="Total", y="Governorate", orientation="h",
             color="Governorate", color_discrete_map=GOV_COLORS, text="Total")
ctx.update_traces(textposition="outside", cliponaxis=False, showlegend=False)
ctx.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10),
                  xaxis_title="Total establishments", yaxis_title="",
                  plot_bgcolor="white", paper_bgcolor="white")
ctx.update_xaxes(gridcolor="#eee")
st.plotly_chart(ctx, width='stretch')
st.info(
    "**Insight 1 - supply is uneven.** Mount Lebanon holds far more tourism "
    "establishments than any other governorate (about a third of the national total), "
    "while the inland Baalbek-Hermel and Beqaa regions have the fewest. Tourism "
    "infrastructure tracks the populated coast, not land area."
)

st.divider()

# ============================ Linked controls ===============================
st.subheader("Explore within a region")
st.caption("Control 1 sets the region. Control 2's options are drawn from that region, "
           "so you drill down instead of filtering two things independently.")

c_left, c_right = st.columns(2)

# ---- CONTROL 1: governorate selector -------------------------------------
with c_left:
    gov = st.selectbox(
        "1. Choose a governorate",
        GOV_ORDER,
        index=GOV_ORDER.index("Mount Lebanon"),
        help="Sets the region in focus and populates the town list on the right.",
    )

region = df[df["Governorate"] == gov].copy()

# ---- CONTROL 2: town selector (options depend on Control 1 = the link) ----
towns_ranked = region.sort_values("Total", ascending=False)["Town"].tolist()
default_towns = towns_ranked[:12] if len(towns_ranked) > 12 else towns_ranked
with c_right:
    sel_towns = st.multiselect(
        f"2. Drill into towns of {gov}",
        options=towns_ranked,
        default=default_towns,
        help="Only towns inside the governorate you picked appear here. "
             "Defaults to the 12 with the most establishments.",
    )

if not sel_towns:
    st.warning("Select at least one town on the right to see the charts.")
    st.stop()

view = region[region["Town"].isin(sel_towns)].copy()

# ---- Metrics for the current selection (dynamic, second insight lives here) -
m1, m2, m3, m4 = st.columns(4)
m1.metric("Towns shown", len(view))
m2.metric("Establishments", int(view["Total"].sum()))
m3.metric("Avg Tourism Index", round(view["TourismIndex"].mean(), 1))
top_row = view.loc[view["Total"].idxmax()]
m4.metric("Busiest town", top_row["Town"], f"{int(top_row['Total'])} places")

# ============================ Two linked charts =============================
left, right = st.columns(2)

# Chart A - composition by town (stacked bar of the four establishment types)
with left:
    st.markdown("**Establishment mix, by town**")
    long = view.melt(id_vars="Town", value_vars=TYPES, var_name="Type", value_name="Count")
    long["Type"] = long["Type"].replace({"GuestHouses": "Guest houses"})
    order = view.sort_values("Total")["Town"].tolist()
    fig_a = px.bar(long, x="Count", y="Town", color="Type", orientation="h",
                   category_orders={"Town": order,
                                    "Type": ["Hotels", "Cafes", "Restaurants", "Guest houses"]},
                   color_discrete_map=TYPE_COLORS)
    fig_a.update_layout(barmode="stack", height=460, margin=dict(l=10, r=10, t=10, b=10),
                        legend_title_text="", plot_bgcolor="white", paper_bgcolor="white",
                        legend=dict(orientation="h", y=1.08))
    fig_a.update_xaxes(title="Establishments", gridcolor="#eee")
    fig_a.update_yaxes(title="")
    st.plotly_chart(fig_a, width='stretch')

# Chart B - relationship between cafes and restaurants across the selected towns
with right:
    st.markdown("**Cafes vs restaurants (bubble = hotels + guest houses)**")
    fig_b = px.scatter(view, x="Cafes", y="Restaurants",
                       size="Accommodation", color="Area", hover_name="Town",
                       size_max=40, hover_data={"TourismIndex": True, "Hotels": True,
                                                "GuestHouses": True, "Area": False})
    fig_b.update_traces(marker=dict(line=dict(width=1, color="white"), opacity=0.85))
    fig_b.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10),
                        legend_title_text="District", plot_bgcolor="white",
                        paper_bgcolor="white", legend=dict(orientation="h", y=1.08))
    fig_b.update_xaxes(title="Cafes in town", gridcolor="#eee")
    fig_b.update_yaxes(title="Restaurants in town", gridcolor="#eee")
    st.plotly_chart(fig_b, width='stretch')

st.success(
    f"**Insight 2 - within {gov}, a few towns carry the region.** The stacked bars show "
    "establishments concentrate in a handful of towns rather than spreading evenly, and "
    "the scatter shows cafes and restaurants rise together while lodging (bubble size) "
    "moves separately. Change the region or the towns to see the pattern hold across "
    "Lebanon."
)

# ============================ Design justifications =========================
st.divider()
st.subheader("Design justifications")

with st.expander("Control 1 - Governorate selector (a dropdown)"):
    st.markdown(
        "- **User question it answers:** *\"What does tourism supply look like in one "
        "specific region?\"* It sets the region in focus for everything below.\n"
        "- **Why a dropdown (selectbox) and not, say, a multiselect or a set of "
        "checkboxes:** the region is a single, mutually exclusive choice, and a dropdown "
        "shows exactly one selection at a time. That keeps the page focused on one region "
        "and avoids the clutter of comparing all seven at once.\n"
        "- **Course concept:** *focusing attention and reducing clutter.* Committing to one "
        "region at a time is the visualization principle of removing what the reader does "
        "not need so the signal for the chosen region stands out."
    )

with st.expander("Control 2 - Town selector (a multiselect, linked to Control 1)"):
    st.markdown(
        "- **User question it answers:** *\"Which towns inside this region actually drive "
        "its tourism, and how do they compare?\"*\n"
        "- **The link:** its options are **only the towns in the governorate chosen in "
        "Control 1**, and it defaults to that region's 12 busiest towns. Picking a new "
        "region rebuilds this list. This is a **drill-down**, not two independent filters - "
        "Control 1 changes the *options* of Control 2.\n"
        "- **Why a multiselect and not a slider or a single dropdown:** the user needs to "
        "compare several towns at once and add or remove them freely, which a single-choice "
        "dropdown cannot do and a numeric slider (which assumes an ordered range) does not "
        "fit town names.\n"
        "- **Course concept:** *progressive disclosure / drill-down.* Start with the whole "
        "country, narrow to a region, then inspect its towns - detail is revealed only when "
        "the reader asks for it."
    )

st.caption(SOURCE + "  |  AI-use: generative AI helped write the Python/Streamlit code, "
           "aggregate the data, and draft the wording; the dataset, chart choices, and the "
           "read of the insights are the author's own.")
