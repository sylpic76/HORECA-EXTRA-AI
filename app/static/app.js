const jobsCache = new Map();
const candidateSelect = document.getElementById("employer-candidate");

async function loadJobs(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  const response = await fetch(`/api/jobs?${params.toString()}`);
  const jobs = await response.json();
  jobs.forEach((job) => jobsCache.set(job.id, job));
  return jobs;
}

function renderJobs(jobs) {
  const container = document.getElementById("job-results");
  if (!jobs.length) {
    container.innerHTML = "<p>Aucune mission ne correspond à votre recherche.</p>";
    return;
  }

  container.innerHTML = jobs
    .map(
      (job) => `
        <article class="job-card">
          <h3>${job.title}</h3>
          <p><strong>${job.venue_name}</strong> • ${job.location}</p>
          <p>
            <span class="badge">${job.start_date}</span>
            <span class="badge">${job.end_date}</span>
          </p>
          <p>Besoin : ${job.requirements.join(", ") || "à préciser"}</p>
          <p>Créneaux : ${job.shifts
            .map((shift) => `${shift.label} ${shift.start}-${shift.end}`)
            .join(", ")}</p>
        </article>
      `
    )
    .join("");
}

async function populateSelectors() {
  const jobs = await loadJobs();
  const candidateJobSelect = document.getElementById("candidate-job");
  const employerJobSelect = document.getElementById("employer-job");

  const options = jobs
    .map((job) => `<option value="${job.id}">${job.title} – ${job.location}</option>`)
    .join("");
  candidateJobSelect.innerHTML = options;
  employerJobSelect.innerHTML = options;

  const response = await fetch("/api/candidates");
  const candidates = await response.json();
  candidateSelect.innerHTML =
    '<option value="">-- Choisir --</option>' +
    candidates
      .map((cand) => `<option value="${cand.id}">${cand.name}</option>`)
      .join("");
}

function extractList(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function displayAssistantOutput(containerId, title, result) {
  const container = document.getElementById(containerId);
  const messages = result.messages
    .map((message) => `<li>${message}</li>`)
    .join("");
  container.innerHTML = `
    <h3>${title}</h3>
    <p>Score : <strong>${result.score}</strong></p>
    <ul>${messages}</ul>
  `;
  container.classList.add("active");
}

function displayEmployerOutput(data) {
  const container = document.getElementById("employer-output");
  let html = "";
  if (data.match) {
    html += `
      <section>
        <h3>Analyse de ${data.candidate.name}</h3>
        <p>Score : <strong>${data.match.score}</strong></p>
        <ul>${data.match.messages.map((msg) => `<li>${msg}</li>`).join("")}</ul>
      </section>
    `;
  }
  if (data.suggestions?.length) {
    html += '<section><h3>Talents recommandés</h3><ul>';
    data.suggestions.forEach((item) => {
      html += `
        <li>
          <strong>${item.candidate.name}</strong> – score ${item.match.score}
          <br /><small>${item.candidate.skills.join(", ")}</small>
        </li>
      `;
    });
    html += "</ul></section>";
  }
  container.innerHTML = html || "<p>Aucune recommandation disponible.</p>";
  container.classList.add("active");
}

// Search form events
document.getElementById("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(event.target);
  const filters = Object.fromEntries(formData.entries());
  const jobs = await loadJobs(filters);
  renderJobs(jobs);
});

// Candidate assistant
document.getElementById("candidate-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const jobId = document.getElementById("candidate-job").value;
  const payload = {
    job_id: jobId,
    name: document.getElementById("candidate-name").value,
    locations: extractList(document.getElementById("candidate-locations").value),
    skills: extractList(document.getElementById("candidate-skills").value),
    availability_start: document.getElementById("candidate-availability-start").value,
    availability_end: document.getElementById("candidate-availability-end").value,
    preferred_shifts: extractList(document.getElementById("candidate-shifts").value),
  };

  const response = await fetch("/api/assistant/candidate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (result.error) {
    alert(result.error);
    return;
  }
  displayAssistantOutput("candidate-output", "Résultat de l'analyse", result);
});

// Employer assistant
document.getElementById("employer-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    job_id: document.getElementById("employer-job").value,
    candidate_id: document.getElementById("employer-candidate").value || undefined,
  };

  const response = await fetch("/api/assistant/employer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (result.error) {
    alert(result.error);
    return;
  }
  displayEmployerOutput(result);
});

(async () => {
  await populateSelectors();
  const jobs = await loadJobs();
  renderJobs(jobs);
})();
