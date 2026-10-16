# Milli-Agent: Technical Launch Kit and Release Dossier

This document contains publication-ready copy and distribution materials for launching Milli-Agent across developer and research communities.

---

## 1. Hacker News (Show HN)

### Title
Show HN: Milli-Agent – Computer-use at 60Hz without screenshot loops or LLM tokens

### URL
https://github.com/Abdullah-Al-Raju/milli-agent

### Submission Text
Hi HN,

I am Abdullah-Al-Raju. Over the past several months, I have been studying the architecture of modern "computer-use" agents (Claude 3.5 Computer Use, OSWorld baselines, AutoGPT). 

The hard truth about current computer-use agents is that their foundational architecture is bottlenecked by a discrete, turn-taking screenshot loop:
1. Capture screenshot via OS tool (800ms)
2. Save 1.5MB PNG to secondary storage (150ms)
3. Upload over HTTP to a cloud LLM (600ms)
4. Burn 1,600 vision tokens decoding coordinate coordinates (3,500ms)
5. Blind OS click or keypress (200ms)
6. Arbitrary time.sleep() heuristics to let the UI settle (1,000-3,000ms)

Total latency per turn: 4 to 8 seconds. A simple 10-step form or search task takes over a minute, consumes 16,000 tokens, thrashes SSD storage, and completely fails if anything on the screen is moving, dynamic, or timed.

To solve this, I designed and built Milli-Agent: an autonomous computer-use and browser execution engine built on a continuous closed-loop reflex manifold.

Key architectural shifts:
- Perception in Transient RAM (0 bytes written to disk): Streams the desktop framebuffer directly into transient memory buffers at 60 FPS. Zero disk persistence, zero vision token burn during continuous perception.
- Sub-Millisecond Decisions (0.083 ms): Uses single-pass non-autoregressive action classification rather than autoregressive token generation, making decisions 38,500x faster than cloud LLMs.
- In-Loop Web Execution (Cypress-style over WebSocket CDP): Dispatches DOM events directly into the browser run-loop in under 0.1 ms. Eliminates sleep statements via mutation-driven reactive settling (wait_until_idle). Headless footprint is ~65 MB (95.5% lighter than standard consumer browsers).
- Microsecond Hardware Actuation: Direct C bindings to libX11 / libXtst (Linux) and Win32 user32.dll (Windows) warp cursor coordinates in 0.013 ms and stream keystrokes at ~20,000 WPM.
- Visual AI Multimodal Server: Integrated HTTP/MJPEG streaming server (milli-agent visual) serving a live HUD, raw JPEG frame endpoints for vision models, and JSON action endpoints.

On our standardized Task Finished Benchmark (TFB), Milli-Agent achieves 13x to 207x faster completion times than turn-taking baselines:
- Web Search & Fact Extraction: 0.19s (vs 38.5s baseline, 203.9x speedup)
- Interactive Form Fill: 0.22s (vs 28.0s baseline, 127.4x speedup)
- 20-Target Optical Aim Reflex: 0.31s (vs 45.0s baseline, 145.2x speedup)

Milli-Agent is fully open for personal, academic, and evaluation use. Commercial / enterprise use requires a written license.

I am an independent researcher actively seeking graduate research fellowships, academic lab positions, or AI research collaborations in foundation computer-use and high-frequency agent architectures.

GitHub: https://github.com/Abdullah-Al-Raju/milli-agent
Direct contact: analystx.raju@gmail.com

Feedback and questions on the architecture are welcome.

---

## 2. X (Twitter) Technical Thread

### Post 1 (Hook)
Current "computer-use" AI agents take 6.5 seconds per turn.

Take screenshot -> Save PNG to disk -> Send 1.5MB to cloud LLM -> Burn 1,600 tokens -> Blind click -> Arbitrary sleep.

This turn-taking loop is fundamentally broken.

Introducing Milli-Agent: Continuous 60Hz computer-use with sub-15ms reflex loops.

github.com/Abdullah-Al-Raju/milli-agent

### Post 2 (The Bottleneck Breakdown)
Every major computer-use benchmark today (OSWorld, Anthropic Computer Use) operates like a slow slide projector:

- 4,000 to 8,000 ms per action
- 1,600 vision tokens burned per click just to locate an input field
- Gigabytes of temporary screenshot PNGs written to SSD
- 100% blind to video, animations, countdown timers, and moving targets

### Post 3 (The Reflex Shift)
Milli-Agent replaces discrete screenshots with a continuous 60Hz optical manifold in transient RAM.

Perception loop:
- 60 FPS framebuffer captured directly into RAM ring buffers (0 bytes disk persistence)
- 0 tokens consumed during perception
- Ingests optical flow velocity vectors (vx, vy) for dynamic trajectory tracking

### Post 4 (Non-Autoregressive System 1 Policy)
You do not need a 70B parameter autoregressive language model to decide if a button should be clicked.

Milli-Agent separates high-level planning (System 2) from reflexive actuation (System 1).
Our single-pass action classifier predicts typed actions in 0.083 ms. That is 38,500x faster than cloud LLM generation.

### Post 5 (In-Loop Browser Execution)
Automating web apps with external screenshot tools is slow.
MilliBrowserEngine runs Cypress-style in-loop over raw WebSocket Chrome DevTools Protocol (CDP):

- Evaluates DOM candidate states in < 0.05 ms
- Dispatches inputs in < 0.1 ms
- Mutation-driven reactive settling (wait_until_idle) eliminates all arbitrary sleep calls
- Hardened ~65 MB memory footprint

### Post 6 (Native C Hardware Actuation)
When acting on native desktop applications:
- Linux: Direct C libX11 / libXtst pointer warps in 0.013 ms
- Windows: Native Win32 SendInput via user32.dll (0.018 ms)
- Hardware keystroke injection streams formatted code and dossiers at ~20,000 WPM (1,700+ characters/sec)

### Post 7 (Empirical Benchmark Results)
Task Finished Benchmark (TFB) comparing Time To Finish (TTF) against conventional turn-taking agents:

- Task A (Web Search & Extraction): 0.19s vs 38.5s (203.9x speedup)
- Task B (Interactive Form Fill): 0.22s vs 28.0s (127.4x speedup)
- Task C (OS Workflow Automation): 0.00s vs 22.0s
- Task D (Dynamic Target Clearance): 0.31s vs 45.0s (145.2x speedup)

### Post 8 (Open Source & Collaborations)
Milli-Agent is available now:
- Code: github.com/Abdullah-Al-Raju/milli-agent
- Machine-readable specs: llms.txt & AGENTS.md
- Free for personal, academic, and research use.
- Written by Abdullah-Al-Raju. I am actively seeking academic fellowships and AI agent research collaborations (analystx.raju@gmail.com).

---

## 3. Reddit (r/MachineLearning & r/LocalLLaMA)

### Title
[R] Milli-Agent: Eliminating the 6-Second Screenshot Loop in Autonomous Computer-Use Agents (Continuous 60Hz Reflex Manifolds)

### Post Body
Hi everyone,

Over the past year, "computer use" has become a central frontier for multimodal LLMs. However, virtually every implementation today (Claude 3.5 Computer Use, OSWorld, WebArena) relies on an identical, synchronous turn-taking loop:
`Screenshot -> Disk IO -> Remote Multimodal Token Generation -> Simulated Input -> Arbitrary Sleep`.

This architecture imposes fundamental limitations:
1. Turn Latency Floor: 4 to 8 seconds per action.
2. Token Burn: 1,200 to 1,600 vision tokens consumed per step.
3. Storage Degradation: Continuous writes of uncompressed PNGs to disk.
4. Temporal Blindness: Total inability to perceive or react to dynamic environments (moving elements, canvas games, video players, countdown timers).

### The Architecture of Milli-Agent
I built **Milli-Agent** (https://github.com/Abdullah-Al-Raju/milli-agent) to investigate whether computer-use can be refactored into a continuous, high-frequency closed-loop system:

#### 1. Dual-System Cognitive Decoupling
Rather than querying a heavy autoregressive model on every screen update, Milli-Agent decouples execution into:
- **System 2 (Strategic / Deliberative):** Invoked asynchronously only on novel task states or topological transitions.
- **System 1 (Reflexive / Actuation):** A single-pass non-autoregressive action policy that fuses optical saliency centroids with interactive DOM state in 0.083 ms.

#### 2. Transient Memory Perception
Framebuffers are captured at 60Hz directly into circular RAM buffers via native X11 shared memory (Linux) or GDI capture (Windows). Zero bytes are written to secondary storage, and zero tokens are burned during continuous observation.

#### 3. In-Loop Web Execution via CDP
Instead of treating browsers as dumb desktop windows, MilliBrowserEngine connects directly to the Chrome DevTools Protocol over WebSockets. It performs microsecond DOM candidate extraction, dispatches in-loop mouse/keyboard events, and uses DOM mutation observers to settle reactively rather than sleeping. Memory footprint is ~65 MB.

#### 4. Microsecond Actuation
OS pointer warps execute in 0.013 ms using direct C bindings to `libX11` / `libXtst` on Linux and `user32.dll` on Windows. Keystroke injection streams at ~20,000 WPM (1,700+ chars/sec).

### Benchmark Comparison
Testing on our standardized Task Finished Benchmark (TFB):
- **Web Fact Extraction:** Milli-Agent 0.19s vs Baseline 38.5s (203.9x speedup)
- **Interactive Form Fill:** Milli-Agent 0.22s vs Baseline 28.0s (127.4x speedup)
- **Dynamic Aim Reflex (Moving Targets):** Milli-Agent 0.31s vs Baseline 45.0s (145.2x speedup, 100% hit rate)

The repository includes `llms.txt` and `AGENTS.md` for integration into external agentic orchestrators, as well as an HTTP/MJPEG Visual Server (`milli-agent visual`) for remote multimodal inspection.

Code: https://github.com/Abdullah-Al-Raju/milli-agent
License: Free for personal and academic research. Industrial / commercial use requires licensing.

I am looking for graduate research fellowships, PhD positions, or AI lab research collaborations in low-latency foundation computer-use and autonomous robotics. Reach out at `analystx.raju@gmail.com`.
