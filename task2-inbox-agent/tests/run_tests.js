import { startServer } from "../server.js";

console.log("=================================================");
console.log("🚀 TASK 2: INBOX AGENT - AUTOMATED TEST SUITE");
console.log("=================================================");

let runningServer = null;

try {
  // 1. Run Unit Tests
  await import("./test_triage.js");

  // 2. Ensure test server is accessible
  const BASE_URL = process.env.INBOX_AGENT_URL || "http://localhost:3000";
  let isRunning = false;
  try {
    const res = await fetch(`${BASE_URL}/api/health`, { signal: AbortSignal.timeout(1000) });
    if (res.ok) isRunning = true;
  } catch {
    isRunning = false;
  }

  if (!isRunning) {
    console.log("⚙  Starting in-process Inbox Agent server on port 3000...");
    runningServer = await startServer(3000);
    // Give it a brief moment
    await new Promise(r => setTimeout(r, 100));
  }

  // 3. Run API Integration Tests
  await import("./test_api.js");

  console.log("=================================================");
  console.log("✅ ALL TASK 2 TESTS PASSED PERFECTLY!");
  console.log("=================================================");
} catch (err) {
  console.error("❌ TEST FAILURE:", err);
  process.exit(1);
} finally {
  if (runningServer) {
    runningServer.close();
  }
}

process.exit(0);

