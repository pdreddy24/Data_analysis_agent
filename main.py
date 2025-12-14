from __future__ import annotations

from agent.service import run_analysis


def main():
    print(" Data Analysis Agent")

    dataset_path = input(" Enter dataset path: ").strip()
    if not dataset_path:
        print(" Dataset path cannot be empty")
        return

    preview = run_analysis(question=None, dataset_path=dataset_path, preview_only=True)
    print("\n DATASET SCHEMA PREVIEW")
    print(preview["schema"])

    previous_plan = None

    while True:
        question = input("\n Enter your question (or 'exit'): ").strip()
        if not question:
            print(" Question cannot be empty")
            continue
        if question.lower() in ["exit", "quit", "q"]:
            break

        result = run_analysis(
            question=question,
            dataset_path=dataset_path,
            preview_only=False,
            previous_plan=previous_plan,
        )

        if "error" in result:
            print("\n ERROR:", result["error"])
            if "plan" in result:
                print(" PLAN:", result["plan"])
            continue

        print("\n=== ANALYSIS PLAN ===")
        print(result["plan"])

        if "result_df" in result:
            print("\n=== RESULT DATA ===")
            print(result["result_df"])

        if "figure_path" in result:
            print("\n=== CHART OUTPUT ===")
            print("Saved chart at:", result["figure_path"])

        print("\n=== EXPLANATION ===")
        print(result.get("explanation", ""))

        previous_plan = result["plan"]


if __name__ == "__main__":
    main()
