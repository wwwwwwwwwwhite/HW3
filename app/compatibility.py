def check_compatibility(parts: list[dict]) -> list[dict[str, str]]:
    by_category = {part["category"]: part for part in parts}
    checks = []

    cpu = by_category.get("CPU")
    board = by_category.get("메인보드")
    if cpu and board:
        cpu_socket = cpu.get("socket")
        board_socket = board.get("socket")
        checks.append(
            {
                "item": "CPU 소켓 ↔ 메인보드",
                "status": "확인" if cpu_socket == board_socket else "불일치",
                "detail": f"{cpu_socket} / {board_socket}",
            }
        )

    ram = by_category.get("RAM")
    if board and ram:
        board_memory = board.get("memory")
        ram_memory = ram.get("memory")
        checks.append(
            {
                "item": "메모리 규격",
                "status": "확인" if board_memory == ram_memory else "불일치",
                "detail": f"{board_memory} / {ram_memory}",
            }
        )

    case = by_category.get("케이스")
    gpu = by_category.get("GPU")
    if case and gpu:
        gpu_length = gpu.get("length", 0)
        case_gpu_limit = case.get("gpu_max_length", 0)
        checks.append(
            {
                "item": "GPU 길이 ↔ 케이스",
                "status": "확인" if gpu_length <= case_gpu_limit else "불일치",
                "detail": f"{gpu_length}mm / {case_gpu_limit}mm",
            }
        )

    cooler = by_category.get("CPU 쿨러")
    if cpu and cooler:
        supported_sockets = cooler.get("sockets", [])
        cpu_socket = cpu.get("socket")
        checks.append(
            {
                "item": "CPU 소켓 ↔ 쿨러",
                "status": "확인" if cpu_socket in supported_sockets else "불일치",
                "detail": f"{cpu_socket} / {', '.join(supported_sockets)}",
            }
        )
    if case and cooler:
        cooler_height = cooler.get("height", 0)
        case_cooler_limit = case.get("cooler_max_height", 0)
        checks.append(
            {
                "item": "쿨러 높이 ↔ 케이스",
                "status": "확인" if cooler_height <= case_cooler_limit else "불일치",
                "detail": f"{cooler_height}mm / {case_cooler_limit}mm",
            }
        )

    psu = by_category.get("파워")
    if psu and gpu:
        estimated_power = gpu.get("power", 0) + 300
        psu_wattage = psu.get("wattage", 0)
        checks.append(
            {
                "item": "예상 소비전력 ↔ 파워",
                "status": "확인" if psu_wattage >= estimated_power else "정보 부족",
                "detail": f"예상 {estimated_power}W / 파워 {psu_wattage}W",
            }
        )

    return checks
