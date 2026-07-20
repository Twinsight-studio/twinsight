"""Supabase keep-alive job entrypoint (twinsight-job image).

Triggered by Cloud Scheduler -> Cloud Run Job every 3 days, to keep the
Supabase Free project from being auto-paused after 7 days idle.
TODO: implement `SELECT now()` against DATABASE_MIGRATION_URL (session-mode
pooler; this job doesn't need transaction pooling).
"""


def main() -> None:
    print("TODO: keep-alive")


if __name__ == "__main__":
    main()
