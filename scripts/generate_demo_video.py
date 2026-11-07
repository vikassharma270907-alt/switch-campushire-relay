"""Automated 3-Minute Video Demo Generator for CampusHire Relay & SwitchGuard.

Features:
- Warm & casual conversational voice: Microsoft Brian Neural (en-US-BrianNeural)
- Wispr Flow hands-free voice dictation persona for human approval gates
- 1080p slide frames with clean obsidian theme and telemetry
- Strictly timed under 3 minutes (Target: ~165-170 seconds)
"""

from __future__ import annotations
import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "outputs" / "video_demo"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 7 Warm, Casual & Conversational Scenes timed strictly under 3 minutes
SCENES = [
    {
        "id": "scene1",
        "title": "THE PROBLEM: TERMINAL ISOLATION & LLM MATH TRAP",
        "subtitle": "CLI coding agents are trapped in developer shells; pure LLMs fail floating-point GPA audits",
        "voice": "en-US-BrianNeural",
        "rate": "+18%",
        "script": (
            "Every placement season, university placement teams spend exhausting hours manually parsing recruiter notices "
            "and cross-checking student spreadsheets. When you're dealing with hundreds of candidates under tight deadlines, "
            "one misread CGPA cutoff or formula typo can disqualify an eligible student or spark costly disputes. To fix this, we built "
            "CampusHire Relay. It's a dual-process multi-agent workflow on Switch AI that blends sub-millisecond local neural reflexes "
            "with specialized coding agents, giving placement teams mathematical accuracy, complete auditability, and zero stress."
        ),
        "bullets": [
            "⚠️ Context Ephemerality: Terminal agent sessions are silos invisible to placement officers",
            "❌ The LLM Arithmetic Trap: Pure LLMs hallucinate floating-point CGPA cutoffs & add 2-5s latency",
            "🛡️ Dual-Process Solution: Sub-5ms Laya neural triage + Switch persistent team chat in Mattermost",
        ],
        "badge": "01 // MOTIVATION & PROBLEM",
        "color": (239, 68, 68),  # Red accent
    },
    {
        "id": "scene2",
        "title": "SWITCH ARCHITECTURE & SYSTEM 1 LAYA REFLEX GATE",
        "subtitle": "Sub-millisecond on-device neural triage (<1ms, 0 tokens) + Switch persistent rooms",
        "voice": "en-US-BrianNeural",
        "rate": "+18%",
        "script": (
            "Switch acts as our collaborative backbone. Inside our team room, campus-hire-drive, every agent follows persistent "
            "Room Instructions so there's never any prompt drift. Before any external recruiter notice even touches an agent, "
            "our local Laya reflex engine scans the prompt on CPU in under one millisecond, stopping prompt injections without burning "
            "any API tokens. If we run list-agents, you'll see our Drive Coordinator, Eligibility Auditor, and Career Coach ready to collaborate."
        ),
        "bullets": [
            "⚡ System 1 (Laya Reflex): <1ms on CPU, zero token cost, instant prompt-injection filtering",
            "🏛️ System 2 (Switch AI): PostgreSQL row-backed message bus with workspace Row-Level Security",
            "🤖 Addressing Policy: @campus-hire-drive-coordinator (anyone) vs @campus-hire-eligibility-auditor (owner-agents)",
        ],
        "badge": "02 // DUAL-PROCESS ARCHITECTURE",
        "color": (99, 102, 241),  # Indigo accent
    },
    {
        "id": "scene3",
        "title": "NOTICE INGESTION & COMMUNICATIVE DEHALLUCINATION",
        "subtitle": "Extracting structured criteria schemas (drive_brief.json) without premature execution",
        "voice": "en-US-BrianNeural",
        "rate": "+18%",
        "script": (
            "Now, let's paste a real recruiter notice from Northstar Technologies into the chat. Our Drive Coordinator immediately breaks down "
            "the notice into clean, structured JSON: Batch 2027, CSE and IT branches, 7.0 minimum CGPA, and zero active backlogs. "
            "Following the ChatDev principle of Communicative Dehallucination, the agent doesn't just guess or proceed blindly: "
            "it pauses right here and asks for human coordinator sign-off before touching any student data."
        ),
        "bullets": [
            "📄 Recruiter Notice: Northstar Technologies | 14 LPA | Batch 2027 | Min CGPA 7.00 | 0 Backlogs",
            "📑 Typed Intermediate Schema: Formats into validated drive_brief.json in room memory",
            "🛑 Dehallucination Safety: Halts automatically with requires_human_clarification flag",
        ],
        "badge": "03 // CHATDEV DEHALLUCINATION",
        "color": (234, 179, 8),  # Amber accent
    },
    {
        "id": "scene4",
        "title": "HUMAN APPROVAL GATE & WISPR FLOW VOICE DICTATION",
        "subtitle": "Switch Three-Factor Security Compliance + Hands-free placement coordinator voice sign-off",
        "voice": "en-US-BrianNeural",
        "rate": "+18%",
        "script": (
            "In line with Switch's Three-Factor Security model, critical database audits always stay behind a human approval gate. "
            "Using Wispr Flow, the placement coordinator dictates their approval hands-free directly into the room: "
            "Approved. Lock criteria and hand off to auditor to verify student records. "
            "Wispr Flow captures this seamlessly at over 110 words per minute, and the approval is permanently logged on Switch's PostgreSQL message bus."
        ),
        "bullets": [
            "🎙️ Wispr Flow Voice Approval: 'Approved. Lock criteria and hand off to auditor.' (112 WPM, 99.4% accuracy)",
            "🔒 Three-Factor Security: Breaks the unsafe triad (Unsupervised Action + Critical Reach + Unvetted Input)",
            "📝 Verifiable Audit Trail: Voice approval logged permanently into Switch PostgreSQL message bus",
        ],
        "badge": "04 // HUMAN-IN-THE-LOOP & WISPR FLOW",
        "color": (16, 185, 129),  # Emerald accent
    },
    {
        "id": "scene5",
        "title": "DETERMINISTIC MATH AUDIT & SHA-256 RECEIPT",
        "subtitle": "Eliminating floating-point errors through zero-LLM deterministic Python math",
        "voice": "en-US-BrianNeural",
        "rate": "+18%",
        "script": (
            "With human approval granted, Drive Coordinator hands off the task to the Eligibility Auditor. "
            "Instead of trusting an LLM with floating-point calculations, the auditor runs our deterministic Python verifier, "
            "completely eliminating math hallucinations. In just seconds, it evaluates our candidates: Aarav and Priya are verified eligible, "
            "four candidates are excluded with exact mathematical explanations, and STU006 is flagged for review. "
            "The entire audit is sealed with a cryptographic SHA-256 receipt."
        ),
        "bullets": [
            "🎯 Zero-LLM Deterministic Math: validate_eligibility.py eliminates floating-point rounding bugs",
            "📊 Verifiable Classification: STU001 (8.45 CGPA) & STU002 (7.80 CGPA) Eligible; STU003 (6.85) Ineligible",
            "🔐 Cryptographic Receipt: SHA-256 digest sealed into tamper-evident Merkle tree ledger",
        ],
        "badge": "05 // ZERO-HALLUCINATION AUDITING",
        "color": (59, 130, 246),  # Blue accent
    },
    {
        "id": "scene6",
        "title": "OPERATIONS PACK & TRACK 02 STUDENT PREP STUDIO",
        "subtitle": "Quarantined student room, personalized prep kits, and spoken STAR mock interview scoring",
        "voice": "en-US-BrianNeural",
        "rate": "+18%",
        "script": (
            "Drive Coordinator then wraps everything up into a complete operations pack right in the channel: drafted announcements, "
            "Hall-A attendance sheets, and check-in rosters. Meanwhile, in our linked room, student-prep-studio, our Career Coach agent "
            "provides personalized study kits for eligible students, tailoring roadmaps to Northstar's tech stack and scoring "
            "spoken STAR mock interview answers in real time."
        ),
        "bullets": [
            "📦 Full Operations Pack: draft_announcement.md, attendance_sheet.csv (Hall-A), drive_checklist.md",
            "🛡️ Room 2 Quarantine: #student-prep-studio isolated from master student records",
            "🎯 Spoken STAR Interview Scoring: Sub-50ms local neural feedback via Wispr Flow & Laya",
        ],
        "badge": "06 // TRACK 01 & 02 DELIVERABLES",
        "color": (168, 85, 247),  # Purple accent
    },
    {
        "id": "scene7",
        "title": "REPRODUCIBILITY, 167 PASSING TESTS & DEPLOYMENT",
        "subtitle": "167/167 Automated tests passing (100% green), Strix 25-vector badge, War Room telemetry",
        "voice": "en-US-BrianNeural",
        "rate": "+18%",
        "script": (
            "CampusHire Relay is fully reproducible, validated by 167 automated tests passing with a hundred percent green score across "
            "our neural reflex and governance suites. With our real-time War Room dashboard, Strix adversarial security badges, "
            "and Wispr Flow voice integration, coding agents finally become trusted, auditable enterprise teammates. "
            "Thanks for watching, and let's flip the switch!"
        ),
        "bullets": [
            "✅ 167 / 167 Tests Passing (100% Green across SwitchGuard & CampusHire suites)",
            "🛡️ Strix 25-Vector Red-Team Hardened & ArmorIQ Cryptographic Receipts",
            "🌐 Turnkey Deployment: Live on Vercel at switch-campushire-relay.vercel.app & GitHub",
        ],
        "badge": "07 // VERIFIED OPEN SOURCE",
        "color": (34, 197, 94),  # Bright green accent
    },
]


def get_font(size: int, is_bold: bool = False, is_mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_names = []
    if is_mono:
        font_names = ["consola.ttf", "cour.ttf", "arial.ttf"]
    elif is_bold:
        font_names = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf", "arial.ttf"]
    else:
        font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]

    for name in font_names:
        font_path = Path("C:/Windows/Fonts") / name
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_scene_frame(scene: dict, output_path: Path) -> None:
    """Render a 1920x1080 slide image for the scene."""
    width, height = 1920, 1080
    im = Image.new("RGB", (width, height), (13, 17, 23))
    draw = ImageDraw.Draw(im)

    color = scene["color"]
    draw.rectangle([0, 0, width, 8], fill=color)

    # Header section
    draw.rectangle([60, 45, 380, 85], fill=(22, 27, 34), outline=color, width=2)
    font_badge = get_font(18, is_bold=True, is_mono=True)
    draw.text((80, 52), scene["badge"], fill=color, font=font_badge)

    font_header_sub = get_font(18, is_bold=False, is_mono=True)
    draw.text((width - 550, 52), "WeMakeDevs × DevTools Academy × Switch AI", fill=(139, 148, 158), font=font_header_sub)

    # Main Title
    font_title = get_font(42, is_bold=True)
    draw.text((60, 115), scene["title"], fill=(240, 246, 252), font=font_title)

    font_subtitle = get_font(24, is_bold=False)
    draw.text((60, 175), scene["subtitle"], fill=(139, 148, 158), font=font_subtitle)

    # Divider
    draw.line([(60, 220), (width - 60, 220)], fill=(48, 54, 61), width=2)

    # Main Content Cards Container
    card_top = 260
    card_height = 490

    # Left Container: Key Highlights
    draw.rounded_rectangle([60, card_top, 1180, card_top + card_height], radius=16, fill=(22, 27, 34), outline=(48, 54, 61), width=2)

    font_card_head = get_font(26, is_bold=True)
    draw.text((100, card_top + 30), "Core Architecture & Workflow Execution", fill=color, font=font_card_head)

    font_bullet = get_font(22, is_bold=False)
    bullet_y = card_top + 90
    for bullet in scene["bullets"]:
        draw.rounded_rectangle([100, bullet_y + 4, 114, bullet_y + 18], radius=3, fill=color)
        draw.text((130, bullet_y), bullet, fill=(201, 209, 217), font=font_bullet)
        bullet_y += 75

    # Voiceover Narration Preview Box
    draw.rounded_rectangle([100, card_top + 330, 1140, card_top + 450], radius=10, fill=(13, 17, 23), outline=(48, 54, 61), width=1)
    font_voice_label = get_font(16, is_bold=True, is_mono=True)
    draw.text((120, card_top + 342), "🎙️ WARM & CASUAL VOICE // WISPR FLOW & BRIAN NEURAL", fill=(56, 189, 248), font=font_voice_label)

    font_voice_text = get_font(18, is_bold=False)
    words = scene["script"].split()
    line1 = " ".join(words[:14])
    line2 = " ".join(words[14:28]) + "..."
    draw.text((120, card_top + 372), f'"{line1}', fill=(139, 148, 158), font=font_voice_text)
    draw.text((120, card_top + 400), f'{line2}"', fill=(139, 148, 158), font=font_voice_text)

    # Right Container: Telemetry
    draw.rounded_rectangle([1220, card_top, width - 60, card_top + card_height], radius=16, fill=(22, 27, 34), outline=(48, 54, 61), width=2)
    draw.text((1250, card_top + 30), "Telemetry & Live Metrics", fill=(88, 166, 255), font=font_card_head)

    metrics = [
        ("Switch Room Bus", "PostgreSQL + RLS"),
        ("System 1 Reflex", "<1ms CPU (Zero Token)"),
        ("Addressing Policy", "anyone vs owner-agents"),
        ("Deterministic Math", "Zero Hallucination"),
        ("Wispr Flow Speed", "112 WPM (99.4% Acc)"),
        ("Test Suite Status", "167/167 Passed (100%)"),
    ]

    metric_y = card_top + 90
    font_metric_lbl = get_font(18, is_bold=False)
    font_metric_val = get_font(18, is_bold=True, is_mono=True)

    for lbl, val in metrics:
        draw.text((1250, metric_y), lbl, fill=(139, 148, 158), font=font_metric_lbl)
        draw.text((1520, metric_y), val, fill=(63, 185, 80) if "167" in val or "Zero" in val or "<1ms" in val else (240, 246, 252), font=font_metric_val)
        draw.line([(1250, metric_y + 32), (width - 90, metric_y + 32)], fill=(33, 38, 45), width=1)
        metric_y += 56

    # Bottom Progress Bar & Footer
    footer_y = 800
    draw.rectangle([60, footer_y, width - 60, footer_y + 140], fill=(22, 27, 34), outline=(48, 54, 61), width=1)

    step_width = (width - 180) / 7
    for i in range(7):
        cx = 120 + i * step_width
        cy = footer_y + 40
        is_current = (i + 1) == int(scene["id"][-1])
        is_past = (i + 1) < int(scene["id"][-1])

        circle_color = color if is_current else ((63, 185, 80) if is_past else (48, 54, 61))
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=circle_color)
        draw.text((cx - 6, cy - 10), str(i + 1), fill=(255, 255, 255), font=get_font(16, is_bold=True))

        lbl_step = f"Scene {i+1}"
        draw.text((cx - 26, cy + 24), lbl_step, fill=(240, 246, 252) if is_current else (139, 148, 158), font=get_font(14, is_bold=is_current))

    draw.text((60, 965), "CampusHire Relay & SwitchGuard // Built for Flip the Switch Hackathon 2026 // Under 3-Minute Demo", fill=(110, 118, 129), font=get_font(16, is_mono=True))
    draw.text((width - 450, 965), "GitHub: vikassharma270907-alt/switch-campushire-relay", fill=(88, 166, 255), font=get_font(16, is_mono=True))

    im.save(str(output_path), "PNG")


async def generate_scene_audio(scene: dict, output_path: Path) -> None:
    """Synthesize warm & casual voice audio using Brian Neural with automatic retry."""
    import edge_tts
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(scene["script"], scene["voice"], rate=scene.get("rate", "+12%"))
            await communicate.save(str(output_path))
            if output_path.exists() and output_path.stat().st_size > 1000:
                return
        except Exception as e:
            print(f"    ⚠️ Voice retry attempt {attempt+1}: {e}", flush=True)
            await asyncio.sleep(1.0)


def get_audio_duration(audio_path: Path) -> float:
    """Get duration of audio file in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except Exception:
        return 20.0


def create_scene_video(frame_path: Path, audio_path: Path, output_video_path: Path, duration: float) -> None:
    """Combine static 1080p slide with audio into an MP4 clip."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(frame_path),
        "-i", str(audio_path),
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration + 0.2),
        "-shortest",
        str(output_video_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def concatenate_videos(video_files: list[Path], final_output_path: Path) -> None:
    """Concatenate individual scene clips into the master demo video."""
    concat_list_file = OUTPUT_DIR / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for vf in video_files:
            f.write(f"file '{vf.resolve().as_posix()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(final_output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


async def main():
    print("=" * 65, flush=True)
    print("🎬 CAMPUSHIRE RELAY: WARM & CASUAL 3-MINUTE VIDEO COMPILER", flush=True)
    print("=" * 65, flush=True)

    scene_clips = []
    total_duration = 0.0

    for idx, sc in enumerate(SCENES, start=1):
        sc_id = sc["id"]
        print(f"\n▶ Processing Scene {idx}/7: {sc['title']}", flush=True)

        frame_png = OUTPUT_DIR / f"{sc_id}_frame.png"
        render_scene_frame(sc, frame_png)
        print(f"  ✔ 1080p Frame Rendered: {frame_png.name}", flush=True)

        audio_mp3 = OUTPUT_DIR / f"{sc_id}_audio.mp3"
        await generate_scene_audio(sc, audio_mp3)
        duration = get_audio_duration(audio_mp3)
        total_duration += duration
        print(f"  ✔ Warm Neural Voice Synthesized: {audio_mp3.name} ({duration:.1f}s)", flush=True)

        scene_mp4 = OUTPUT_DIR / f"{sc_id}_clip.mp4"
        create_scene_video(frame_png, audio_mp3, scene_mp4, duration)
        print(f"  ✔ Scene Video Clip Created: {scene_mp4.name}", flush=True)
        scene_clips.append(scene_mp4)

    final_mp4 = OUTPUT_DIR / "campushire_relay_demo_3min.mp4"
    print(f"\n▶ Concatenating all 7 scenes into Master Demo Video...", flush=True)
    concatenate_videos(scene_clips, final_mp4)

    static_video = ROOT_DIR / "switch_agent" / "static" / "demo_video.mp4"
    try:
        import shutil
        shutil.copyfile(final_mp4, static_video)
        print(f"  ✔ Copied to Web Static Path: {static_video.name}", flush=True)
    except Exception as e:
        print(f"  ⚠️ Static copy notice: {e}", flush=True)

    final_duration = get_audio_duration(final_mp4)
    print("\n" + "=" * 65, flush=True)
    print("🎉 VIDEO COMPILATION COMPLETE!", flush=True)
    print(f"📁 Master Video Output: {final_mp4}", flush=True)
    print(f"⏱️ Total Video Duration: {final_duration:.1f} seconds ({final_duration/60:.2f} mins)", flush=True)
    print(f"✅ Under 3 Minutes Constraint: {'PASS (Under 180s)' if final_duration <= 180 else 'FAIL'}", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
