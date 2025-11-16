const apiBase = "/api";

// API functions
async function fetchPlaybooks() {
  try {
    const res = await fetch(`${apiBase}/playbooks`);
    const data = await res.json();
    return data.playbooks || [];
  } catch (error) {
    console.error('Error fetching playbooks:', error);
    return [];
  }
}

async function fetchJobs() {
  try {
    const res = await fetch(`${apiBase}/jobs?limit=10`);
    const data = await res.json();
    return data.jobs || [];
  } catch (error) {
    console.error('Error fetching jobs:', error);
    return [];
  }
}

async function runPlaybook(playbook, hostname) {
  try {
    const res = await fetch(`${apiBase}/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ playbook, hostname })
    });
    return await res.json();
  } catch (error) {
    console.error('Error running playbook:', error);
    return { error: error.message };
  }
}

async function fetchJobLogs(jobId) {
  try {
    const res = await fetch(`${apiBase}/jobs/${jobId}/logs`);
    return await res.json();
  } catch (error) {
    console.error('Error fetching job logs:', error);
    return { stdout: '', stderr: `Error: ${error.message}` };
  }
}

// UI update functions
function updatePlaybooksGrid(playbooks) {
  const container = document.getElementById("playbooksContainer");

  if (playbooks.length === 0) {
    container.innerHTML = '<div class="loading">No playbooks found</div>';
    return;
  }

  container.innerHTML = playbooks.map(playbook => `
    <div class="playbook-card">
      <div class="playbook-header">
        <div class="playbook-icon">
          <i class="fas fa-file-code"></i>
        </div>
        <div class="playbook-info">
          <h3>${playbook.name}</h3>
          <div class="playbook-meta">
            Size: ${formatBytes(playbook.size)} |
            Modified: ${new Date(playbook.modified).toLocaleDateString()}
          </div>
        </div>
      </div>
      <div class="playbook-actions">
        <button class="btn btn-primary run-playbook-btn" data-playbook="${playbook.name}">
          <i class="fas fa-play"></i> Run Playbook
        </button>
      </div>
    </div>
  `).join('');
}

function updateJobsList(jobs) {
  const container = document.getElementById("jobsContainer");

  if (jobs.length === 0) {
    container.innerHTML = '<div class="loading">No jobs found</div>';
    return;
  }

  container.innerHTML = jobs.map(job => `
    <div class="job-item">
      <div class="job-header">
        <div class="job-title">Job #${job.id} - ${job.playbook_name}</div>
        <div class="job-status status-${job.status}">${job.status}</div>
      </div>
      <div class="job-details">
        <div><strong>Host:</strong> ${job.target_host}</div>
        <div><strong>Started:</strong> ${job.started_at ? new Date(job.started_at).toLocaleString() : 'N/A'}</div>
        <div><strong>Completed:</strong> ${job.completed_at ? new Date(job.completed_at).toLocaleString() : 'N/A'}</div>
        <div><strong>Exit Code:</strong> ${job.exit_code !== null ? job.exit_code : 'N/A'}</div>
      </div>
      <div class="job-actions">
        <button class="btn btn-secondary view-logs-btn" data-jobid="${job.id}">
          <i class="fas fa-eye"></i> View Logs
        </button>
      </div>
    </div>
  `).join('');
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Modal management
function showModal(modalId) {
  document.getElementById(modalId).style.display = 'block';
}

function hideModal(modalId) {
  document.getElementById(modalId).style.display = 'none';
}

// Initialize app
async function initializeApp() {
  try {
    // Load playbooks
    const playbooks = await fetchPlaybooks();
    updatePlaybooksGrid(playbooks);

    // Load jobs
    const jobs = await fetchJobs();
    updateJobsList(jobs);
  } catch (error) {
    console.error('Failed to initialize app:', error);
  }
}

// Event listeners
document.addEventListener("DOMContentLoaded", () => {
  initializeApp();

  // Refresh buttons
  document.getElementById("refreshPlaybooks").addEventListener("click", async () => {
    const playbooks = await fetchPlaybooks();
    updatePlaybooksGrid(playbooks);
  });

  document.getElementById("refreshJobs").addEventListener("click", async () => {
    const jobs = await fetchJobs();
    updateJobsList(jobs);
  });

  // Run playbook buttons
  document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("run-playbook-btn") || e.target.closest(".run-playbook-btn")) {
      const button = e.target.classList.contains("run-playbook-btn") ? e.target : e.target.closest(".run-playbook-btn");
      const playbook = button.getAttribute("data-playbook");

      // Show run modal with hostname input
      const runModalContent = document.getElementById("runModalContent");
      runModalContent.innerHTML = `
        <div class="playbook-run-form">
          <h4>Run ${playbook}</h4>
          <div class="form-group">
            <label for="runHostname">Target Host:</label>
            <input type="text" id="runHostname" placeholder="Enter hostname or IP" required>
          </div>
          <div class="form-actions">
            <button id="confirmRun" class="btn btn-success">
              <i class="fas fa-play"></i> Execute
            </button>
            <button id="cancelRun" class="btn btn-secondary">
              <i class="fas fa-times"></i> Cancel
            </button>
          </div>
        </div>
      `;

      showModal("runModal");

      // Handle run confirmation
      document.getElementById("confirmRun").addEventListener("click", async () => {
        const hostname = document.getElementById("runHostname").value.trim();
        if (!hostname) {
          alert("Please enter a hostname");
          return;
        }

        runModalContent.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Running playbook...</div>';

        const result = await runPlaybook(playbook, hostname);

        if (result.job_id) {
          runModalContent.innerHTML = `
            <div class="success-message">
              <i class="fas fa-check-circle"></i>
              <h4>Playbook Started Successfully!</h4>
              <p>Job ID: ${result.job_id}</p>
              <p>Status: ${result.status}</p>
            </div>
          `;
        } else {
          runModalContent.innerHTML = `
            <div class="error-message">
              <i class="fas fa-exclamation-triangle"></i>
              <h4>Error Starting Playbook</h4>
              <p>${result.error || 'Unknown error'}</p>
            </div>
          `;
        }

        // Refresh jobs list
        setTimeout(async () => {
          const jobs = await fetchJobs();
          updateJobsList(jobs);
        }, 1000);
      });

      // Handle cancel
      document.getElementById("cancelRun").addEventListener("click", () => {
        hideModal("runModal");
      });
    }
  });

  // View logs buttons
  document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("view-logs-btn") || e.target.closest(".view-logs-btn")) {
      const button = e.target.classList.contains("view-logs-btn") ? e.target : e.target.closest(".view-logs-btn");
      const jobId = button.getAttribute("data-jobid");

      document.getElementById("modalLogs").textContent = "Loading logs...";
      showModal("logModal");

      const logs = await fetchJobLogs(jobId);
      document.getElementById("modalLogs").textContent =
        "STDOUT:\n" + (logs.stdout || "No stdout output") +
        "\n\nSTDERR:\n" + (logs.stderr || "No stderr output");
    }
  });

  // Modal close buttons
  document.querySelectorAll(".close").forEach(closeBtn => {
    closeBtn.addEventListener("click", () => {
      document.querySelectorAll(".modal").forEach(modal => {
        modal.style.display = "none";
      });
    });
  });

  // Click outside modal to close
  window.addEventListener("click", (event) => {
    document.querySelectorAll(".modal").forEach(modal => {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    });
  });
});

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
