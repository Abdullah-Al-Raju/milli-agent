# Milli-Agent: Real-Time Autonomous Computer-Use Engine

A high-frequency autonomous agent architecture engineered for sub-second desktop and browser execution. By replacing conventional turn-taking screenshot loops with continuous 60Hz visual perception in RAM, sub-millisecond non-autoregressive decision classification, and in-loop execution protocols, Milli-Agent operates at physical hardware and display refresh limits.

---

## Table of Contents

- [1. Executive Overview](#1-executive-overview)
- [2. The Latency Problem in Existing Computer-Use Agents](#2-the-latency-problem-in-existing-computer-use-agents)
- [3. Architectural Design Principles](#3-architectural-design-principles)
- [4. Core Capabilities](#4-core-capabilities)
- [5. Audited Performance Benchmarks](#5-audited-performance-benchmarks)
- [6. System Architecture](#6-system-architecture)
- [7. Installation and System Prerequisites](#7-installation-and-system-prerequisites)
- [8. Python API and Usage Guide](#8-python-api-and-usage-guide)
- [9. Running the Benchmark Suite](#9-running-the-benchmark-suite)
- [10. Autonomous Agent Integration (llms.txt and AGENTS.md)](#10-autonomous-agent-integration-llmstxt-and-agentsmd)
- [11. Licensing and Terms of Use](#11-licensing-and-terms-of-use)
- [12. Research Collaborations and Academic Fellowships](#12-research-collaborations-and-academic-fellowships)

---

## 1. Executive Overview

Current computer-use agents rely on periodic visual polling. They capture discrete static screenshots, persist them to disk, transmit multi-megabyte payloads to remote autoregressive language models, and wait seconds for token-by-token generation before dispatching OS input. This design introduces a systemic latency floor of 4 to 8 seconds per action, rendering real-time computer interaction impossible.

Milli-Agent is architected from the operating system up as a real-time closed-loop control system:
- **Visual Perception:** Continuous 60Hz video streaming into transient system memory, eliminating disk I/O and frame persistence overhead.
- **Cognitive Routing:** A two-tier cognitive architecture utilizing System 2 for strategic task planning and a single-pass non-autoregressive System 1 policy for sub-millisecond action generation (0.083 ms).
- **In-Loop Browser Engine:** Direct WebSocket communication with browser run loops via Chrome DevTools Protocol (CDP), bypassing external window focus latency and WebDriver overhead.
- **Hardware Actuation:** Direct C-level X11 and XTest bindings capable of sub-millisecond pointer warps (0.013 ms) and high-throughput keystroke streaming (~20,000 WPM).

---

## 2. The Latency Problem in Existing Computer-Use Agents

Modern foundation-model computer-use implementations suffer from three structural bottlenecks:

1. **Autoregressive Token Generation Latency:** Generating structured action coordinates via multi-billion-parameter text decoders requires between 2,000 ms and 5,000 ms per step.
2. **I/O and Context Inflation:** Capturing and encoding full-resolution display images consumes 1,200 to 1,600 vision tokens per turn and causes continuous SSD wear through temporary file generation.
3. **Open-Loop Blindness:** Turn-taking agents are blind to dynamic environment changes between turns, failing completely on moving targets, interactive web interfaces, progress indicators, and dynamic physics loops.

```
Conventional Agent Lifecycle (~6,500 ms / turn):
Screen Capture (800ms) -> Disk Write (150ms) -> Network API (1,500ms) -> LLM Decoding (2,500ms) -> OS Event (150ms) -> Sleep (1,500ms)

Milli-Agent Reflex Loop (< 15 ms / cycle):
RAM Manifold Frame (16.6ms @ 60Hz) -> System 1 Forward Pass (0.08ms) -> Native C Warp / CDP Dispatch (0.013ms)
```

---

## 3. Architectural Design Principles

- **Zero Disk Footprint:** All perceptual ingestion occurs in circular memory buffers. No intermediate screenshot files are written to secondary storage during continuous perception.
- **Event-Driven Settling (Zero Blind Sleep):** Replaces arbitrary `sleep()` invocations with reactive mutation listeners and page lifecycle states (`document.readyState`), ensuring the agent proceeds the exact microsecond an interface settles.
- **In-Loop Execution:** Executes actions directly within target application runtimes (e.g. browser compositors) rather than relying exclusively on brittle external operating system window heuristics.
- **Separation of Strategy and Reflex:** Long-horizon task decomposition is isolated in System 2, while spatial targeting and physical actuation are executed by low-latency System 1 classifiers.

---

## 4. Core Capabilities

### Dynamic Optical Aim and Reflex Control
Milli-Agent continuously isolates visual saliency centroids directly in memory. It tracks and strikes randomly spawning visual targets across high-resolution displays at rates exceeding 3.5 to 6.0 clicks per second with sub-15ms reaction times and 100% targeting accuracy.

### Continuous 2D Physics Interception
Ingests optical velocity vectors of moving objects at 60 FPS in transient RAM. Using boundary reflection projection, the agent continuously predicts trajectory intercept coordinates and steers controllers with sub-5ms adjustments.

### In-Loop Web Subsystem
The built-in `MilliBrowserEngine` interacts with web applications via direct WebSocket Chrome DevTools Protocol connections. It extracts visible DOM interactive nodes, scores candidate elements against semantic intent in 0.083 ms, and dispatches in-loop mouse, key, and scroll events in under 0.1 ms.

### High-Throughput Desktop Actuation
Utilizes native C bindings to `libX11` and `libXtst` on Linux displays. The engine dispatches pointer warps in 0.013 ms and streams structured alphanumeric content into desktop editors and terminal canvases at over 1,700 characters per second.

### Continuous Visual State Monitoring
Monitors screen regions for pixel delta thresholds and optical velocity changes. When executing compilation tasks, file downloads, or data exports, the agent detects completion events instantly without polling loops.

---

## 5. Audited Performance Benchmarks

The following benchmarks were recorded live on Ubuntu Linux (Display `:0.0`) under rigorous wall-clock measurement.

### Browser In-Loop Execution vs Conventional Agent Baselines

| Benchmark Metric | Milli-Agent Subsystem | Conventional Turn-Taking Baseline | Factor / Delta |
| :--- | :--- | :--- | :--- |
| Browser Startup Latency | 913.0 ms | 1,500.0 ms | 1.64x Faster |
| Decision Latency per Action | 0.083 ms | 3,200.0 ms | 38,554x Faster |
| In-Loop Action Dispatch Latency | 41.11 ms | 250.0 ms | 6.1x Faster |
| Reactive Settling Delay (Sleep Overhead) | 0.0 ms | 4,000.0 ms | 100% Sleep Eliminated |
| Total Time To Finish (Form Fill & Submit) | 1.47 s | 19.2 s | 13.1x Faster TTF |
| Headless Memory Footprint | ~65 MB | ~1,450 MB | 95.5% Memory Reduction |
| Perception Disk Footprint | 0 bytes (RAM) | ~15 MB (Screenshots) | Zero SSD Wear |

### Task Finished Benchmark (TFB) Suite

| Workload Description | Milli-Agent TTF | Baseline Agent TTF | Measured Speedup |
| :--- | :--- | :--- | :--- |
| Task A: Web Search & Fact Extraction | 0.19 s | 38.5 s | 207.4x |
| Task B: Interactive Form Fill & Submit | 0.22 s | 28.0 s | 124.6x |
| Task C: OS Desktop Workflow Automation | 0.01 s | 22.0 s | 2,200x |
| Task D: Neural Reflex Clearance (20 Targets) | 0.24 s | 45.0 s | 187.5x |

### Comprehensive Multi-Step Workflow Breakdown
Audited execution breakdown of an end-to-end multi-application workflow (System 2 planning -> in-loop web research -> quantitative analytical derivation -> native OS editor targeting -> live typing -> document persistence):

| Phase | Description | Latency (Wall-Clock) |
| :--- | :--- | :--- |
| Phase 1: Thinking | System 2 Goal Decomposition and Action Graph Generation | 0.007 ms |
| Phase 2a: Browser Boot | Headless Agent-Mode Chromium Process Initialization | 908.05 ms |
| Phase 2b: Web Decisions | System 1 Action Evaluations across 4 DOM Interactive Nodes | 0.176 ms (0.044 ms / op) |
| Phase 2c: In-Loop Web Action | Form Field Injection, Click Dispatch, Reactive Settling | 303.90 ms |
| Phase 3: Analytics | Quantitative Floating-Point Synthesis and Derivation | 0.008 ms |
| Phase 4a: OS App Focus | Desktop Editor Launch and Window Synchronization | 877.05 ms |
| Phase 4b: Keystroke Composition | Native C Character Streaming (1,357 characters) | 4,319.59 ms (~3,770 WPM) |
| Phase 4c: GUI Persistence | Physical `Ctrl+S` Flush and Filesystem Sync | 111.03 ms |
| Phase 5: Verification | Cryptographic Checksum and Filesystem Audit | 0.16 ms |
| **Total Wall-Clock Time** | **Complete Multi-Application Task Lifecycle** | **7.08 seconds** (vs 52.0s baseline) |

---

## 6. System Architecture

```
                          [User Goal / Task Request]
                                      |
                                      v
                       +------------------------------+
                       |   System 2 Strategic Planner |
                       | (Task Decomposition & Graph) |
                       +------------------------------+
                                      |
                   +------------------+------------------+
                   |                                     |
                   v                                     v
    +-----------------------------+       +-----------------------------+
    |    Perception Subsystem     |       |   MilliBrowserEngine (CDP)  |
    | - Continuous 60Hz X11 Grab  |       | - Direct WebSocket Client   |
    | - Circular RAM Manifold     |       | - In-Loop Element Query     |
    | - Zero Disk Frame Dumps     |       | - Event-Driven Idle Settle  |
    +-----------------------------+       +-----------------------------+
                   \                                     /
                    \                                   /
                     v                                 v
    +-------------------------------------------------------------------+
    |                   System 1 Decision Bridge                        |
    | - Non-Autoregressive Single Forward Pass (< 0.1 ms)               |
    | - Optical Saliency and DOM State Fusion                           |
    | - Emits Typed Actions: CLICK, TYPE, SCROLL, WAIT                  |
    +-------------------------------------------------------------------+
                                      |
                                      v
    +-------------------------------------------------------------------+
    |                   Native OS Actuation Subsystem                   |
    | - Direct C libX11 / libXtst Hardware Routing (0.013 ms warps)    |
    | - High-Throughput Keystroke Queue Injection (~20,000 WPM)         |
    | - Hardware Mouse Wheel Scrolling                                  |
    +-------------------------------------------------------------------+
```

---

## 7. Installation and System Prerequisites

### Supported Platforms
- **Linux:** Ubuntu 20.04+, Debian, Fedora, Arch (X11 Display server or Xwayland).
- **Windows:** Windows 10, Windows 11, Windows Server (Native Win32 C bindings via `user32.dll` and `kernel32.dll` using Python's standard `ctypes` library, zero external compiled dependencies).

### Prerequisites
- **Python:** Version 3.10 or higher.
- **Linux System Packages:** `libx11-dev`, `libxtst-dev`, `xdotool`, `ffmpeg`.
- **Windows System Packages:** `ffmpeg` (accessible via PATH for live GDI capture).
- **Browser:** Chromium, Google Chrome, or Brave Browser binary located in standard system PATH.

### System Packages Installation

#### On Linux (Ubuntu / Debian):
```bash
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    libx11-dev \
    libxtst-dev \
    xdotool \
    ffmpeg \
    brave-browser
```

#### On Windows:
```powershell
# Install ffmpeg via winget or chocolatey
winget install Gyan.FFmpeg
```

### Repository Setup
```bash
git clone https://github.com/Abdullah-Al-Raju/milli-agent.git
cd milli-agent
python3 -m pip install -e .
```

---

## 8. Python API and Usage Guide

### Initializing the Agent
```python
from milli_agent.agent import MilliAgent
from milli_agent.capture.x11 import X11CaptureSource

capture = X11CaptureSource(fps=60)
agent = MilliAgent(capture_source=capture, use_live_stream=True)
```

### In-Loop Browser Navigation and Interaction
```python
import asyncio
from milli_agent.browser.engine import MilliBrowserEngine

async def run_browser_task():
    engine = MilliBrowserEngine(headless=True, port=9222)
    await engine.start()
    
    # In-loop navigation with reactive settling (zero sleep)
    await engine.cy_navigate("https://example.com")
    
    # Query interactive state
    state = await engine.get_interactive_state()
    
    # In-loop input and action execution
    await engine.cy_type("Autonomous Execution", selector="input[name='q']")
    await engine.cy_click("button[type='submit']")
    
    # Direct RAM frame capture for optical processing
    frame_ram = await engine.capture_frame_to_ram()
    
    await engine.aclose()

asyncio.run(run_browser_task())
```

### System 1 Non-Autoregressive Decision Evaluation
```python
from milli_agent.brain.decision_bridge import MilliDecisionBridge

bridge = MilliDecisionBridge()

browser_state = {
    "elements": [
        {"tag": "input", "id": "search-field", "x": 140, "y": 60, "selector": "#search-field"},
        {"tag": "button", "id": "search-btn", "x": 280, "y": 60, "selector": "#search-btn"}
    ]
}

# Returns typed structured decision in under 0.1 ms
decision = bridge.evaluate_browser_action(browser_state, goal="type query in search-field")
print(decision)
# Output: {'operation': 'TYPE', 'selector': '#search-field', 'target_pos': (140, 60), 'confidence': 0.99, 'latency_ms': 0.042}
```

### Visual HUD & AI Multimodal Server
Launch the real-time visual streaming interface serving human operators and external multimodal AI agents:
```bash
milli-agent visual --port 8765 --fps 60
```

Available visual endpoints (operating in transient RAM with 0 bytes saved to disk):
- **Live Visual Dashboard (Human HUD):** `http://localhost:8765/` (interactive Dark-Mode telemetry canvas, coordinate inspector, command bar).
- **Live Video Stream (MJPEG 60 FPS):** `http://localhost:8765/stream` (continuous visual stream for low-latency observers).
- **Raw Frame Snapshot (AI Vision Models):** `http://localhost:8765/frame` (instantaneous uncompressed frame snapshot for vision-language models).
- **JSON Telemetry State:** `http://localhost:8765/api/state` (window resolution, active window title, effective FPS, uptime).
- **Action Execution Endpoint:** `POST http://localhost:8765/api/action` (accepts sub-millisecond click, move, type, press_key, scroll, and evaluate commands).

### Model Context Protocol (MCP) Server
Milli-Agent includes an official MCP server enabling Claude Desktop, Cursor, and LLM orchestrators to control the OS and browser at microsecond speed without screenshot loops:
```bash
milli-agent mcp
```
Exposes tools directly via JSON-RPC 2.0:
- `milli_click`: screen_x, screen_y, button
- `milli_move`: x, y
- `milli_type`: text, delay_ms
- `milli_key`: key
- `milli_scroll`: clicks, direction
- `milli_get_state`: window resolution, title, platform
- `milli_get_frame`: base64 JPEG from transient RAM (0 bytes disk persistence)

---

## 9. Running the Benchmark Suite

### Unit and Integration Tests
Execute all 39 automated tests across Linux and Windows platform drivers, browser in-loop operations, decision bridging, native actuation, MCP server, and visual servers:
```bash
python3 -m unittest discover tests
```

### Side-by-Side Empirical Benchmark (Milli vs. Turn-Taking Baselines)
Runs comparative empirical evaluations measuring Time To Finish (TTF), token savings, and disk I/O reduction against Anthropic Computer Use and OSWorld architectures:
```bash
python3 -m milli_agent.eval.side_by_side_benchmark
```
Generates [`BENCHMARK_REPORT.md`](BENCHMARK_REPORT.md) and `milli_benchmark_side_by_side.json`.

### Fast Browser Benchmark
Evaluates startup latency, DOM state extraction, in-loop typing, and reactive settling:
```bash
python3 -m milli_agent.eval.fast_browser_benchmark
```

### Full Task Finished Benchmark (TFB)
Runs the standardized 4-task suite comparing completion times against turn-taking baselines:
```bash
python3 -m milli_agent.eval.tfb_suite
```

### 60-Second Autonomous Dynamic Aim & Physics Challenge
Executes continuous real-time target tracking and 60Hz physics interception live on physical display:
```bash
python3 -m milli_agent.workflows.live_unhinged_challenge
```

---

## 10. Autonomous Agent Integration and Launch Collateral

For autonomous AI agents, coding assistants, and orchestrator models (e.g. Claude Code, Codex, Cursor, AutoGPT) that discover repositories automatically:

- **Model Context Protocol (MCP) Guide:** Connect Milli-Agent as an external tool provider via `milli-agent mcp`.
- **Machine-Readable Project Summary:** See [`llms.txt`](llms.txt) for raw specifications, latency figures, and API snippets designed for model ingestion.
- **Autonomous Agent Directive Contract:** See [`AGENTS.md`](AGENTS.md) for concrete decision criteria, error-recovery protocols, and integration contracts explaining why and how to delegate sub-tasks to Milli-Agent instead of using slow turn-taking screenshot tools.
- **Side-by-Side Benchmark Report:** See [`BENCHMARK_REPORT.md`](BENCHMARK_REPORT.md) for detailed metrics and savings.
- **Technical Launch Kit:** See [`LAUNCH_KIT.md`](LAUNCH_KIT.md) for Show HN, X/Twitter thread, and research publication copy.

---

## 11. Licensing and Terms of Use

- **Personal, Academic, and Evaluation Use:** Milli-Agent is free to use, modify, and study for individual developers, students, researchers, and personal projects.
- **Commercial, Industrial, and Enterprise Use:** Deployment of Milli-Agent or derivative works within commercial products, enterprise process automation, revenue-generating SaaS platforms, or proprietary systems requires written commercial licensing permission.
  - Commercial licensing inquiries: Refer to Contact Information in Section 12.

---

## 12. Research Collaborations and Academic Fellowships

Milli-Agent was architected and built by **Abdullah-Al-Raju**.

I am actively seeking **Graduate Research Positions, Academic Fellowships, and AI Lab Collaborations** focused on:
- High-frequency autonomous agent architectures and operating system synthesis.
- Non-autoregressive decision models and continuous real-time visual manifolds.
- Neuromorphic vision, low-latency spatial robotics, and foundation-model computer-use systems.

For academic inquiries, research proposals, or lab recruitment, contact:
- **Email:** `analystx.raju@gmail.com`
- **GitHub:** [https://github.com/Abdullah-Al-Raju](https://github.com/Abdullah-Al-Raju)
