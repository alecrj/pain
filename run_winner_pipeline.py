#!/usr/bin/env python3
"""
Master Orchestrator - Complete 3-Stage Winner Pipeline
Runs all stages automatically to find TRUE WINNERS
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*70}")
    print(f"🚀 {description}")
    print(f"{'='*70}\n")

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=False,
        text=True
    )

    if result.returncode != 0:
        print(f"\n❌ Error in {description}")
        sys.exit(1)

    print(f"\n✅ {description} - Complete!")
    return True

def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           🏆 TRUE WINNER PIPELINE v2.0 🏆                       ║
║                                                                  ║
║  3-Stage Filtering System for HIGH-GROWTH Opportunities         ║
║                                                                  ║
║  Stage 1: Growth Filter      (Kill 80%)                        ║
║  Stage 2: Budget Validator   (Kill 50% more)                   ║
║  Stage 3: Deep Research      (Find TRUE WINNERS)               ║
║                                                                  ║
║  Expected: 50 ideas → 10 pass S1 → 5 pass S2 → 1-2 WINNERS   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Stage 1: Growth Filter
    run_command(
        "python stage1_growth_filter.py",
        "STAGE 1: Growth Filter (High-growth industries + API feasibility)"
    )

    # Stage 2: Budget Validator
    run_command(
        "python stage2_budget_validator.py",
        "STAGE 2: Budget Validator (Proven spending + Decision makers)"
    )

    # Stage 3: Deep Research
    run_command(
        "python stage3_deep_research.py",
        "STAGE 3: Deep Research (Complete analysis + Final winners)"
    )

    print(f"""
{'='*70}
🎉 PIPELINE COMPLETE! 🎉
{'='*70}

📊 Check Results:
   - Google Sheet tabs for stage-by-stage filtering
   - WINNER_*.txt files for complete reports

🚀 Next Steps:
   1. Review TRUE WINNERS in "TRUE WINNERS" sheet tab
   2. Read WINNER_*.txt reports for full details
   3. Move to Stage 2: The Strategist (create lead magnets)

{'='*70}
    """)

if __name__ == "__main__":
    main()
