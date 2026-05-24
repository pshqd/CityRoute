"""Generate and save sample scenarios to data/scenarios/."""
from pathlib import Path

from app.services.scenario_generator import generate_scenario

OUT_DIR = Path("data/scenarios")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    for n in [10, 20, 40]:
        for seed in [42, 7, 99]:
            scenario = generate_scenario(num_orders=n, seed=seed)
            out = OUT_DIR / f"scenario_n{n}_seed{seed}.json"
            out.write_text(scenario.model_dump_json(indent=2), encoding="utf-8")
            print(f"Saved {out}")


if __name__ == "__main__":
    main()
