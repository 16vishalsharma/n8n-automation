import "dotenv/config";
import { readFileSync, readdirSync } from "fs";

const { N8N_API_URL, N8N_API_KEY } = process.env;

const headers = {
  "X-N8N-API-KEY": N8N_API_KEY,
  "Content-Type": "application/json",
};

async function pushWorkflow(filePath) {
  const raw = readFileSync(filePath, "utf-8");
  const workflow = JSON.parse(raw);

  if (!workflow.id) {
    console.error(`No workflow ID found in ${filePath}`);
    process.exit(1);
  }

  // Extract only the fields n8n API accepts for PUT update
  const payload = {
    name: workflow.name,
    nodes: workflow.nodes,
    connections: workflow.connections,
    settings: workflow.settings,
    staticData: workflow.staticData,
    // Note: "active" is read-only via API — activate/deactivate in n8n UI
  };

  console.log(`Pushing workflow: "${workflow.name}" (ID: ${workflow.id})...`);

  const res = await fetch(`${N8N_API_URL}/workflows/${workflow.id}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const body = await res.text();
    console.error(`Failed to update workflow: ${res.status} ${res.statusText}`);
    console.error(body);
    process.exit(1);
  }

  const updated = await res.json();
  console.log(`Successfully updated: "${updated.name}" (ID: ${updated.id})`);
  console.log(`Active: ${updated.active}`);
}

// Get file path from CLI argument, or push all workflows
const target = process.argv[2];

if (target) {
  await pushWorkflow(target);
} else {
  const files = readdirSync("workflows").filter((f) => f.endsWith(".json"));
  for (const file of files) {
    await pushWorkflow(`workflows/${file}`);
  }
  console.log(`\nTotal workflows pushed: ${files.length}`);
}
