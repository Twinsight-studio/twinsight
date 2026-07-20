"""Post-market batch job entrypoint (twinsight-job image).

Triggered by Cloud Scheduler -> Cloud Run Job, Mon-Fri 14:35 Asia/Taipei.
TODO: implement. Needs the pandas/numpy/pandas-ta/yfinance stack, which is
why this lives in a separate image (Dockerfile.job) from the API.
"""


def main() -> None:
    print("TODO: 盤後批次")


if __name__ == "__main__":
    main()
