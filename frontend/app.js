const apiBase = "http://localhost:5000/api";

async function fetchPlaybooks() {
  const res = await fetch(`${apiBase}/playbooks`);
  const data = await res.json();
  return data.playbooks || [];
}

async function fetchJobs() {
  const res = await fetch(`${apiBase}/jobs?limit=10`);
  const data = await res.json();
  return data.jobs || [];
}

async function runPlaybook(playbook, hostname) {
  const res = await fetch(`${apiBase}/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ playbook, hostname })
  });
  return await res.json();
}

async function fetchJobLogs(jobId) {
  const res = await fetch(`${apiBase}/jobs/${jobId}/logs`);
  return await res.json();
}

function updatePlaybookDropdown(playbooks) {
  const sel = document.getElementById("playbook");
  sel.innerHTML = "";
  playbooks.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.name;
    opt.textContent = p.name;
    sel.appendChild(opt);
  });
}

function updateJobsTable(jobs) {
  const tbody = document.querySelector("#jobsTable tbody");
  tbody.innerHTML = "";
  jobs.forEach(job => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${job.id}</td>
      <td>${job.playbook_name}</td>
      <td>${job.target_host}</td>
      <td>${job.status}</td>
      <td>${job.started_at ? job.started_at.replace('T', ' ').slice(0, 19) : ''}</td>
      <td>${job.completed_at ? job.completed_at.replace('T', ' ').slice(0, 19) : ''}</td>
      <td><button data-jobid="${job.id}" class="log-btn">Logs</button></td>
    `;
    tbody.appendChild(tr);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  // Populate playbook dropdown
  const playbooks = await fetchPlaybooks();
  updatePlaybookDropdown(playbooks);

  // Populate jobs table
  async function refreshJobs() {
    const jobs = await fetchJobs();
    updateJobsTable(jobs);
  }
  await refreshJobs();
  setInterval(refreshJobs, 5000);

  // Run playbook
  document.getElementById("runButton").onclick = async () => {
    const playbook = document.getElementById("playbook").value;
    const hostname = document.getElementById("hostname").value;
    if (!playbook || !hostname) {
      alert("Pick a playbook and enter hostname!");
      return;
    }
    await runPlaybook(playbook, hostname);
    await refreshJobs();
  };

  // Modal logic
  const modal = document.getElementById("logModal");
  const closeModal = () => { modal.style.display = "none"; };
  document.querySelector(".close").onclick = closeModal;

  document.body.onclick = async (e) => {
    if (e.target.classList.contains("log-btn")) {
      const jobId = e.target.getAttribute("data-jobid");
      const logs = await fetchJobLogs(jobId);
      document.getElementById("modalLogs").textContent =
        "STDOUT:\n" + (logs.stdout || "") +
        "\n\nSTDERR:\n" + (logs.stderr || "");
      modal.style.display = "block";
    }
  };

  window.onclick = function(event) {
    if (event.target == modal) {
      closeModal();
    }
  };
});
