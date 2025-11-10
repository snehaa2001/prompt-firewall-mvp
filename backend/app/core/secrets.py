import os
from google.cloud import secretmanager
from functools import lru_cache

IS_CLOUD_RUN = os.getenv("K_SERVICE") is not None
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "prompt-firewall-mvp-1762592086")


@lru_cache(maxsize=10)
def access_secret_version(secret_id: str, version_id: str = "latest") -> str:
    if not IS_CLOUD_RUN:
        return os.getenv(secret_id, "")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"

    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error accessing secret {secret_id}: {e}")
        raise


def get_openai_api_key() -> str:
    return access_secret_version("OPENAI_API_KEY")


def get_jwt_secret_key() -> str:
    return access_secret_version("JWT_SECRET_KEY")


def get_anthropic_api_key() -> str:
    return access_secret_version("ANTHROPIC_API_KEY")
