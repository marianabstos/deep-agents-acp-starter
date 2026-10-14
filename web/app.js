const state = {
  sessionId: localStorage.getItem("deepAgentsWebSession") || crypto.randomUUID(),
  busy: false,
};

localStorage.setItem("deepAgentsWebSession", state.sessionId);

const messages = document.querySelector("#messages");
const composer = document.querySelector("#composer");
const promptInput = document.querySelector("#prompt");
const statusPill = document.querySelector("#status-pill");
const runSteps = [...document.querySelectorAll("#run-steps li")];
const tools = document.querySelector("#tools");

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`#panel-${button.dataset.panel}`).classList.add("active");
  });
});

async function loadStatus() {
  const response = await fetch("/api/status");
  const status = await response.json();
  document.querySelector("#model").textContent = status.model;
  document.querySelector("#langsmith").textContent = status.langsmith_project;
  document.querySelector("#workspace").textContent = status.workspace;
  statusPill.textContent = "Ready";
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (state.busy) return;

  const text = promptInput.value.trim();
  if (!text) return;

  state.busy = true;
  promptInput.value = "";
  statusPill.textContent = "Running";
  setStage("Context");
  addMessage("You", text, "user");
  const assistant = addMessage("Agent", "", "assistant");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: state.sessionId }),
    });

    await readEvents(response, {
      token(data) {
        assistant.querySelector("p").textContent += data.text;
        messages.scrollTop = messages.scrollHeight;
      },
      stage(data) {
        setStage(data.name);
      },
      tool(data) {
        appendTool(data.name);
        setStage("Tools");
      },
      session(data) {
        state.sessionId = data.session_id;
        localStorage.setItem("deepAgentsWebSession", state.sessionId);
      },
      error(data) {
        assistant.querySelector("p").textContent += `\n\nError: ${data.message}`;
        statusPill.textContent = "Error";
      },
      done() {
        statusPill.textContent = "Ready";
        setStage("Done");
      },
    });
  } finally {
    state.busy = false;
  }
});

async function readEvents(response, handlers) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const eventText of events) {
      const event = parseEvent(eventText);
      const handler = handlers[event.name];
      if (handler) handler(event.data);
    }
  }
}

function parseEvent(raw) {
  const lines = raw.split("\n");
  const name = lines.find((line) => line.startsWith("event: "))?.slice(7) || "message";
  const dataLine = lines.find((line) => line.startsWith("data: "));
  const data = dataLine ? JSON.parse(dataLine.slice(6)) : {};
  return { name, data };
}

function addMessage(author, text, kind) {
  const item = document.createElement("div");
  item.className = `message ${kind}`;
  item.innerHTML = `<span></span><p></p>`;
  item.querySelector("span").textContent = author;
  item.querySelector("p").textContent = text;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

function setStage(name) {
  runSteps.forEach((step) => {
    step.classList.toggle("active", step.textContent === name);
  });
}

function appendTool(name) {
  if (tools.classList.contains("tools-empty")) {
    tools.classList.remove("tools-empty");
    tools.textContent = "";
  }
  const item = document.createElement("div");
  item.textContent = name;
  tools.appendChild(item);
}

loadStatus().catch(() => {
  statusPill.textContent = "Offline";
});
