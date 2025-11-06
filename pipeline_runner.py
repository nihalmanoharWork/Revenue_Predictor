# pipeline_runner.py
import yaml
import subprocess
import sys
import time
import os

def run_step(name, script, args):
    """Run one pipeline step."""
    cmd = [sys.executable, script] + args
    print(f"\nStep: {name}")
    print(f"Running: {' '.join(cmd)}")
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start

    if result.returncode == 0:
        print(f"✅ Step '{name}' completed in {duration:.2f}s")
        print(result.stdout)
    else:
        print(f"❌ Step '{name}' failed with code {result.returncode}")
        print(result.stderr)
        sys.exit(result.returncode)

def commit_predictions(file_path="data/predictions.csv"):
    """Add, commit, and push the latest predictions to GitHub."""
    if not os.path.exists(file_path):
        print(f"⚠️ Predictions file '{file_path}' not found. Skipping commit.")
        return

    # Force add to bypass .gitignore
    subprocess.run(["git", "add", "-f", file_path], check=True)
    # Commit
    commit_result = subprocess.run(
        ["git", "commit", "-m", f"Automated daily run - {time.strftime('%Y-%m-%d %H:%M:%S')}"],
        text=True
    )
    # Skip push if no changes to commit
    if commit_result.returncode == 0:
        subprocess.run(["git", "push"], check=True)
        print("✅ Predictions committed and pushed successfully!")
    else:
        print("ℹ️ No changes to commit.")

def main():
    pipeline_file = "pipeline.yaml"
    if not os.path.exists(pipeline_file):
        print(f"Pipeline file '{pipeline_file}' not found.")
        sys.exit(1)

    with open(pipeline_file, "r") as f:
        pipeline = yaml.safe_load(f)

    steps = pipeline.get("steps", [])
    if not steps:
        print("No steps found in pipeline.yaml.")
        sys.exit(1)

    for step in steps:
        run_step(step["name"], step["script"], step.get("args", []))

    # Commit latest predictions
    commit_predictions()

    print("\n🎉 All steps completed successfully!")

if __name__ == "__main__":
    main()
