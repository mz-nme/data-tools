import json
import zipfile
import pandas as pd
import streamlit as st
import requests
from io import BytesIO


def convert(response_json):
    json_file = BytesIO()
    json_file.write(response_json)
    return json_file


def request(message_type, edited_df, start_date, end_date):
    base_url = "https://api.informatika.si/enotna-vstopna-tocka/merilni-podatki/meter-readings"

    encoded_string = st.secrets['encoded_string']
    headers = {
        'accept': 'application/json',
        'Authorization': f'Basic {encoded_string}'
    }

    if message_type == 'Daily 15 minute':
        base_url = base_url + '?messageType=D1_15MIN'
    elif message_type == 'Monthly 15 minute':
        base_url = base_url + '?messageType=M1_15MIN'
    elif message_type == 'Specify date':
        base_url = base_url + '?startTime=' + str(start_date) + '&endTime=' + str(end_date)

    usage_points = edited_df.tolist()
    usage_points_str = '&'.join(f"usagePoints={point}" for point in usage_points)
    complete_url = f"{base_url}&{usage_points_str}"

    return requests.get(complete_url, headers=headers)


def get_zip(json_response):
    meter_readings = json_response["meterReadings"]

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for i, meter_reading in enumerate(meter_readings):
            usage_point = meter_reading["usagePoint"]
            filename = f"{usage_point}.json"
            json_data = json.dumps(meter_reading, separators=(",", ":"))
            zip_file.writestr(filename, json_data)

    zip_buffer.seek(0)

    return zip_buffer


def main():
    st.set_page_config(layout="centered")

    st.subheader("Meter readings")

    messageType = st.selectbox('Type of meter readings', ('Daily 15 minute', 'Monthly 15 minute', 'Specify date'))

    start_date, end_date = "", ""
    if messageType == 'Specify date':
        col_left, col_right = st.columns(2)
        with col_left:
            start_date = st.date_input('Start date')
        with col_right:
            end_date = st.date_input('End date')

    uploaded_file = st.file_uploader('Upload a file', type='xlsx')

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, converters={'Merilna točka': str})
        df = df['Merilna točka']

        edited_df = st.data_editor(df)

        if st.button('Retreive', type='primary'):
            response = request(messageType, edited_df, start_date, end_date)
            st.write(response)
            if response.status_code != 200:
                st.write(response.json())
            else:
                st.download_button(
                    "Download JSON",
                    type='primary',
                    data=json.dumps(response.json()),
                    file_name='meter_readings.json',
                    mime='application/json'
                )
                st.download_button(
                    "Download JSON ZIP",
                    type='primary',
                    data=get_zip(response.json()),
                    file_name='meter_readings.zip'
                )


if __name__ == "__main__":
    main()
