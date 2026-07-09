# app.py

import os
import subprocess
from pathlib import Path

import streamlit as st


def safe_name(name: str) -> str:
    return name.replace("/", "_").replace("-", "_").replace(" ", "_")


@st.dialog("Diagnostic Report")
def show_report(report_text: str):
    st.markdown(report_text)


def run_command(command: list[str]):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
    )


st.set_page_config(
    page_title="Accent Stress Test Lab",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Accent Stress Test Lab")
st.caption(
    "Quickly profile an ASR model across accent-sensitive and meaning-critical failure modes."
)

st.divider()

left, right = st.columns([1, 1])

with left:
    st.subheader("1. Choose model")

    provider_label = st.selectbox(
        "Provider",
        ["Hugging Face", "OpenAI"],
    )

    provider = {
        "Hugging Face": "hf",
        "OpenAI": "openai",
    }[provider_label]

    if provider == "hf":
        model_id = st.text_input(
            "Hugging Face model ID",
            value="openai/whisper-small",
        )
        model_name = st.text_input(
            "Display name",
            value=safe_name(model_id),
        )
        openai_api_key = None

    else:
        model_id = st.text_input(
            "OpenAI transcription model",
            value="gpt-4o-mini-transcribe",
        )
        model_name = st.text_input(
            "Display name",
            value=safe_name(model_id),
        )
        openai_api_key = st.text_input(
            "OpenAI API key",
            type="password",
            help="Your key is only used for this run and is not saved.",
        )

with right:
    st.subheader("2. Choose diagnostic set")

    cards_path = st.text_input(
        "Test cards path",
        value="data/final/test_cards.json",
    )

    st.info(
        "This runs the selected ASR model over a curated stress-test set, "
        "then reports the model's likely failure areas with examples."
    )

st.divider()

run_button = st.button(
    "Run diagnostic",
    type="primary",
    use_container_width=True,
)

if "latest_report_path" not in st.session_state:
    st.session_state.latest_report_path = None

if "latest_report_text" not in st.session_state:
    st.session_state.latest_report_text = None


if run_button:
    if provider == "openai" and not openai_api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()

    if provider == "openai":
        os.environ["OPENAI_API_KEY"] = openai_api_key

    safe_model = safe_name(model_name)

    predictions_path = f"results/predictions_{provider}_{safe_model}.json"
    report_path = f"reports/diagnostic_{provider}_{safe_model}.md"

    progress = st.progress(0)
    status = st.empty()

    status.info("Running ASR model...")
    progress.progress(20)

    run_asr_command = [
        "python",
        "scripts/run_asr.py",
        "--provider",
        provider,
        "--model_id",
        model_id,
        "--model_name",
        model_name,
        "--cards",
        cards_path,
        "--out",
        predictions_path,
    ]

    result = run_command(run_asr_command)

    if result.returncode != 0:
        progress.progress(0)
        status.error("ASR run failed.")
        st.code(result.stderr)
        st.stop()

    progress.progress(75)
    status.info("Evaluating predictions...")

    evaluate_command = [
        "python",
        "scripts/evaluate.py",
        "--preds",
        predictions_path,
        "--refs",
        cards_path,
        "--out",
        report_path,
    ]

    result = run_command(evaluate_command)

    if result.returncode != 0:
        progress.progress(0)
        status.error("Evaluation failed.")
        st.code(result.stderr)
        st.stop()

    report_file = Path(report_path)

    if not report_file.exists():
        progress.progress(0)
        status.error(f"Report file was not created: {report_path}")
        st.stop()

    report_text = report_file.read_text(encoding="utf-8")

    st.session_state.latest_report_path = report_path
    st.session_state.latest_report_text = report_text

    progress.progress(100)
    status.success("Diagnostic complete.")


if st.session_state.latest_report_text:
    st.success("A diagnostic report is ready.")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("View failure profile", use_container_width=True):
            show_report(st.session_state.latest_report_text)

    with col2:
        st.download_button(
            "Download report",
            data=st.session_state.latest_report_text,
            file_name=Path(st.session_state.latest_report_path).name,
            mime="text/markdown",
            use_container_width=True,
        )