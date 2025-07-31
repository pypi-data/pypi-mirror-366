import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Union

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    ContainerSasPermissions,
    generate_container_sas,
)


class AzureBlobManager:
    """A client for managing blobs in Azure Blob Storage.

    This client can be authenticated via a connection string, default Azure credentials, or a SAS URL.

    Attributes:
        blob_service_client: The Azure BlobServiceClient.
    """

    def __init__(
        self,
        conn_str: str = None,
        acc_url: str = None,
        sas_url: str = None,
    ):
        """Initializes the Azure Blob Manager.

        Args:
            conn_str: The connection string for the Azure Storage account.
            acc_url: The URL to the storage account (used with DefaultAzureCredential).
            sas_url: A SAS URL for authentication.
        """
        conn_str = conn_str or os.environ.get("AZURE_CONN_STR")
        acc_url = acc_url or os.environ.get("AZURE_ACCOUNT_URL")
        sas_url = sas_url or os.environ.get("AZURE_SAS_URL")

        try:
            if conn_str:
                logging.info("Initializing BlobServiceClient using connection string.")
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    conn_str
                )
            elif acc_url:
                logging.info(
                    "Initializing BlobServiceClient using DefaultAzureCredential."
                )
                credential = DefaultAzureCredential()
                self.blob_service_client = BlobServiceClient(account_url=acc_url, credential=credential)  # type: ignore
            elif sas_url:
                logging.info("Initializing BlobServiceClient using SAS URL.")
                self.blob_service_client = BlobServiceClient(account_url=sas_url)
            else:
                raise ValueError(
                    "Could not initialize AzureBlobManager, need at least one of: conn_str, acc_url, or sas_url."
                )
        except Exception as e:
            logging.error(f"Failed to create BlobServiceClient: {e}")
            raise

    def create_container_if_not_exists(self, container_name: str):
        """Creates a container if it does not already exist.

        Args:
            container_name (str): The name of the container.
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                container_name
            )
            if not container_client.exists():
                logging.info(
                    f"Container '{container_name}' does not exist. Creating it."
                )
                container_client.create_container()
                logging.info(f"Container '{container_name}' created successfully.")
        except Exception as e:
            logging.error(f"Failed to create container '{container_name}': {e}")
            raise

    def upload_blob(
        self,
        container_name: str,
        blob_name: str,
        data: Union[bytes, str, Path],
        overwrite: bool = True,
    ):
        """Uploads data to a blob in the specified container.

        Args:
            container_name (str): The name of the container.
            blob_name (str): The name of the blob.
            data (Union[bytes, str, Path]): The data to upload. Can be bytes, a string, or a local file path.
            overwrite (bool): Whether to overwrite the blob if it already exists.
        """
        logging.info(
            f"Uploading to blob '{blob_name}' in container '{container_name}'..."
        )
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )
            if isinstance(data, Path) or isinstance(data, str) and Path(data).exists():
                with open(data, "rb") as f:
                    blob_client.upload_blob(f, overwrite=overwrite)
            elif isinstance(data, (bytes, str)):
                blob_client.upload_blob(data, overwrite=overwrite)
            else:
                raise TypeError("Data must be bytes, a string, or a valid file path.")
            logging.info("Upload successful.")
        except Exception as e:
            logging.error(f"Upload failed: {e}")
            raise

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """Downloads a blob's content as bytes.

        Args:
            container_name (str): The name of the container.
            blob_name (str): The name of the blob.

        Returns:
            bytes: The content of the blob.
        """
        logging.info(
            f"Downloading blob '{blob_name}' from container '{container_name}'..."
        )
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )
            return blob_client.download_blob().readall()
        except ResourceNotFoundError:
            logging.error(
                f"Blob '{blob_name}' not found in container '{container_name}'."
            )
            raise
        except Exception as e:
            logging.error(f"Download failed: {e}")
            raise

    def list_blobs(self, container_name: str, **kwargs) -> list[str]:
        """Lists the names of all blobs in a container.

        Args:
            container_name (str): The name of the container.

        Returns:
            list[str]: A list of blob names.
        """
        logging.info(f"Listing blobs in container '{container_name}'...")
        try:
            container_client = self.blob_service_client.get_container_client(
                container_name
            )
            return [blob.name for blob in container_client.list_blobs(**kwargs)]
        except Exception as e:
            logging.error(f"Failed to list blobs: {e}")
            raise

    def delete_blob(self, container_name: str, blob_name: str):
        """Deletes a blob from the container.

        Args:
            container_name (str): The name of the container.
            blob_name (str): The name of the blob to delete.
        """
        logging.info(
            f"Deleting blob '{blob_name}' from container '{container_name}'..."
        )
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )
            blob_client.delete_blob()
            logging.info("Blob deleted successfully.")
        except ResourceNotFoundError:
            logging.warning(f"Blob '{blob_name}' not found. Nothing to delete.")
        except Exception as e:
            logging.error(f"Failed to delete blob: {e}")
            raise


def get_sas_url(
    account_name: str, account_key: str, container_name: str, blob_name: str
) -> str:
    """Gets a sas URL for the specified account, container and blob."""
    sas_token = get_sas_token(account_name, account_key, container_name)
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"


def get_sas_token(account_name: str, account_key: str, container_name: str) -> str:
    """Gets a sas token for the specified account and container with full permissions."""
    return generate_container_sas(
        account_name=account_name,
        container_name=container_name,
        account_key=account_key,
        permission=ContainerSasPermissions(
            read=True, write=True, list=True, create=True, add=True
        ),
        expiry=datetime.now(timezone.utc) + timedelta(hours=2),
        start=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
