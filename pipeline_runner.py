import yaml
import subprocess
import sys
import time
import os

def run_step(name, script, args):
    """Run one pipeline step."""
    cmd = [sys.executable, script] + args
    print(f"\n🚀 Step: {name}")
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

    print("\n🎉 All steps completed successfully!")

if __name__ == "__main__":
    main()
