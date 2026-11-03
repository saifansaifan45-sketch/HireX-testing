import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run all HireX automated tests and synchronize reports")
    parser.add_argument("--headed", action="store_true", help="Launch visible browser windows")
    parser.add_argument("--slowmo", type=int, default=0, help="Slow down Playwright actions by milliseconds")
    args = parser.parse_args()

    pytest_cmd = [
        sys.executable, "-m", "pytest", "tests/", "-v",
        "--junitxml=reports/junit.xml"
    ]
    if args.headed:
        pytest_cmd.append("--headed")
    if args.slowmo > 0:
        pytest_cmd.extend(["--slowmo", str(args.slowmo)])

    print("================================================================================")
    print("🚀 Starting HireX Complete End-to-End Test Suite Execution")
    print(f"Command: {' '.join(pytest_cmd)}")
    print("================================================================================")

    # Execute Pytest
    res = subprocess.run(pytest_cmd)

    print("\n================================================================================")
    print("📊 Synchronizing Results with Test Cases Workbook & RTM...")
    print("================================================================================")
    
    # Synchronize results
    sync_cmd = [sys.executable, "scripts/sync_results.py"]
    subprocess.run(sync_cmd)

    print("================================================================================")
    print("✅ All Tests Completed! Reports generated:")
    print("  - HireX_Complete_Test_Cases.xlsx")
    print("  - HireX_Requirements_Traceability_Matrix.xlsx")
    print("  - HireX_Automation_Execution_Report.html")
    print("  - HireX_Test_Execution_Report.xlsx")
    print("  - HireX_Defect_Report.xlsx")
    print("================================================================================")

if __name__ == "__main__":
    main()

