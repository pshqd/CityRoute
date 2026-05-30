"""Run full experiment grid and save CSV + plots."""
from pathlib import Path

from app.services.experiment_runner import run_experiments
from app.services.plotter import plot_all

OUT_DIR = Path("results")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("Running experiments...")
    df = run_experiments()

    csv_path = OUT_DIR / "baseline_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"Results saved to {csv_path}")
    print(df.to_string(index=False))

    plot_all(df)


if __name__ == "__main__":
    main()
