from __future__ import annotations

import shlex

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


def _quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _compose_yaml(service_name: str, image: str, command: list[str], ports: list[str], env: list[str], volumes: list[str], restart: str, network: str) -> str:
    lines = ["services:", f"  {service_name}:", f"    image: {_quote_yaml(image)}"]
    if command:
        lines.append("    command:")
        lines.extend(f"      - {_quote_yaml(part)}" for part in command)
    if ports:
        lines.append("    ports:")
        lines.extend(f"      - {_quote_yaml(item)}" for item in ports)
    if env:
        lines.append("    environment:")
        lines.extend(f"      - {_quote_yaml(item)}" for item in env)
    if volumes:
        lines.append("    volumes:")
        lines.extend(f"      - {_quote_yaml(item)}" for item in volumes)
    if restart:
        lines.append(f"    restart: {_quote_yaml(restart)}")
    if network:
        lines.extend(["    networks:", f"      - {_quote_yaml(network)}", "", "networks:", f"  {network}:", "    external: true"])
    return "\n".join(lines)


def convert_docker_run_to_compose(command_text: str, service_name: str) -> dict[str, str | bool]:
    text = (command_text or "").strip()
    if not text:
        return {"ok": False, "error": "Enter a docker run command.", "output": ""}
    try:
        tokens = shlex.split(text)
    except ValueError as exc:
        return {"ok": False, "error": f"Unable to parse command: {exc}", "output": ""}
    if len(tokens) < 3 or tokens[0:2] != ["docker", "run"]:
        return {"ok": False, "error": "Command must start with `docker run`.", "output": ""}

    image = ""
    trailing_command: list[str] = []
    ports: list[str] = []
    env: list[str] = []
    volumes: list[str] = []
    restart = ""
    network = ""
    i = 2
    while i < len(tokens):
        token = tokens[i]
        if token in {"-p", "--publish"} and i + 1 < len(tokens):
            ports.append(tokens[i + 1])
            i += 2
            continue
        if token in {"-e", "--env"} and i + 1 < len(tokens):
            env.append(tokens[i + 1])
            i += 2
            continue
        if token in {"-v", "--volume"} and i + 1 < len(tokens):
            volumes.append(tokens[i + 1])
            i += 2
            continue
        if token == "--restart" and i + 1 < len(tokens):
            restart = tokens[i + 1]
            i += 2
            continue
        if token == "--network" and i + 1 < len(tokens):
            network = tokens[i + 1]
            i += 2
            continue
        if token == "--name" and i + 1 < len(tokens):
            i += 2
            continue
        if token.startswith("-"):
            i += 1
            continue
        image = token
        trailing_command = tokens[i + 1 :]
        break

    if not image:
        return {"ok": False, "error": "Could not find an image in the docker run command.", "output": ""}

    output = _compose_yaml((service_name or "app").strip() or "app", image, trailing_command, ports, env, volumes, restart, network)
    return {"ok": True, "error": "", "output": output}


_baseline = start_page_baseline("Docker Run to Compose")
st.set_page_config(page_title="Docker Run to Compose", layout="wide")
apply_app_shell(active_page="Docker Run to Compose")
mark_page_baseline(_baseline, "shell-ready")

render_page_header(
    "Docker Run to Compose",
    "Convert a docker run command into a starter docker-compose service block.",
)

with tool_form_panel("docker_run_to_compose"):
    render_form_intro("Paste command and choose service name", "Grouped controls keep the conversion flow readable on phones and desktops.")
    with st.form("docker-run-to-compose-form"):
        st.markdown('<div class="tool-panel-eyebrow">Docker run command</div>', unsafe_allow_html=True)
        command_input = st.text_area("Docker command", height=180, placeholder="docker run -p 8080:80 --name web nginx:latest")
        st.markdown('<div class="tool-panel-eyebrow">Compose service name</div>', unsafe_allow_html=True)
        service_name_input = st.text_input("Service name", value="app")
        submitted = st.form_submit_button("Convert to compose", use_container_width=True)

if submitted:
    st.session_state["docker_run_to_compose_result"] = convert_docker_run_to_compose(command_input, service_name_input)

result = st.session_state.get("docker_run_to_compose_result")
if result is None:
    render_empty_state("Ready to convert", "Compose YAML appears here after conversion.")
    render_status_note(
        "Awaiting docker run command",
        "Paste a docker run command and select Convert to compose to generate a starter Compose service block.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("docker_run_to_compose_result", related_to="docker_run_to_compose"):
        render_section_heading("Compose output", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: command validation required", str(result["error"]), tone="warning")
        else:
            render_status_note("Outcome: compose YAML generated", "Review and adapt this starter service block for your stack.", tone="success")
            st.code(str(result["output"]), language="yaml")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
