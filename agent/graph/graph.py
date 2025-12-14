from __future__ import annotations

import os
import tempfile
import streamlit as st

from graph import app  # Option 2: requires graph/__init__.py exporting app


st.set_page_config(page_title="AI Data Analysis Agent", layout="wide")
st.title("AI Data Analysis Agent (LangGraph Flow)")

if "chat" not in st.session_state:
    st.session_state.chat = []
if "dataset_path" not in st.session_state:
    st.session_state.dataset_path = None
if "previous_plan" not in st.session_state:
    st.session_state.previous_plan = None
if "dataset_fingerprint" not in st.session_state:
    st.session_state.dataset_fingerprint = None


with st.expander("Agent Flow Graph", expanded=False):
    try:
        st.image(app.get_graph().draw_mermaid_png(), caption="Agent Flow (LangGraph)")
    except Exception as e:
        st.warning(
            "Graph PNG render failed (often due to network restrictions for Mermaid rendering). "
            "Showing Mermaid source instead."
        )
        try:
            mermaid_src = app.get_graph().draw_mermaid()
            st.code(mermaid_src, language="mermaid")
        except Exception:
            st.error(f"Graph render failed: {e}")


uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded:
    tmp_dir = tempfile.gettempdir()
    path = os.path.join(tmp_dir, uploaded.name)

    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())

    fingerprint = f"{uploaded.name}:{uploaded.size}"

    # New dataset => reset chat + memory
    if st.session_state.dataset_fingerprint != fingerprint:
        st.session_state.dataset_fingerprint = fingerprint
        st.session_state.dataset_path = path
        st.session_state.chat = []
        st.session_state.previous_plan = None
    else:
        st.session_state.dataset_path = path


if not st.session_state.dataset_path:
    st.info("Upload a CSV to start.")
    st.stop()

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Clear chat"):
        st.session_state.chat = []
        st.session_state.previous_plan = None
        st.rerun()
with col2:
    show_plan = st.toggle("Show plan/debug", value=True)
with col3:
    show_schema = st.toggle("Show schema output", value=False)


preview = {}
try:
    preview_out = app.invoke(
        {
            "dataset_path": st.session_state.dataset_path,
            "question": None,
            "preview_only": True,
            "previous_plan": st.session_state.previous_plan,
        }
    )
    preview = preview_out.get("result", {}) or {}
except Exception as e:
    preview = {"error": f"Schema preview failed: {e}"}

with st.expander("Dataset schema preview", expanded=False):
    if preview.get("error"):
        st.error(preview["error"])
    elif "schema" in preview:
        st.json(preview["schema"])
    else:
        st.info("Schema preview not available.")


for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg["role"] == "assistant" and msg.get("result"):
            res = msg["result"]

            # confidence
            if "confidence" in res:
                try:
                    st.metric("Confidence", f"{float(res['confidence']):.2f}")
                except Exception:
                    st.metric("Confidence", str(res["confidence"]))

            # plan
            if show_plan and "plan" in res:
                with st.expander("Plan", expanded=False):
                    st.json(res["plan"])

            # schema output (from data_quality etc.)
            if show_schema and "schema" in res:
                with st.expander("Schema output", expanded=False):
                    st.json(res["schema"])

            # result table
            if "result_df" in res:
                st.dataframe(res["result_df"], use_container_width=True)

            # chart
            if "fig" in res:
                st.pyplot(res["fig"], clear_figure=True)

            if "figure_path" in res:
                st.caption(f"Saved chart: {res['figure_path']}")

            # explanation / error
            if res.get("explanation"):
                st.caption(res["explanation"])
            if res.get("error"):
                st.error(res["error"])


prompt = st.chat_input("Ask: 'any duplicate rows?' or 'plot revenue by region'")
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})

    try:
        out = app.invoke(
            {
                "dataset_path": st.session_state.dataset_path,
                "question": prompt,
                "preview_only": False,
                "previous_plan": st.session_state.previous_plan,
            }
        )
        result = out.get("result", {}) or {}

        # memory update returned in state
        st.session_state.previous_plan = out.get("previous_plan", st.session_state.previous_plan)

    except Exception as e:
        # hard failure: show it as a structured result
        result = {"error": f"Graph execution failed: {e}", "confidence": 0.0}

    # assistant message
    if "error" in result:
        st.session_state.chat.append(
            {"role": "assistant", "content": "I hit an error. Here’s the detail:", "result": result}
        )
    else:
        st.session_state.chat.append(
            {"role": "assistant", "content": "Here’s what I found:", "result": result}
        )

    st.rerun()
