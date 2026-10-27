import time
from collections import defaultdict, deque

from fastapi import HTTPException, status


class LoginThrottle:
    def __init__(self, max_failures: int = 5, window_seconds: int = 15 * 60) -> None:
        self.max_failures = max_failures
        self.window = window_seconds
        self._failures: defaultdict[str, deque[float]] = defaultdict(deque)

    def _recent(self, key: str) -> deque[float]:
        attempts = self._failures[key]
        while attempts and attempts[0] <= time.monotonic() - self.window:
            attempts.popleft()
        return attempts

    def check(self, key: str) -> None:
        """Corta con 429 si `key` (la IP) ya acumuló demasiados fallos en la ventana."""
        attempts = self._recent(key)
        if len(attempts) >= self.max_failures:
            retry_after = int(attempts[0] + self.window - time.monotonic()) + 1
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Demasiados intentos fallidos. Probá más tarde.",
                headers={"Retry-After": str(retry_after)},
            )

    def fail(self, key: str) -> None:
        self._failures[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


login_throttle = LoginThrottle()
