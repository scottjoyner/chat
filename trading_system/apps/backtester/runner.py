import argparse
from analytics.metrics.performance import basic_metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    sample_returns = [0.01, -0.004, 0.007]
    print({"config": args.config, "metrics": basic_metrics(sample_returns)})


if __name__ == "__main__":
    main()
