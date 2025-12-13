
from edgedb import create_client,Client




def get_sync_client() -> Client:
    """
    Creates and returns a SYNCHRONOUS client for use in CLI scripts.
    """
    from app.config import settings 
    client: Client | None = None
    try:
        client = create_client(
        user=settings.geldb_user,
        password=settings.geldb_password,
        database=settings.geldb_branch_name,
        port=settings.geldb_port,
        host=settings.geldb_host,
        tls_security=settings.geldb_tls_security,
        tls_ca=settings.geldb_tls_ca_data,
        wait_until_available=300,
        )
        
        client.ensure_connected()
        return client

    except Exception as e:
        print(f"Failed to create sync EdgeDB client: {e}")
        raise