import os
import sys
import time
import click
from .agent import MilliAgent
from .capture.mock import MockCanvaDesktopSource
from .capture.x11 import X11CaptureSource
from .capture.video import VideoCaptureSource
from .engine.manifold import ManifoldEngine


class QuickRunGroup(click.Group):
    """Allows running goals directly (e.g. milli-agent 'open youtube, search mr beast') without typing 'run'."""
    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = ["run"] + args
        return super().parse_args(ctx, args)


@click.group(cls=QuickRunGroup)
def main():
    """Milli-Agent: Autonomous OS-Level Computer-Use Agent (Continuous 4D Manifold)."""
    pass


is_headless = not bool(os.environ.get("DISPLAY"))


@main.command()
@click.argument("goal", default="Open canva and draw a Milli mascot cat")
@click.option("--model", default="builtin", help="Model backend: builtin, ollama:qwen2.5-vl, openai:gpt-4o")
@click.option("--mock/--live", default=is_headless, help="Use simulated browser or live X11 desktop screen")
@click.option("--dry-run", is_flag=True, default=False, help="Log actions without moving OS mouse")
@click.option("--output-img", default=None, help="Save final canvas view to an image file")
def run(goal: str, model: str, mock: bool, dry_run: bool, output_img: str):
    """Execute any high-level autonomous goal."""
    click.echo(click.style("\n🚀 [Milli-Agent] Autonomous OS Execution Active", fg="cyan", bold=True))
    click.echo(f"  • Screen Mode: {'SIMULATION (Mock)' if mock else 'REAL PHYSICAL DESKTOP (Live X11)'}")
    click.echo(f"  • Target Display: {os.environ.get('DISPLAY', ':0.0')}")
    source = MockCanvaDesktopSource() if mock else X11CaptureSource()
    agent = MilliAgent(capture_source=source, model=model, dry_run=dry_run)
    try:
        res = agent.execute_goal(goal)
        if output_img and res.get("artifact_saved"):
            import shutil
            shutil.copyfile(res["artifact_saved"], output_img)
            click.echo(click.style(f"[Milli-Agent] 🖼  Exported final visual to {output_img}", fg="green"))
        click.echo(click.style(f"\n[Status] {res['status'].upper()} in {res['elapsed_seconds']}s", fg="green", bold=True))
    finally:
        agent.close()



@main.command("demo-cat")
@click.option("--dry-run", is_flag=True, default=False, help="Do not send physical OS mouse events")
@click.option("--output-img", default="milli_cat_demo.png", help="Path to export the drawn cat mascot image")
def demo_cat(dry_run: bool, output_img: str):
    """Run the signature demo: Open Canva moodboard and draw the Milli Mascot Cat!"""
    click.echo(click.style("\n🐱 [Milli-Agent] Running Signature Mascot Drawing Demo...", fg="magenta", bold=True))
    click.echo("Target: Canva Whiteboard Moodboard -> Continuous Spline Cat Mascot")
    source = MockCanvaDesktopSource()
    agent = MilliAgent(capture_source=source, model="builtin", dry_run=dry_run)
    res = agent.execute_goal("Open Canva moodboard and draw a Milli mascot cat")
    if output_img and res.get("artifact_saved"):
        import shutil
        shutil.copyfile(res["artifact_saved"], output_img)
        click.echo(click.style(f"\n✨ Mascot canvas exported to: {output_img}", fg="green", bold=True))



@main.command()
@click.option("--duration", default=5, help="Monitor duration in seconds")
@click.option("--mock", is_flag=True, default=True, help="Use mock stream instead of X11 screen")
def monitor(duration: int, mock: bool):
    """Monitor live 60 Hz spatiotemporal manifold visual telemetry in terminal."""
    click.echo(click.style(f"\n👁  [Milli-Agent] Monitoring Continuous 4D Manifold for {duration}s...", fg="cyan", bold=True))
    source = MockCanvaDesktopSource() if mock else X11CaptureSource()
    engine = ManifoldEngine()

    start_time = time.time()
    frames = 0

    while time.time() - start_time < duration:
        ok, frame = source.read_frame()
        if not ok:
            break
        v = engine.ingest_frame(frame)
        frames += 1

        delta_indicator = click.style("⚠ SHOCK DELTA TRIGGERED", fg="red", bold=True) if v["event_triggered"] else click.style("SMOOTH FLOW", fg="green")
        sys.stdout.write(
            f"\r[60Hz Engine] Frame: {frames:04d} | Vel: {v['mean_velocity']:05.2f} | Res: {v['residual_norm']:05.2f} | "
            f"Target: ({v['subpixel_target'][0]:.1f}, {v['subpixel_target'][1]:.1f}) | {delta_indicator} | Tokens Saved: {v['token_savings_percent']:.1f}%"
        )
        sys.stdout.flush()
        time.sleep(0.016)  # 60 FPS target

    source.close()
    click.echo(click.style("\n\n✓ Monitoring Complete. Static Scaffolds remain locked. Zero ViT drift.", fg="green", bold=True))


@main.command()
@click.option("--video", default=None, help="Path to video file for empirical benchmark (defaults to synthetic stream)")
def benchmark(video: str = None):
    """Run empirical benchmark against discrete ViT & 1-FPS baselines."""
    import os
    from .capture.mock import MockCaptureSource
    if video and os.path.exists(video):
        click.echo(click.style(f"\n📊 [Milli-Agent] Benchmarking '{video}'...", fg="yellow", bold=True))
        source = VideoCaptureSource(video_path=video, loop=False)
    else:
        click.echo(click.style(f"\n📊 [Milli-Agent] Benchmarking 60Hz synthetic optical manifold...", fg="yellow", bold=True))
        source = MockCaptureSource(width=1920, height=1080)
    engine = ManifoldEngine()

    frames = 0
    t0 = time.time()
    while True:
        ok, frame = source.read_frame()
        if not ok:
            break
        engine.ingest_frame(frame)
        frames += 1

    elapsed = time.time() - t0
    source.close()

    vit_cost = frames * 258
    fps_1_cost = max(1, int(frames / 30)) * 258
    milli_cost = engine.total_milli_tokens

    reduction_vit = (1.0 - milli_cost / vit_cost) * 100.0
    reduction_1fps = (1.0 - milli_cost / fps_1_cost) * 100.0

    click.echo(f"\n==========================================")
    click.echo(f"  Processed {frames} frames in {elapsed:.2f}s ({frames/elapsed:.1f} FPS)")
    click.echo(f"  Legacy 30-FPS ViT Tokens: ~{vit_cost:,} tokens")
    click.echo(f"  Frontier 1-FPS Tokens:    ~{fps_1_cost:,} tokens")
    click.echo(click.style(f"  Milli 4D Manifold Tokens: ~{milli_cost:,} tokens", fg="green", bold=True))
    click.echo(click.style(f"  Reduction vs ViT:         {reduction_vit:.2f}%", fg="green"))
    click.echo(click.style(f"  Reduction vs 1-FPS:       {reduction_1fps:.2f}%", fg="green"))
    click.echo(f"==========================================\n")


@main.command("visual")
@click.option("--host", default="0.0.0.0", help="HTTP server bind host")
@click.option("--port", default=8765, help="HTTP server bind port")
@click.option("--fps", default=60, help="Visual stream capture framerate")
@click.option("--dry-run", is_flag=True, default=False, help="Do not dispatch physical OS clicks")
def visual(host: str, port: int, fps: int, dry_run: bool):
    """Launch the real-time Visual HUD & AI Multimodal interface server."""
    from .visual.server import MilliVisualServer
    server = MilliVisualServer(host=host, port=port, fps=fps, dry_run=dry_run)
    server.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        server.stop()
        click.echo("\n[Milli-Agent] Visual server shut down cleanly.")


@main.command("mcp")
@click.option("--dry-run", is_flag=True, default=False, help="Do not dispatch physical OS clicks")
def mcp(dry_run: bool):
    """Launch Model Context Protocol (MCP) server for Claude Desktop, Cursor, and LLMs."""
    from .mcp.server import MilliMCPServer
    server = MilliMCPServer(dry_run=dry_run)
    server.run_stdio()


if __name__ == "__main__":
    main()

