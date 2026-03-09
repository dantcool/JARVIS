import requests
import re
import time


_AUTO_SELECTED_MODEL = None
_LAST_USED_MODEL = None
_AVAILABLE_MODELS_CACHE = None
_AVAILABLE_MODELS_CACHE_TS = 0.0
_AVAILABLE_MODELS_TTL_SECONDS = 60.0


def _coerce_timeout_pair(timeout, connect_timeout=None):
    # requests accepts either a float or a (connect, read) tuple.
    try:
        read_timeout = float(timeout)
    except Exception:
        read_timeout = 120.0

    if connect_timeout is None:
        connect_timeout = min(5.0, read_timeout)

    try:
        connect_timeout = float(connect_timeout)
    except Exception:
        connect_timeout = 5.0

    return (max(0.5, connect_timeout), max(1.0, read_timeout))


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


def _get_available_models_cached(base_url, timeout):
    global _AVAILABLE_MODELS_CACHE, _AVAILABLE_MODELS_CACHE_TS
    now = time.time()
    if _AVAILABLE_MODELS_CACHE is not None and (now - _AVAILABLE_MODELS_CACHE_TS) < _AVAILABLE_MODELS_TTL_SECONDS:
        return _AVAILABLE_MODELS_CACHE

    models = _fetch_available_models(base_url, timeout)
    _AVAILABLE_MODELS_CACHE = models
    _AVAILABLE_MODELS_CACHE_TS = now
    return models


def list_available_models(base_url="http://127.0.0.1:11434", timeout=5):
    timeout_pair = _coerce_timeout_pair(timeout, connect_timeout=min(timeout, 5))
    models = _get_available_models_cached(base_url, timeout_pair)
    return [model.get("name") for model in models if model.get("name")]


def get_last_used_model():
    return _LAST_USED_MODEL


def check_ollama_health(base_url="http://127.0.0.1:11434", timeout=2.5):
    timeout_pair = _coerce_timeout_pair(timeout, connect_timeout=timeout)
    try:
        models = _fetch_available_models(base_url, timeout_pair)
        return True, f"Connected to Ollama. Models available: {len(models)}"
    except Exception as error:
        return False, f"Could not reach Ollama at {base_url}: {error}"


def _normalize_model_name(name):
    return (name or "").strip().lower()


def _classify_prompt_complexity(prompt):
    text = (prompt or "").strip().lower()
    words = re.findall(r"\w+", text)
    word_count = len(words)

    fast_markers = [
        "quick",
        "brief",
        "one sentence",
        "short answer",
        "yes or no",
        "what time",
        "what day",
    ]
    deep_markers = [
        "step-by-step",
        "analyze",
        "architecture",
        "tradeoff",
        "compare",
        "design",
        "debug",
        "root cause",
        "explain why",
    ]

    if any(marker in text for marker in fast_markers) or word_count <= 8:
        return "fast"

    if any(marker in text for marker in deep_markers) or word_count >= 40:
        return "deep"

    return "balanced"


def _rank_models_ascending(models):
    return sorted(
        models,
        key=lambda model: (
            _parse_parameter_size_to_billions((model.get("details") or {}).get("parameter_size")),
            float(model.get("size") or 0),
            model.get("name", ""),
        ),
    )


def _resolve_model_for_prompt(
    base_url,
    configured_model,
    timeout,
    auto_select_model,
    auto_route_by_prompt,
    prompt,
    model_candidates=None,
):
    if not auto_route_by_prompt:
        return resolve_best_model(
            base_url=base_url,
            configured_model=configured_model,
            timeout=timeout,
            auto_select=auto_select_model,
        )

    models = _get_available_models_cached(base_url, timeout)
    if not models:
        return configured_model

    installed_by_name = {
        _normalize_model_name(model.get("name")): model
        for model in models
        if model.get("name")
    }

    candidate_models = []
    if model_candidates:
        for candidate in model_candidates:
            candidate_key = _normalize_model_name(candidate)
            if candidate_key in installed_by_name:
                candidate_models.append(installed_by_name[candidate_key])

    if not candidate_models:
        candidate_models = models

    ranked = _rank_models_ascending(candidate_models)
    if not ranked:
        return configured_model

    complexity = _classify_prompt_complexity(prompt)
    if complexity == "fast":
        selected = ranked[0].get("name")
    elif complexity == "deep":
        selected = ranked[-1].get("name")
    else:
        selected = ranked[len(ranked) // 2].get("name")

    if selected:
        print(f"Jarvis: prompt complexity={complexity}; routed model={selected}")
        return selected

    return configured_model


def preview_routed_model(
    prompt,
    model="llama3.2",
    base_url="http://127.0.0.1:11434",
    timeout=120,
    auto_select_model=True,
    auto_route_by_prompt=True,
    model_candidates=None,
    connect_timeout=5,
    model_discovery_timeout=5,
):
    request_timeout = _coerce_timeout_pair(timeout, connect_timeout=connect_timeout)
    discovery_timeout = _coerce_timeout_pair(model_discovery_timeout, connect_timeout=connect_timeout)
    return _resolve_model_for_prompt(
        base_url=base_url,
        configured_model=model,
        timeout=discovery_timeout,
        auto_select_model=auto_select_model,
        auto_route_by_prompt=auto_route_by_prompt,
        prompt=prompt,
        model_candidates=model_candidates,
    )


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
    auto_route_by_prompt=True,
    model_candidates=None,
    connect_timeout=5,
    model_discovery_timeout=5,
):
    global _LAST_USED_MODEL
    request_timeout = _coerce_timeout_pair(timeout, connect_timeout=connect_timeout)
    discovery_timeout = _coerce_timeout_pair(model_discovery_timeout, connect_timeout=connect_timeout)

    model = _resolve_model_for_prompt(
        base_url=base_url,
        configured_model=model,
        timeout=discovery_timeout,
        auto_select_model=auto_select_model,
        auto_route_by_prompt=auto_route_by_prompt,
        prompt=prompt,
        model_candidates=model_candidates,
    )
    _LAST_USED_MODEL = model

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
            timeout=request_timeout,
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
        timeout=request_timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()
