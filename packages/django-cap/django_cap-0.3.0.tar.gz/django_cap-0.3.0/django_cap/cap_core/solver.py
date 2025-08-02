import hashlib

from django_cap.cap_core.cap import Cap
from django_cap.cap_core.utils import ChallengeType


def solve(
    challenge: str | list[list[str]], config: ChallengeType | None = None
) -> list[int]:
    """
    Solve CAP challenges using proof-of-work algorithm.

    Args:
        challenge: Challenge token string
        config: Configuration of this challenge
    Returns:
        list of nonces (solutions) for each challenge
    """
    if isinstance(challenge, str):
        assert config is not None, (
            "Config must be provided if you want generate challenges from token"
        )
        # Generate challenges from token
        challenges = Cap.generate_challenge_from_token(challenge, config)
    elif isinstance(challenge, list):
        # Assume challenge is already a list of (salt, target) tuples
        challenges = challenge
    else:
        raise ValueError("Invalid challenge format, must be str or list")

    results = [solve_pow(salt, target) for salt, target in challenges]

    return results


def py_solve_pow(salt: str, target: str) -> int:
    """
    Solve a single proof-of-work challenge.

    Args:
        salt: Salt string to prepend to nonce
        target: Target hex string that hash must start with

    Returns:
        Nonce value that produces valid hash
    """
    for nonce in range(2**64):  # Iterate through possible nonces
        # Create hash input: salt + nonce
        hash_input = salt + str(nonce)

        # Calculate SHA256 hash
        hash_result = hashlib.sha256(hash_input.encode()).hexdigest()

        # Check if hash starts with target
        if hash_result.startswith(target):
            return nonce

    raise RuntimeError("Solution not found within u64 range")


try:
    from ._cap_rust import rust_solve_pow

    # Why this is slower than python implementation??
    solve_pow = rust_solve_pow
except ImportError:
    solve_pow = py_solve_pow
