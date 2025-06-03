# streamlit_app.py

import streamlit as st
import requests
import json

st.title("Internal AI Assistant Query")

# Input box for user query
user_query = st.text_input("Enter your query:", "How to make upload 99% bug?")

if st.button("Submit"):
    url = "http://localhost:8000/api/v1/query"
    payload = {"query": user_query}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            parsed = json.loads(data["response"])
            st.subheader("LLM Reasoning:")
            st.write(parsed.get("reasoning", "No reasoning provided."))
            st.subheader("Answer:")
            st.write(parsed.get("response", "No response provided."))
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")
