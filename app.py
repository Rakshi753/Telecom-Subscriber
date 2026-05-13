import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.title("Patient Zero - Telecom Subscriber Management")

agent = st.selectbox("Select Agent", ["Agent A", "Agent B", "Admin"])
st.write(f"Logged in as: {agent}")

def display_as_table(data):
    if isinstance(data, dict):
        st.table(pd.DataFrame([data]))
    elif isinstance(data, list):
        st.table(pd.DataFrame(data))
    else:
        st.write(data)

if st.button("Seed Initial Data (Run Once)"):
    try:
        res = requests.post(f"{API_URL}/seed")
        display_as_table(res.json())
    except Exception as e:
        st.error(f"Error: {e}")

st.header("Create Subscriber")
with st.form("create_sub"):
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    plan_id = st.number_input("Plan ID (leave 0 for None)", min_value=0, value=1)
    submit_create = st.form_submit_button("Create")
    if submit_create:
        payload = {"name": name, "phone_number": phone}
        if plan_id > 0:
            payload["plan_id"] = plan_id
        try:
            res = requests.post(f"{API_URL}/subscribers/", json=payload)
            display_as_table(res.json())
        except Exception as e:
            st.error(f"Error: {e}")

st.header("Search Subscriber")
search_id = st.number_input("Subscriber ID to Search", min_value=1, value=1)
if st.button("Search"):
    try:
        res = requests.get(f"{API_URL}/subscribers/{search_id}")
        st.write("Status:", res.status_code)
        try:
            display_as_table(res.json())
        except:
            st.write("Failed to parse response")
    except Exception as e:
        st.error(f"Error: {e}")

st.header("Update Plan Quota")
with st.form("update_plan"):
    update_id = st.number_input("Subscriber ID to Update", min_value=1, value=1)

    quota_gb_input = st.text_input("New Quota (GB)", value="10")
    submit_update = st.form_submit_button("Update")
    if submit_update:
        
        payload = {"quota_gb": quota_gb_input + " GB"} 
        try:
            res = requests.put(f"{API_URL}/subscribers/{update_id}/plan", json=payload)
            st.write("Status:", res.status_code)
            try:
                display_as_table(res.json())
            except:
                pass
        except Exception as e:
            st.error(f"Error: {e}")

st.header("Deactivate Subscriber")
deactivate_id = st.number_input("Subscriber ID to Deactivate", min_value=1, value=1)
if st.button("Deactivate"):
    try:
        res = requests.delete(f"{API_URL}/subscribers/{deactivate_id}")
        st.write("Status:", res.status_code)
        try:
            display_as_table(res.json())
        except:
            pass
    except Exception as e:
        st.error(f"Error: {e}")

st.header("Create SIM Card")
with st.form("create_sim"):
    iccid = st.text_input("ICCID")
    sim_sub_id = st.number_input("Subscriber ID to Attach", min_value=1, value=1)
    submit_sim = st.form_submit_button("Create SIM")
    if submit_sim:
        payload = {"iccid": iccid, "subscriber_id": sim_sub_id}
        try:
            res = requests.post(f"{API_URL}/sim/", json=payload)
            st.write("Status:", res.status_code)
            display_as_table(res.json())
        except Exception as e:
            st.error(f"Error: {e}")

st.header("Provision SIM Card Network")
with st.form("provision_sim"):
    prov_sim_id = st.number_input("SIM ID to Provision", min_value=1, value=1)
    submit_prov = st.form_submit_button("Provision")
    if submit_prov:
        try:
            res = requests.post(f"{API_URL}/sim/{prov_sim_id}/provision")
            st.write("Status:", res.status_code)
            try:
                display_as_table(res.json())
            except:
                pass
        except Exception as e:
            st.error(f"Error: {e}")
