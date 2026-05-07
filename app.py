import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Patient Zero - Telecom Subscriber Management")

agent = st.selectbox("Select Agent", ["Agent A", "Agent B", "Admin"])
st.write(f"Logged in as: {agent}")

if st.button("Seed Initial Data (Run Once)"):
    try:
        res = requests.post(f"{API_URL}/seed")
        st.write(res.json())
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
            st.write("Response:", res.json())
        except Exception as e:
            st.error(f"Error: {e}")

st.header("Search Subscriber")
search_id = st.number_input("Subscriber ID to Search", min_value=1, value=1)
if st.button("Search"):
    try:
        res = requests.get(f"{API_URL}/subscribers/{search_id}")
        st.write("Status:", res.status_code)
        try:
            st.write("Response:", res.json())
        except:
            st.write("Failed to parse response")
    except Exception as e:
        st.error(f"Error: {e}")

st.header("Update Plan Quota")
with st.form("update_plan"):
    update_id = st.number_input("Subscriber ID to Update", min_value=1, value=1)
    # Bug 2: Streamlit UI sends quota_gb as a string
    quota_gb_input = st.text_input("New Quota (GB)", value="10")
    submit_update = st.form_submit_button("Update")
    if submit_update:
        # Intentionally passing string to trigger 422 in FastAPI
        payload = {"quota_gb": quota_gb_input + " GB"} 
        try:
            res = requests.put(f"{API_URL}/subscribers/{update_id}/plan", json=payload)
            st.write("Status:", res.status_code)
            try:
                st.write("Response:", res.json())
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
            st.write("Response:", res.json())
        except:
            pass
    except Exception as e:
        st.error(f"Error: {e}")
