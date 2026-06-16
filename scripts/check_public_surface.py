from pathlib import Path
import sys

def main():
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    
    banned_terms = [
        "portfolio_v2", "v2.1", "v2.2", 
        "career", "recruiter", "LinkedIn", "interview"
    ]
    
    failed = False
    for term in banned_terms:
        if term.lower() in readme.lower():
            print(f"FAILED: Found banned term '{term}' in README.md")
            failed = True
            
    # Check that image paths do not point to archive or reports/portfolio_*
    import re
    image_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
    for raw_path in image_paths:
        if "archive/" in raw_path or "reports/portfolio_" in raw_path:
            print(f"FAILED: Found banned path '{raw_path}' in README.md")
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
