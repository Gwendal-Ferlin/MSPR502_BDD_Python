"""Émet les littéraux SQL Fernet pour init/postgres-sante/02_seed.sql (clé = .env.example)."""
from __future__ import annotations

from cryptography.fernet import Fernet

KEY = b"Teb9fyXE4L28LXo5pC5JGRESG-aTXb6TJ1IxkfdQOQM="
f = Fernet(KEY)


def enc(s: str) -> str:
    return f.encrypt(str(s).encode()).decode("ascii")


def main() -> None:
    refs = [
        ("Sans gluten", "Allergie"),
        ("Lactose", "Intolérance"),
        ("Végétarien", "Régime"),
        ("Arachides", "Allergie"),
        ("Vegan", "Régime"),
        ("halal", "Régime"),
        ("kosher", "Régime"),
        ("sans lactose", "Intolérance"),
        ("sans gluten", "Allergie"),
        ("sans soja", "Allergie"),
        ("sans arachides", "Allergie"),
        ("sans fruits de mer", "Allergie"),
        ("sans oeufs", "Allergie"),
        ("sans mollusques", "Allergie"),
    ]
    for n, t in refs:
        print(f"('{enc(n)}', '{enc(t)}'),")

    print("---PROFIL---")
    profils = [
        ("1992", "F", "165", "Modéré"),
        ("1988", "H", "178", "Élevé"),
        ("1995", "F", "172", "Faible"),
        ("1985", "H", "182", "Modéré"),
    ]
    for row in profils:
        print(
            "("
            + ", ".join(f"'{enc(x)}'" for x in row)
            + "),"
        )

    print("---BIO---")
    bio = [("61.2", "7"), ("60.8", "8"), ("74.5", "6"), ("65.0", "7")]
    for p, s in bio:
        print(f"'{enc(p)}', '{enc(s)}'")


if __name__ == "__main__":
    main()
