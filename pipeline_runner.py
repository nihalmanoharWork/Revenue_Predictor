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


def commit_files(file_paths):
    """
    Add, commit, and push updated files to GitHub.
    Uses force-add (-f) to override .gitignore.
    """
    existing_files = [f for f in file_paths if os.path.exists(f)]
    if not existing_files:
        print("⚠️ No files found to commit.")
        return

    # Force-add files to bypass .gitignore
    subprocess.run(["git", "add", "-f"] + existing_files, check=True)

    commit_msg = f"Automated daily run - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    commit_result = subprocess.run(["git", "commit", "-m", commit_msg], text=True)

    if commit_result.returncode == 0:
        subprocess.run(["git", "push"], check=True)
        print("✅ Updated files committed and pushed successfully!")
    else:
        print("ℹ️ No changes to commit. Files may not have changed.")


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

    # Run all pipeline steps
    for step in steps:
        run_step(step["name"], step["script"], step.get("args", []))

    # Commit updated CSVs to GitHub
    csv_files = ["data/revenue_data.csv", "data/predictions.csv"]
    commit_files(csv_files)

    print("\n🎉 All steps completed successfully!")


if __name__ == "__main__":
    main()
