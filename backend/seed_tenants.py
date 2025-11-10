import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.services.firestore_service import FirestoreService

async def seed_tenants():
    db_service = FirestoreService()

    tenants = [
        {
            "id": "tenant-a",
            "name": "Tenant A",
            "color": "blue",
            "settings": {
                "max_requests_per_day": 10000,
                "data_retention_days": 90
            }
        },
        {
            "id": "tenant-b",
            "name": "Tenant B",
            "color": "green",
            "settings": {
                "max_requests_per_day": 10000,
                "data_retention_days": 90
            }
        },
        {
            "id": "tenant-c",
            "name": "Tenant C",
            "color": "purple",
            "settings": {
                "max_requests_per_day": 10000,
                "data_retention_days": 90
            }
        }
    ]

    for tenant in tenants:
        try:
            tenant_id = await db_service.create_tenant(tenant)
            print(f"Created tenant: {tenant['name']} (ID: {tenant_id})")
        except Exception as e:
            print(f"Error creating tenant {tenant['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(seed_tenants())
