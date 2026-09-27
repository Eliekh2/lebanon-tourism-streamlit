# Lebanon Tourism Infrastructure Explorer

An interactive Streamlit app for MSBA 325 (Data Visualization & Communication),
built on the same dataset as the Plotly assignment: **Tourism-Lebanon-2023** from
the AUB PKGCubes portal (1,137 Lebanese towns, with counts of hotels, cafes,
restaurants and guest houses and a composite Tourism Index).

**Live app:** https://lebanon-tourism-app-lhcbezejtvn6z8jc9f5jts.streamlit.app/

## What it does

The page shows where Lebanon's tourism establishments sit and lets you drill into
one region at a time using **two linked controls**:

1. **Governorate** (dropdown) - sets the region in focus.
2. **Towns** (multiselect) - its options are drawn from the governorate chosen in
   control 1, so you drill down within that region instead of filtering two things
   independently. Picking a new governorate rebuilds the town list.

Two charts and a metrics row update with the selection: a stacked bar of each
town's establishment mix, and a scatter of cafes vs restaurants (bubble size =
hotels + guest houses).

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py` - the Streamlit app
- `tourism_lebanon_towns.csv` - the dataset (town, governorate, district, Tourism Index, and the four establishment counts)
- `requirements.txt` - dependencies

## Data source

AUB PKGCubes portal (https://linked.aub.edu.lb:8502/), Tourism-Lebanon-2023 cube,
built from the Lebanon IMPACT open-data programme. The town records were kept at
town level and tagged with their governorate and district for this app.

## AI use

Generative AI helped gather and clean the data, write the Streamlit/Plotly code,
and draft wording. The dataset choice, the interaction design, the chart choices,
and the reading of the insights are the author's own.
