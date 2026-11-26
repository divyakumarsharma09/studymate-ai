import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 120


def get_json(path: str):
    response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def post_json(path: str, payload: dict):
    response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def upload_pdf(filename: str, data: bytes):
    response = requests.post(
        f"{BASE_URL}/upload-pdf",
        files={"file": (filename, data, "application/pdf")},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def post_image(filename: str, data: bytes, mime_type: str, task: str, question: str):
    response = requests.post(
        f"{BASE_URL}/image",
        files={"file": (filename, data, mime_type)},
        data={"task": task, "question": question},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def error_detail(error: requests.RequestException) -> str:
    response = getattr(error, "response", None)
    if response is not None:
        try:
            return str(response.json().get("detail", "The request failed"))
        except ValueError:
            return "The request failed"
    return "Cannot reach the backend"