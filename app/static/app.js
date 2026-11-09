const form = document.querySelector("#form");
const result = document.querySelector("#result");
let latest = null;

function downloadCsv() {
  const rows = [
    ["구성", "제조사", "모델", "사양", "참고 가격"],
    ...latest.parts.map((part) => [
      part.category,
      part.maker,
      part.model,
      part.spec,
      part.price,
    ]),
  ];
  const csv =
    "\ufeff" +
    rows
      .map((row) =>
        row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","),
      )
      .join("\n");
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  link.download = "buildmypc-estimate.csv";
  link.click();
  URL.revokeObjectURL(link.href);
}

function renderRecommendation(estimate) {
  const parts = estimate.parts
    .map(
      (part) => `
        <article class="card">
          <span class="muted">${part.category} · ${part.maker}</span>
          <h3>${part.model}</h3>
          <p class="muted">${part.spec}</p>
          <div class="price">${part.price.toLocaleString()}원</div>
        </article>`,
    )
    .join("");
  const checks = estimate.compatibility
    .map(
      (check) =>
        `<p><b>${check.status}</b> ${check.item} <span class="muted">(${check.detail})</span></p>`,
    )
    .join("");
  const warnings = estimate.warnings
    .map((warning) => `<p class="warning">${warning}</p>`)
    .join("");

  result.innerHTML = `
    <div class="summary">
      <h2>추천 견적</h2>
      <p>${estimate.reason}</p>
      <strong>총 예상 비용: ${estimate.total.toLocaleString()}원</strong>
      <p>예산 ${estimate.balance >= 0 ? "잔액" : "초과"}: ${Math.abs(estimate.balance).toLocaleString()}원</p>
      <button id="copy" type="button">견적 내용 복사</button>
      <button id="csv" type="button" class="secondary">CSV 다운로드</button>
    </div>
    ${warnings}
    <div class="cards">${parts}</div>
    <section class="compat">
      <h3>호환성 검사</h3>
      ${checks}
    </section>
    <p class="muted">${estimate.source_note}</p>`;

  document.querySelector("#copy").addEventListener("click", async () => {
    const text = estimate.parts
      .map(
        (part) =>
          `${part.category}: ${part.model} - ${part.price.toLocaleString()}원`,
      )
      .join("\n");
    await navigator.clipboard.writeText(
      `${text}\n총액: ${estimate.total.toLocaleString()}원`,
    );
  });
  document.querySelector("#csv").addEventListener("click", downloadCsv);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.innerHTML = "<p>조건에 맞는 구성을 계산하고 있습니다...</p>";
  const data = Object.fromEntries(new FormData(form));
  data.include = [...form.querySelectorAll("[name=include]:checked")].map(
    (input) => input.value,
  );
  for (const key of ["budget", "memory", "storage"]) {
    data[key] = Number(data[key]);
  }

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const body = await response.json();
      throw new Error(body.detail?.[0]?.msg ?? "입력값을 확인해 주세요.");
    }
    latest = await response.json();
    renderRecommendation(latest);
  } catch (error) {
    result.innerHTML = `<p class="error">${error.message}</p>`;
  }
});
