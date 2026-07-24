"""External data-source clients.

Shared rather than per-module because FinMind feeds both `chips` and
`stocks`; a module-local client would have to be duplicated. Modules own
their queries (repository.py); these own the wire format.

All clients use httpx — no vendor SDKs, so there is nothing extra to keep
up to date and no surprise transitive dependencies.
"""
