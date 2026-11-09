import json
from pathlib import Path
from typing import Any

from .compatibility import check_compatibility
from .models import RecommendationRequest

PRODUCTS: list[dict[str, Any]] = json.loads(
    (Path(__file__).parent / "data" / "products.json").read_text(encoding="utf-8")
)


def _products(category: str, **filters: Any) -> list[dict[str, Any]]:
    return [
        product
        for product in PRODUCTS
        if product["category"] == category
        and all(product.get(key) == value for key, value in filters.items())
    ]


def _choose_storage(requested_capacity: int) -> tuple[dict[str, Any], bool]:
    options = sorted(_products("SSD"), key=lambda product: product["price"])
    matching = [
        product
        for product in options
        if product.get("capacity", 0) >= requested_capacity
    ]
    if matching:
        return matching[0], False
    return max(options, key=lambda product: product.get("capacity", 0)), True


def recommend(request: RecommendationRequest) -> dict[str, Any]:
    cpu_choices = _products("CPU")
    if request.cpu_preference != "any":
        cpu_choices = [
            cpu for cpu in cpu_choices if cpu["maker"] == request.cpu_preference
        ]
    cpus = sorted(cpu_choices, key=lambda product: product["performance"])
    if not cpus:
        raise ValueError(f"No CPU products available for {request.cpu_preference}")

    cpu = cpus[0]
    productivity_purposes = {"dev", "creative", "ai"}
    if request.purpose in productivity_purposes and request.budget >= 1_200_000:
        cpu = cpus[-1]

    gpu_choices = _products("GPU")
    if request.gpu_preference != "any":
        gpu_choices = [
            gpu for gpu in gpu_choices if gpu["gpu_brand"] == request.gpu_preference
        ]
    if not gpu_choices:
        raise ValueError(f"No GPU products available for {request.gpu_preference}")

    target_power = {"1080p": 2, "1440p": 3, "4K": 4}[request.resolution]
    gpu = min(
        gpu_choices,
        key=lambda product: abs(product["power"] / 60 - target_power),
    )
    if request.budget >= 1_500_000 and request.resolution != "1080p":
        gpu = max(gpu_choices, key=lambda product: product["price"])

    boards = _products("메인보드", socket=cpu["socket"])
    if not boards:
        raise ValueError(f"No motherboard available for socket {cpu['socket']}")
    board = boards[0]

    ram_choices = sorted(
        (
            ram
            for ram in _products("RAM", memory=board["memory"])
            if ram["capacity"] >= request.memory
        ),
        key=lambda product: product["price"],
    )
    if not ram_choices:
        raise ValueError(
            f"No {board['memory']} RAM product available for {request.memory}GB"
        )
    ram = ram_choices[0]

    storage, storage_shortfall = _choose_storage(request.storage)
    cooler = next(
        (
            product
            for product in _products("CPU 쿨러")
            if cpu["socket"] in product.get("sockets", [])
        ),
        None,
    )
    if cooler is None:
        raise ValueError(f"No compatible cooler available for socket {cpu['socket']}")

    parts = [
        cpu,
        cooler,
        board,
        ram,
        gpu,
        storage,
        _products("파워")[0],
        _products("케이스")[0],
    ]
    optional_parts = []
    if "monitor" in request.include:
        optional_parts.append(
            {
                "category": "모니터",
                "maker": "BuildMyPC",
                "model": "24인치 FHD 100Hz 모니터",
                "spec": "24인치 / 1920x1080 / 100Hz (예시 구성)",
                "price": 150_000,
            }
        )
    if "keyboard" in request.include:
        optional_parts.append(
            {
                "category": "키보드·마우스",
                "maker": "BuildMyPC",
                "model": "기본 키보드·마우스 세트",
                "spec": "유선 입력장치 세트 (예시 구성)",
                "price": 30_000,
            }
        )

    total = sum(part["price"] for part in parts + optional_parts)
    warnings = []
    if storage_shortfall:
        warnings.append(
            f"요청한 {request.storage}GB 제품이 없어 "
            f"{storage['capacity']}GB 참고 제품을 표시했습니다."
        )
    if total > request.budget:
        warnings.append(
            "현재 제품 데이터 기준으로 예산을 초과합니다. "
            "GPU·메모리·주변기기 조건을 조정해 주세요."
        )

    return {
        "parts": parts + optional_parts,
        "total": total,
        "budget": request.budget,
        "balance": request.budget - total,
        "compatibility": check_compatibility(parts),
        "warnings": warnings,
        "source_note": (
            "가격은 2026-11-02 기준 기능 시연용 수동 관리 참고 가격이며 "
            "실시간 판매가가 아닙니다."
        ),
        "reason": (
            f"{request.resolution} 해상도와 {request.purpose} 목적을 기준으로 "
            "CPU·GPU 성능과 예산을 균형 있게 배분했습니다."
        ),
    }
