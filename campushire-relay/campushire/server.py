"""FastAPI Webhook Server & Interactive Switch Room Simulator for CampusHire Relay."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from typing import List, Dict, Any
from campushire.models import SwitchMessage
from campushire.switch_room import SwitchRoom
from campushire.storage.student_db import StudentRepository
from campushire.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Multi-agent campus placement workflow relay connected to Switch room chat.",
    version="0.1.0",
)

# Shared in-memory Switch Room instance
repo = StudentRepository()
repo.load_synthetic_dataset()
room = SwitchRoom(student_repo=repo, room_name=settings.room_name, borderline_delta=settings.borderline_cgpa_delta)


@app.get("/health")
def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name, "version": "0.1.0"}


@app.get("/api/candidates")
def list_candidates() -> List[Dict[str, Any]]:
    """Return all candidate records in the student database."""
    return [c.model_dump() for c in repo.get_all_candidates()]


@app.post("/api/switch/events")
def handle_switch_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming Switch Room webhooks and return multi-agent responses."""
    try:
        msg = SwitchMessage(
            sender=event.get("sender", "Anonymous"),
            content=event.get("content", ""),
            room=event.get("room", room.room_name),
            mentions=event.get("mentions", []),
        )
        responses = room.handle_message(msg)
        return {
            "status": "processed",
            "received_message": msg.model_dump(),
            "responses": [r.model_dump() for r in responses],
            "room_history_length": len(room.history),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/report")
def get_audit_report() -> Dict[str, Any]:
    """Return the active eligibility audit report in JSON format."""
    if not room.active_report:
        return {"status": "no_active_audit", "message": "No audit has been performed yet."}
    return room.active_report.model_dump()


@app.get("/api/audit/export-csv")
def export_csv() -> Response:
    """Download verified candidate shortlist as a CSV file."""
    if not room.active_report:
        raise HTTPException(status_code=400, detail="No active audit report available to export.")
    csv_data = room.eligibility_auditor.export_shortlist_csv(room.active_report)
    filename = f"shortlist_{room.active_report.criteria.company_name.lower().replace(' ', '_')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Modern interactive Switch room simulator dashboard."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CampusHire Relay - Switch Room Simulator</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .message-enter { animation: fadeIn 0.3s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-sans">
  <!-- Top Navigation -->
  <header class="bg-slate-800/80 backdrop-blur border-b border-slate-700 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <span class="text-2xl">⚡</span>
      <div>
        <h1 class="font-bold text-lg text-white">CampusHire Relay</h1>
        <p class="text-xs text-emerald-400">Flip the Switch Hackathon · Multi-Agent Room Integration</p>
      </div>
    </div>
    <div class="flex items-center space-x-4 text-xs">
      <span class="bg-slate-700 px-3 py-1.5 rounded-full border border-slate-600">Channel: <b class="text-indigo-400">#placement-drive-2027</b></span>
      <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-900/60 text-emerald-400 border border-emerald-500/30">
        ● Switch Connected
      </span>
      <a href="/api/audit/export-csv" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3 py-1.5 rounded transition">📥 Export CSV</a>
    </div>
  </header>

  <!-- Main Content Layout -->
  <div class="flex-1 grid grid-cols-1 lg:grid-cols-4 max-w-7xl w-full mx-auto p-4 gap-4">
    <!-- Left Panel: Presets & Controls -->
    <div class="lg:col-span-1 bg-slate-800/60 border border-slate-700 rounded-xl p-4 flex flex-col space-y-4">
      <h2 class="font-semibold text-sm text-slate-300 uppercase tracking-wider">Quick Actions</h2>
      <button onclick="loadSampleJD('stripe')" class="w-full text-left bg-slate-700 hover:bg-slate-600 p-3 rounded-lg text-xs transition border border-slate-600">
        <p class="font-bold text-white">1. Post Stripe JD (28 LPA)</p>
        <p class="text-slate-400 mt-1">@DriveCoordinator extraction & checklist</p>
      </button>
      <button onclick="triggerAudit()" class="w-full text-left bg-slate-700 hover:bg-slate-600 p-3 rounded-lg text-xs transition border border-slate-600">
        <p class="font-bold text-emerald-400">2. Run Student Audit</p>
        <p class="text-slate-400 mt-1">@EligibilityAuditor verification</p>
      </button>
      <button onclick="approveBorderline('23CS04')" class="w-full text-left bg-slate-700 hover:bg-slate-600 p-3 rounded-lg text-xs transition border border-slate-600">
        <p class="font-bold text-amber-400">3. Grant Borderline Waiver</p>
        <p class="text-slate-400 mt-1">Human-in-the-loop approval for 23CS04</p>
      </button>
      
      <div class="pt-4 border-t border-slate-700">
        <h3 class="text-xs font-semibold text-slate-400 uppercase">Room Teammates</h3>
        <div class="mt-2 space-y-2 text-xs">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span><b>@DriveCoordinator</b> (AI Agent)</span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
            <span><b>@EligibilityAuditor</b> (AI Agent)</span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-amber-400"></span>
            <span><b>@PlacementOfficer</b> (Human)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Center Panel: Switch Room Chat -->
    <div class="lg:col-span-3 bg-slate-800/90 border border-slate-700 rounded-xl flex flex-col h-[75vh]">
      <!-- Chat Messages Container -->
      <div id="chatBox" class="flex-1 overflow-y-auto p-4 space-y-4">
        <div class="text-center text-xs text-slate-500 my-2">── Room session started in #placement-drive-2027 ──</div>
      </div>

      <!-- Message Input Form -->
      <form onsubmit="sendMessage(event)" class="p-3 bg-slate-800 border-t border-slate-700 flex space-x-2">
        <input id="msgInput" type="text" placeholder="Type a message or mention @DriveCoordinator or @EligibilityAuditor..." 
          class="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500">
        <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2 rounded-lg text-sm transition">
          Send
        </button>
      </form>
    </div>
  </div>

  <script>
    const chatBox = document.getElementById('chatBox');
    const msgInput = document.getElementById('msgInput');

    function escapeHtml(str) {
      const p = document.createElement('p');
      p.textContent = str;
      return p.innerHTML;
    }

    function appendMessage(sender, content, isAgent = false) {
      const div = document.createElement('div');
      div.className = "flex flex-col space-y-1 message-enter " + (isAgent ? "items-start" : "items-end");
      
      let badgeClass = "bg-amber-600 text-amber-100";
      if (sender === "DriveCoordinator") badgeClass = "bg-emerald-600 text-emerald-100";
      if (sender === "EligibilityAuditor") badgeClass = "bg-indigo-600 text-indigo-100";

      div.innerHTML = `
        <div class="flex items-center space-x-2 text-xs text-slate-400 ${isAgent ? 'flex-row' : 'flex-row-reverse space-x-reverse'}">
          <span class="px-2 py-0.5 rounded font-semibold text-[10px] ${badgeClass}">${escapeHtml(sender)}</span>
          <span>Just now</span>
        </div>
        <div class="p-3.5 rounded-xl text-sm max-w-2xl whitespace-pre-wrap font-mono ${isAgent ? 'bg-slate-700/80 text-slate-100 border border-slate-600' : 'bg-indigo-600 text-white'}">
          ${escapeHtml(content)}
        </div>
      `;
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendPayload(sender, content, mentions = []) {
      appendMessage(sender, content, sender !== "PlacementOfficer");
      try {
        const res = await fetch('/api/switch/events', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ sender, content, room: "#placement-drive-2027", mentions })
        });
        const data = await res.json();
        if (data.responses) {
          data.responses.forEach(r => appendMessage(r.sender, r.content, true));
        }
      } catch (e) {
        appendMessage("System", "Error communicating with Switch Relay: " + e.message, true);
      }
    }

    function sendMessage(e) {
      e.preventDefault();
      const val = msgInput.value.trim();
      if (!val) return;
      msgInput.value = '';
      const mentions = [];
      if (val.includes("@DriveCoordinator")) mentions.push("@DriveCoordinator");
      if (val.includes("@EligibilityAuditor")) mentions.push("@EligibilityAuditor");
      sendPayload("PlacementOfficer", val, mentions);
    }

    function loadSampleJD(type) {
      const jd = `@DriveCoordinator Campus Recruitment Drive 2027 - Stripe
Role: Backend Platform Engineer
Compensation: 28 LPA
Eligibility: Minimum CGPA 8.00, 0 active backlogs, Branches: CSE, IT, ECE
Passing Batch: 2027
Deadline: Nov 15, 2026, 6:00 PM
Assessment Date: Nov 18, 2026`;
      sendPayload("PlacementOfficer", jd, ["@DriveCoordinator"]);
    }

    function triggerAudit() {
      sendPayload("PlacementOfficer", "@EligibilityAuditor please execute eligibility audit on 2027 batch", ["@EligibilityAuditor"]);
    }

    function approveBorderline(roll) {
      sendPayload("PlacementOfficer", `@EligibilityAuditor approve waiver for ${roll} based on HOD recommendation`, ["@EligibilityAuditor"]);
    }
  </script>
</body>
</html>
"""
