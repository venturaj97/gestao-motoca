from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    if not isinstance(senha, str):
        senha = str(senha)

    b = senha.encode("utf-8")

    if len(b) > 72:
        raise ValueError("senha_maior_que_72_bytes")

    return pwd_context.hash(senha)

