import "dotenv/config";
import { writeFileSync, mkdirSync } from "fs";

const { N8N_API_URL, N8N_API_KEY } = process.env;

const headers = {
  "X-N8N-API-KEY": N8N_API_KEY,
  "Content-Type": "application/json",
};

async function fetchWorkflows() {
  const res = await fetch(`${N8N_API_URL}/workflows`, { headers });

  if (!res.ok) {
    console.error(`Failed to fetch workflows: ${res.status} ${res.statusText}`);
    const body = await res.text();
    console.error(body);
    process.exit(1);
  }

  const data = await res.json();
  const workflows = data.data ?? data;

  mkdirSync("workflows", { recursive: true });

  for (const wf of workflows) {
    const detail = await fetch(`${N8N_API_URL}/workflows/${wf.id}`, { headers });
    const full = await detail.json();
    const filename = `workflows/${wf.id}-${wf.name.replace(/[^a-zA-Z0-9]/g, "_")}.json`;
    writeFileSync(filename, JSON.stringify(full, null, 2));
    console.log(`Saved: ${filename}`);
  }

  console.log(`\nTotal workflows exported: ${workflows.length}`);
}

fetchWorkflows();
