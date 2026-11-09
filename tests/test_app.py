from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def payload(**extra):
    data = {
        "budget": 1_200_000,
        "purpose": "game",
        "resolution": "1080p",
        "cpu_preference": "any",
        "gpu_preference": "any",
        "memory": 32,
        "storage": 1000,
    }
    data.update(extra)
    return data


def test_recommendation_has_expected_parts_and_total():
    response = client.post("/api/recommend", json=payload())

    assert response.status_code == 200
    body = response.json()
    assert len(body["parts"]) == 8
    assert body["total"] == sum(part["price"] for part in body["parts"])
    assert body["compatibility"]


def test_invalid_budget_is_rejected():
    response = client.post("/api/recommend", json=payload(budget=0))

    assert response.status_code == 422


def test_invalid_memory_choice_is_rejected():
    response = client.post("/api/recommend", json=payload(memory=48))

    assert response.status_code == 422


def test_front_page_and_static_assets_load():
    assert client.get("/").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "BuildMyPC"}


def test_optional_items_are_included_and_priced():
    body = client.post(
        "/api/recommend",
        json=payload(include=["monitor", "keyboard"]),
    ).json()

    categories = [part["category"] for part in body["parts"]]
    assert "모니터" in categories
    assert "키보드·마우스" in categories
    assert body["total"] == sum(part["price"] for part in body["parts"])


def test_compatibility_checks_cover_cpu_ram_gpu_and_power():
    body = client.post("/api/recommend", json=payload()).json()
    checks = {check["item"]: check["status"] for check in body["compatibility"]}

    assert checks["CPU 소켓 ↔ 메인보드"] == "확인"
    assert checks["메모리 규격"] == "확인"
    assert checks["GPU 길이 ↔ 케이스"] == "확인"
    assert checks["예상 소비전력 ↔ 파워"] == "확인"


def test_requested_memory_and_storage_are_met():
    body = client.post(
        "/api/recommend",
        json=payload(budget=2_500_000, memory=64, storage=2000),
    ).json()
    parts = {part["category"]: part for part in body["parts"]}

    assert parts["RAM"]["capacity"] == 64
    assert parts["SSD"]["capacity"] == 2000
    assert body["warnings"] == []


def test_brand_preferences_are_respected():
    body = client.post(
        "/api/recommend",
        json=payload(cpu_preference="Intel", gpu_preference="NVIDIA"),
    ).json()
    parts = {part["category"]: part for part in body["parts"]}

    assert parts["CPU"]["maker"] == "Intel"
    assert parts["GPU"]["gpu_brand"] == "NVIDIA"
