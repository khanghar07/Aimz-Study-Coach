function section(title, content, collapsible = true) {
  const s = document.createElement("section");
  s.className = "result-section";

  if (collapsible) {
    s.classList.add("collapsible");
    const header = document.createElement("div");
    header.className = "section-header";
    const h = document.createElement("h3");
    h.textContent = title;
    const chev = document.createElement("span");
    chev.className = "chev";
    chev.textContent = "▾";
    header.appendChild(h);
    header.appendChild(chev);
    s.appendChild(header);

    const body = document.createElement("div");
    body.className = "section-body";
    body.appendChild(content);
    s.appendChild(body);

    header.addEventListener("click", () => {
      const collapsed = s.classList.toggle("collapsed");
      chev.textContent = collapsed ? "▸" : "▾";
    });
  } else {
    const h = document.createElement("h3");
    h.textContent = title;
    s.appendChild(h);
    s.appendChild(content);
  }
  return s;
}

function list(items) {
  const ul = document.createElement("ul");
  (items || []).forEach(i => {
    const li = document.createElement("li");
    li.textContent = i;
    ul.appendChild(li);
  });
  return ul;
}

function renderResults(json) {
  const wrap = document.createElement("div");

  const summary = document.createElement("p");
  summary.textContent = json.summary || "";
  wrap.appendChild(section("Summary", summary, false));

  wrap.appendChild(section("Key Concepts", list(json.key_concepts)));
  wrap.appendChild(section("Confusion Points", list(json.confusion_points)));

  const plan = document.createElement("div");
  (json.study_plan || []).forEach(step => {
    const card = document.createElement("div");
    card.className = "plan-step";
    card.innerHTML = `<strong>${step.time}</strong> - ${step.step}<div class="plan-goal">${step.goal}</div>`;
    plan.appendChild(card);
  });
  wrap.appendChild(section("Study Plan", plan));

  const flashcards = document.createElement("div");
  (json.flashcards || []).forEach(c => {
    const card = document.createElement("div");
    card.className = "flashcard";
    card.innerHTML = `<div class="q">${c.q}</div><div class="a">${c.a}</div>`;
    flashcards.appendChild(card);
  });
  wrap.appendChild(section("Flashcards", flashcards));

  const quiz = document.createElement("div");
  (json.quiz || []).forEach(q => {
    const card = document.createElement("div");
    card.className = "quiz";
    card.innerHTML = `<div class="q">${q.q}</div><div class="a">${q.a}</div><div class="exp">${q.explanation}</div>`;
    quiz.appendChild(card);
  });
  wrap.appendChild(section("Quiz", quiz));

  wrap.appendChild(section("Next Actions", list(json.next_actions)));

  if (json.weak_spot_radar) {
    const w = document.createElement("div");
    w.appendChild(section("Diagnostic Questions", list(json.weak_spot_radar.questions || [])));
    w.appendChild(section("Predicted Weak Topics", list(json.weak_spot_radar.predicted_weak_topics || [])));
    wrap.appendChild(section("Weak-Spot Radar", w));
  }

  if (json.exam_simulator) {
    const ex = document.createElement("div");
    (json.exam_simulator.sections || []).forEach(s => {
      const card = document.createElement("div");
      card.className = "plan-step";
      card.innerHTML = `<strong>${s.minutes} min</strong> - ${s.name}<div class="plan-goal">${s.description || ""}</div>`;
      ex.appendChild(card);
    });
    wrap.appendChild(section("Exam Day Simulator", ex));
  }

  wrap.appendChild(section("Mistake Library", list(json.mistake_library)));
  wrap.appendChild(section("Socratic Mode", list(json.socratic_mode)));

  if (json.rewritten_notes) {
    const rn = document.createElement("div");
    rn.appendChild(section("Clean Bullets", list(json.rewritten_notes.bullets || [])));
    rn.appendChild(section("Outline", list(json.rewritten_notes.outline || [])));
    wrap.appendChild(section("Rewrite Notes", rn));
  }

  wrap.appendChild(section("Memory Hooks", list(json.memory_hooks)));

  if (json.code_debug_coach) {
    const cd = document.createElement("div");
    (json.code_debug_coach || []).forEach(i => {
      const card = document.createElement("div");
      card.className = "quiz";
      card.innerHTML = `<div class="q">${i.issue}</div><div class="a">${i.fix}</div><div class="exp">${i.why}</div>`;
      cd.appendChild(card);
    });
    wrap.appendChild(section("Code Debug Coach", cd));
  }

  if (json.spaced_review_pack) {
    const sr = document.createElement("div");
    (json.spaced_review_pack || []).forEach(d => {
      const card = document.createElement("div");
      card.className = "plan-step";
      card.innerHTML = `<strong>${d.day}</strong> - ${d.focus}`;
      sr.appendChild(card);
    });
    wrap.appendChild(section("Spaced Review Pack", sr));
  }

  return wrap;
}

async function exportMarkdown(json) {
  const res = await fetch("/export/markdown", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(json)
  });
  const text = await res.text();
  const blob = new Blob([text], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "study-coach-report.md";
  a.click();
  URL.revokeObjectURL(url);
}

async function exportPdf(json) {
  const res = await fetch("/export/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(json)
  });
  if (!res.ok) {
    const err = await res.text();
    alert("PDF export failed: " + err);
    return;
  }
  const blob = await res.blob();
  if (!blob || blob.size === 0) {
    alert("PDF export returned empty file.");
    return;
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "study-coach-report.pdf";
  a.click();
  URL.revokeObjectURL(url);
}

async function shareReport(json) {
  const res = await fetch("/share", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(json)
  });
  return await res.json();
}
