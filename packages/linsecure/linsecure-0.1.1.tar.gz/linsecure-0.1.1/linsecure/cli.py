# linsecure/cli.py
import argparse
from linsecure.core import run_all_checks
import datetime

def main():
    parser = argparse.ArgumentParser(description="Linux vulnerability scanner")
    parser.add_argument("--output", help="Path to save the report", default=None)
    args = parser.parse_args()

    report = run_all_checks()

    if args.output:
        try:
            timestamp = datetime.datetime.now().isoformat()
            with open(args.output, "w") as f:
                f.write(f"# linsecure scan - {timestamp}\n\n")
                f.write(report + "\n")
            print(f"[✓] Report saved to: {args.output}")
        except Exception as e:
            print(f"[!] Failed to save report: {e}")
    else:
        print(report)

if __name__ == "__main__":
    main()
