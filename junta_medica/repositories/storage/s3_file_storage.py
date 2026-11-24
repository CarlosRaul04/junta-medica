"""
S3FileStorage: guarda los resultados JSON y los informes PDF en un bucket de AWS S3.

Las credenciales NO van en el código: en EC2 se usa el rol IAM de la instancia; en una PC, `aws configure`
o las variables AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY.
"""
from botocore.exceptions import ClientError

from junta_medica.interfaces.file_storage import FileStorage

_NOT_FOUND = {"NoSuchKey", "404", "NotFound"}


class S3FileStorage(FileStorage):
    def __init__(self, client, bucket: str):
        self._client = client          # boto3.client("s3")
        self._bucket = bucket

    def save(self, key: str, content: bytes, content_type: str) -> str:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=content, ContentType=content_type,
                                ServerSideEncryption="AES256")
        return key

    def load(self, key: str) -> bytes | None:
        try:
            return self._client.get_object(Bucket=self._bucket, Key=key)["Body"].read()
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in _NOT_FOUND:
                return None
            raise
