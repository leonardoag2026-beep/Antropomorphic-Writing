"""
Standard Pipeline v1.7.0

Single pass (5 steps):
  Step 0: Input → Portuguese — LLM rewrite
  Step 1: Portuguese → Chinese — LLM rewrite
  Step 2: Chinese → Japanese — LLM rewrite (with history)
  Step 3: Japanese → Finnish — Google Translate
  Step 4: Finnish → Target — Niutrans Web / Google

Double pass (10 steps, --double-pass):
  Pass 1: Input → PT → 中文 → 日本語 → fi → PT
  Pass 2: PT → 中文 → 日本語 → fi → Target
"""

import time
import click
import toml

from .llm_client import resolve_llm_config
from .translators import google_translate, niutrans_web_translate
from .llm_rewriter import llm_rewrite


def _run_pass(text: str, config: dict, target_lang: str,
              llm: dict, intermediate_lang: str, step_offset: int = 0,
              skip_step0: bool = False, original_input: str | None = None) -> tuple:
    """
    Run a single pass through the pipeline.

    Args:
        skip_step0: If True, skip the Input→Portuguese step (text is already PT).
        original_input: Original input text (for history in step 2 when skipping step 0).

    Returns:
        (result_text, steps_list)
    """
    engine_name = llm["display_name"]
    steps = []

    if not skip_step0:
        step0 = llm_rewrite(
            text=text,
            target_language="葡萄牙语",
            api_key=llm["api_key"],
            base_url=llm["base_url"],
            model=llm["model"],
            history=None,
            temperature=llm["temperature"],
            extra_headers=llm["extra_headers"],
            provider=llm["provider"],
        )
        steps.append({
            "step": step_offset + 0, "engine": engine_name,
            "direction": "Input → Portuguese (葡萄牙语改写)",
            "output": step0, "length": len(step0),
        })
        pt_text = step0
        prev_input = text
    else:
        pt_text = text
        prev_input = original_input or text

    step1 = llm_rewrite(
        text=pt_text,
        target_language="中文",
        api_key=llm["api_key"],
        base_url=llm["base_url"],
        model=llm["model"],
        history={"input": prev_input, "output": pt_text},
        temperature=llm["temperature"],
        extra_headers=llm["extra_headers"],
        provider=llm["provider"],
    )
    steps.append({
        "step": step_offset + 1, "engine": engine_name,
        "direction": "Portuguese → Chinese (中文改写)",
        "output": step1, "length": len(step1),
    })

    step2 = llm_rewrite(
        text=step1,
        target_language="日语",
        api_key=llm["api_key"],
        base_url=llm["base_url"],
        model=llm["model"],
        history={"input": pt_text, "output": step1},
        temperature=llm["temperature"],
        extra_headers=llm["extra_headers"],
        provider=llm["provider"],
    )
    steps.append({
        "step": step_offset + 2, "engine": engine_name,
        "direction": "Chinese → Japanese (日语改写)",
        "output": step2, "length": len(step2),
    })

    step3 = google_translate(step2, source="ja", target=intermediate_lang)
    steps.append({
        "step": step_offset + 3, "engine": "Google",
        "direction": f"Japanese → {intermediate_lang.upper()}",
        "output": step3, "length": len(step3),
    })

    try:
        step4 = niutrans_web_translate(step3, source=intermediate_lang, target=target_lang)
        engine_name_4 = "Niutrans Web"
    except Exception:
        step4 = google_translate(step3, source=intermediate_lang, target=target_lang)
        engine_name_4 = "Google"
    steps.append({
        "step": step_offset + 4, "engine": engine_name_4,
        "direction": f"{intermediate_lang.upper()} → {target_lang.upper()}",
        "output": step4, "length": len(step4),
    })

    return step4, steps


def run_standard_pipeline(text: str, config: dict, target_lang: str = "en",
                          double_pass: bool = True) -> dict:
    llm = resolve_llm_config(config)
    intermediate_lang = config.get("pipeline", {}).get("intermediate_lang", "fi")

    all_steps = []
    start = time.time()

    if double_pass:
        # Pass 1: Input → Portuguese → Chinese → Japanese → Finnish → Portuguese
        mid_result, pass1_steps = _run_pass(
            text, config, target_lang="pt",
            llm=llm, intermediate_lang=intermediate_lang, step_offset=0,
            skip_step0=False, original_input=None,
        )
        all_steps.extend(pass1_steps)

        # Pass 2: Portuguese → Chinese → Japanese → Finnish → Target
        final_result, pass2_steps = _run_pass(
            mid_result, config, target_lang=target_lang,
            llm=llm, intermediate_lang=intermediate_lang, step_offset=5,
            skip_step0=True, original_input=text,
        )
        all_steps.extend(pass2_steps)
    else:
        final_result, pass_steps = _run_pass(
            text, config, target_lang=target_lang,
            llm=llm, intermediate_lang=intermediate_lang, step_offset=0,
            skip_step0=False, original_input=None,
        )
        all_steps = pass_steps

    elapsed_ms = int((time.time() - start) * 1000)

    return {
        "result": final_result,
        "steps": all_steps,
        "processing_time_ms": elapsed_ms,
    }


@click.command()
@click.option("--input", "input_text", required=True, help="Input text or path to text file")
@click.option("--target", default="en", help="Target language code (default: en)")
@click.option("--config", default="config/config.toml", help="Config file path")
@click.option("--output", default=None, help="Output file path")
@click.option("--verbose", is_flag=True, help="Show step-by-step progress")
@click.option("--double-pass", is_flag=True, help="Run pipeline twice for deeper humanization")
def main(input_text, target, config, output, verbose, double_pass):
    import os

    if os.path.isfile(input_text):
        with open(input_text, "r", encoding="utf-8") as f:
            input_text = f.read()

    cfg = toml.load(config)
    result = run_standard_pipeline(input_text, cfg, target_lang=target, double_pass=double_pass)

    if verbose:
        click.echo("\n--- Pipeline Steps ---")
        for s in result["steps"]:
            click.echo(f"  Step {s['step']}: {s['engine']} | {s['direction']} | {s['length']} chars")
        click.echo(f"  Total: {result['processing_time_ms']}ms\n")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result["result"])
        click.echo(f"Written to {output}")
    else:
        click.echo(result["result"])


if __name__ == "__main__":
    main()
