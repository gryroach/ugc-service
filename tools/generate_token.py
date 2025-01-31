# stdlib
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# thirdparty
import jwt

ALGORITHM = "RS256"
TOKEN_EXPIRE_DAYS = 7
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class JWTService:
    def __init__(self) -> None:
        private_key_path = os.path.join(SCRIPT_DIR, "keys", "example_private_key.pem")
        public_key_path = os.path.join(SCRIPT_DIR, "keys", "example_public_key.pem")

        with open(private_key_path, "r") as private_key_file:
            self.private_key = private_key_file.read()
        with open(public_key_path, "r") as public_key_file:
            self.public_key = public_key_file.read()

    def _create_token(self, payload: dict) -> str | bytes:
        """Создает JWT-токен с подписью приватным ключом (асимметричный)."""
        return jwt.encode(payload, self.private_key, algorithm=ALGORITHM)

    def create_access_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user": user_id,
            "session_version": 1,
            "iat": now,
            "exp": now + timedelta(days=TOKEN_EXPIRE_DAYS),
            "role": "regular_user",
            "type": "access",
        }
        jwt_token = self._create_token(payload)
        if isinstance(jwt_token, bytes):
            return jwt_token.decode("utf-8")
        return jwt_token


if __name__ == "__main__":
    user_id = input(
        "Введите user_id в формате UUID, либо нажмите Enter, чтобы он был сгенерирован: "
    )
    if not user_id.strip():
        user_id = str(uuid4())
    token = JWTService().create_access_token(user_id)
    print(f"Сгенерированный токен для пользователя {user_id}:", token, sep="\n")
