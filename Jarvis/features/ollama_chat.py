import requests
import re


_AUTO_SELECTED_MODEL = None


def _parse_parameter_size_to_billions(parameter_size):
    if not parameter_size:
        return -1.0
    text = str(parameter_size).strip().upper()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([BM])", text)
    if not match:
        return -1.0
    value = float(match.group(1))
    unit = match.group(2)
    if unit == "M":
        return value / 1000.0
    return value


def _fetch_available_models(base_url, timeout):
    response = requests.get(f"{base_url}/api/tags", timeout=timeout)
    response.raise_for_status()
    data = response.json() or {}
    return data.get("models", [])


def resolve_best_model(base_url, configured_model, timeout=120, auto_select=True):
    global _AUTO_SELECTED_MODEL

    if not auto_select:
        return configured_model

    if _AUTO_SELECTED_MODEL:
        return _AUTO_SELECTED_MODEL

    try:
        models = _fetch_available_models(base_url, timeout)
        if not models:
            _AUTO_SELECTED_MODEL = configured_model
            return _AUTO_SELECTED_MODEL

        names = [model.get("name", "") for model in models if model.get("name")]
        if configured_model in names:
            _AUTO_SELECTED_MODEL = configured_model
            return _AUTO_SELECTED_MODEL

        ranked = sorted(
            models,
            key=lambda model: (
                _parse_parameter_size_to_billions((model.get("details") or {}).get("parameter_size")),
                float(model.get("size") or 0),
                model.get("name", ""),
            ),
            reverse=True,
        )
        _AUTO_SELECTED_MODEL = ranked[0].get("name") or configured_model
        print(f"Jarvis: auto-selected Ollama model: {_AUTO_SELECTED_MODEL}")
        return _AUTO_SELECTED_MODEL
    except Exception as error:
        print(f"Jarvis: model auto-select failed, using configured model ({configured_model}). Error: {error}")
        _AUTO_SELECTED_MODEL = configured_model
        return _AUTO_SELECTED_MODEL


def ask_ollama(
    prompt,
    model="llama3.2",
    base_url="http://127.0.0.1:11434",
    system_prompt="You are Jarvis, a concise and helpful local AI assistant.",
    timeout=120,
    num_gpu=-1,
    num_ctx=8192,
    temperature=0.6,
    num_thread=0,
    auto_select_model=True,
):
    model = resolve_best_model(
        base_url=base_url,
        configured_model=model,
        timeout=timeout,
        auto_select=auto_select_model,
    )

    options = {
        "num_gpu": num_gpu,
        "num_ctx": num_ctx,
        "temperature": temperature,
        "num_thread": num_thread,
    }

    chat_payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": options,
    }

    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()
    except requests.HTTPError as error:
        if error.response is None or error.response.status_code != 404:
            raise

    generate_payload = {
        "model": model,
        "prompt": f"{system_prompt}\n\nUser: {prompt}\nAssistant:",
        "stream": False,
        "options": options,
    }
    response = requests.post(
        f"{base_url}/api/generate",
        json=generate_payload,
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()
