import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
import base64



st.set_page_config(page_title="Historical Staking Data", page_icon="🔍️", layout="wide", initial_sidebar_state="auto")
    
st.title("Get Historical Data for Assets on StakingRewards.com")

st.info("""
This web app allows you to fetch historical data for various assets on StakingRewards.com.

Step 1: Enter the slug of the asset that you want historical data for

Step 2: Enter the metric of the asset that you want historical data for

Step 3: Enter the date range that you are looking for 

Step 4: Click 'Get my Data'

When inputting multiple assets, please separate them by a comma without a space.
""")




today = date.today()

url = 'https://api.stakingrewards.com/public/query'

api_key = st.text_input("Enter your API key", type="password") # add an input box for API key

headers = {"X-API-Key": api_key} # use the API key in the headers

query = """
query getHistoricalMetrics($slugs:[String!],$limit:Int,$offset:Int, $metricKeys:[String!],$timeStart:Date, $isActive:Boolean){
  assets(where:{slugs:$slugs, isActive:$isActive},limit:20){
    name
    metrics(where:{metricKeys:$metricKeys, createdAt_gt:$timeStart},limit:$limit, offset:$offset, order:{createdAt:asc}){
      defaultValue
      createdAt
      label
    }
  }
}
"""


def fetch_data(slugs, metricKeys, timeStart):
    variables = {
        "slugs": slugs,
        "limit": len(metricKeys),
        "offset": 0,
        "metricKeys": metricKeys,
        "timeStart": str(timeStart),
        "isActive": True,
    }

    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    print(response.text)
    response_dict = response.json()
    assets_dict = response_dict['data']['assets']

    return assets_dict


def create_download_link(data_df, title="Download CSV file", filename="comparison_data.csv"):
    csv = data_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{title}</a>'


def prepare_and_display_data(assets_data, metricKeys):
    data = []
    for assets in assets_data:
        for asset in assets:
            asset_data = {
                "Asset Name": asset["name"],
                "Date": asset["metrics"][0]["createdAt"],
            }
            asset_data.update({metric["label"]: metric["defaultValue"] for metric in asset["metrics"]})
            data.append(asset_data)

    data_df = pd.DataFrame(data)

    st.markdown(create_download_link(data_df), unsafe_allow_html=True)
    st.write(data_df)



slugs_input = st.text_input("Enter the Slugs of each Asset (comma-separated without a space)", "polkadot")
metrics_input = st.text_input("Enter the Metrics you are looking for (comma-separated without a space)", "staking_ratio,staking_marketcap")

st.markdown("""
<style>
.link-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}
.link-container a {
  display: block;
  margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="link-container">
    <a href="https://docs.google.com/spreadsheets/d/1Jz46jlCfPWav6Ia9Hrmdv33215v8iUz9508LR8HKyE8/edit?usp=sharing" target="_blank">🔍️ View available slugs and metrics that you can query for each asset</a>
</div>
""", unsafe_allow_html=True)




start_date = st.date_input("Enter the starting Date", value=today - timedelta(days=30))
end_date = st.date_input("Enter the ending Date", value=today)

compare_button = st.button("Get my Data!")


st.markdown("---")

# ... (rest of the code remains the same)

if compare_button:
    slugs = slugs_input.split(',')
    metrics = metrics_input.split(',')

    total_days = (end_date - start_date).days + 1

    assets_data = []
    current_date = start_date
    processed_days = 0

    progress_bar = st.progress(0)  # Create a progress bar

    with st.spinner("Loading..."):
        while current_date <= end_date:
            assets = fetch_data(slugs, metrics, current_date)
            assets_data.append(assets)
            current_date += timedelta(days=1)
            processed_days += 1

            # Update the progress bar
            progress = processed_days / total_days
            progress_bar.progress(progress)  # Update the progress bar value

    st.balloons()
    prepare_and_display_data(assets_data, metrics)




