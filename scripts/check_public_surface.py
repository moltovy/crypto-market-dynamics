import re
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")

    banned_terms = [
        "portfolio_v2", "v2.1", "v2.2", "v2.0",
        "career", "recruiter", "LinkedIn", "interview"
    ]

    failed = False
    for term in banned_terms:
        if term.lower() in readme.lower():
            print(f"FAILED: Found banned term '{term}' in README.md")
            failed = True

    # Check that README contains "Results at a Glance"
    if "results at a glance" not in readme.lower():
        print("FAILED: README.md does not contain 'Results at a Glance' section.")
        failed = True

    # Check that README links T11_results_at_a_glance.md
    if "t11_results_at_a_glance.md" not in readme.lower():
        print("FAILED: README.md does not link to T11_results_at_a_glance.md")
        failed = True

    # Check that image paths do not point to archive or reports/portfolio_*
    image_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
    for raw_path in image_paths:
        if "archive/" in raw_path or "reports/portfolio_" in raw_path:
            print(f"FAILED: Found banned path '{raw_path}' in README.md")
            failed = True

        # Check that old figure names are not embedded
        old_figs = [
            "F02_btc_model_sensitivity.png",
            "F01_data_inventory.png",
            "F02_btc_model_sensitivity",
            "F01_data_inventory"
        ]
        for old_fig in old_figs:
            if old_fig in raw_path:
                print(f"FAILED: Found old misleading figure '{old_fig}' embedded in README.md")
                failed = True

        path = root / raw_path
        if not path.exists():
            print(f"FAILED: Image path '{raw_path}' does not exist")
            failed = True

    if failed:
        sys.exit(1)
    else:
        print("Public surface check passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
