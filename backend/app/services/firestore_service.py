import firebase_admin
from firebase_admin import firestore
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class FirestoreService:
    def __init__(self):
        if not firebase_admin._apps:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

            if project_id:
                firebase_admin.initialize_app(
                    options={
                        "projectId": project_id,
                    }
                )

        try:
            self.db = firestore.Client()
        except Exception as e:
            print(f"Warning: Could not initialize Firestore client: {e}")
            self.db = None

    async def redact_pii_for_logging(self, text: str) -> str:
        if not text:
            return text

        from app.core.pii_detector import PIIDetector

        pii_detector = PIIDetector()

        results = await pii_detector.detect(text)

        redacted_text = text
        for risk in results:
            if "original_match" in risk:
                entity_type = risk["subtype"].upper()
                redacted_text = redacted_text.replace(risk["original_match"], f"[REDACTED_{entity_type}]")

        return redacted_text

    async def log_request(
        self,
        prompt: str,
        response: str,
        decision: dict,
        latency: float,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        if not self.db:
            return "firestore_not_configured"

        safe_prompt = await self.redact_pii_for_logging(prompt[:100])
        safe_response = await self.redact_pii_for_logging(response[:100])

        _, doc_ref = self.db.collection("logs").add(
            {
                "timestamp": datetime.utcnow(),
                "tenantId": tenant_id or "default",
                "prompt_preview": safe_prompt,
                "response_preview": safe_response,
                "decision": decision.get("decision", "unknown"),
                "risks": decision.get("risks", []),
                "severity": decision.get("severity", "low"),
                "latency": latency,
                "userId": user_id,
                "metadata": decision.get("metadata", {}),
            }
        )
        return doc_ref.id

    async def get_logs(
        self, limit: int = 50, offset: int = 0, filter_type: str = "all", tenant_id: Optional[str] = None
    ) -> Dict:
        if not self.db:
            return {"logs": [], "total": 0}

        base_query = self.db.collection("logs")

        if tenant_id:
            base_query = base_query.where("tenantId", "==", tenant_id)

        if filter_type != "all":
            base_query = base_query.where("decision", "==", filter_type)

        base_query = base_query.order_by("timestamp", direction=firestore.Query.DESCENDING)

        query = base_query.limit(limit)
        docs = list(query.stream())

        logs = [{"id": doc.id, **doc.to_dict()} for doc in docs]

        return {"logs": logs, "total": len(logs)}

    async def get_active_policies(self) -> List[Dict]:
        if not self.db:
            return []

        docs = self.db.collection("policies").where("enabled", "==", True).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    async def get_all_policies(self) -> List[Dict]:
        if not self.db:
            return []

        docs = self.db.collection("policies").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    async def create_policy(self, policy_data: dict) -> str:
        if not self.db:
            return "firestore_not_configured"

        policy_data.update(
            {"version": 1, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow(), "createdBy": "admin", "history": []}
        )
        _, doc_ref = self.db.collection("policies").add(policy_data)
        return doc_ref.id

    async def update_policy(self, policy_id: str, updates: dict, updated_by: str = "admin") -> None:
        if not self.db:
            return

        doc_ref = self.db.collection("policies").document(policy_id)
        current = doc_ref.get()

        if not current.exists:
            raise ValueError(f"Policy {policy_id} not found")

        current_data = current.to_dict()

        history_entry = {
            "version": current_data["version"],
            "data": current_data,
            "updatedAt": current_data["updatedAt"],
            "updatedBy": current_data.get("createdBy", "unknown"),
        }

        new_version = current_data["version"] + 1
        updates.update({"version": new_version, "updatedAt": datetime.utcnow(), "updatedBy": updated_by})

        doc_ref.update({**updates, "history": firestore.ArrayUnion([history_entry])})

    async def delete_policy(self, policy_id: str) -> None:
        if not self.db:
            return

        doc_ref = self.db.collection("policies").document(policy_id)
        doc_ref.delete()

    async def get_policy_history(self, policy_id: str) -> list:
        if not self.db:
            return []

        doc = self.db.collection("policies").document(policy_id).get()
        if not doc.exists:
            raise ValueError(f"Policy {policy_id} not found")

        return doc.to_dict().get("history", [])

    async def rollback_policy(self, policy_id: str, target_version: int) -> None:
        if not self.db:
            return

        doc_ref = self.db.collection("policies").document(policy_id)
        current = doc_ref.get()

        if not current.exists:
            raise ValueError(f"Policy {policy_id} not found")

        current_data = current.to_dict()
        history = current_data.get("history", [])

        target_data = None
        for entry in history:
            if entry["version"] == target_version:
                target_data = entry["data"].copy()
                break

        if not target_data:
            raise ValueError(f"Version {target_version} not found")

        history_entry = {
            "version": current_data["version"],
            "data": {k: v for k, v in current_data.items() if k != "history"},
            "updatedAt": current_data["updatedAt"],
            "updatedBy": current_data.get("updatedBy", "unknown"),
        }

        policy_fields = ["name", "type", "pattern", "action", "severity", "enabled"]
        clean_target_data = {k: v for k, v in target_data.items() if k in policy_fields}

        clean_target_data.update(
            {"version": current_data["version"] + 1, "updatedAt": datetime.utcnow(), "updatedBy": "system_rollback"}
        )

        doc_ref.update({**clean_target_data, "history": firestore.ArrayUnion([history_entry])})

    async def cleanup_old_logs(self, retention_days: int = 90) -> int:
        if not self.db:
            return 0

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        old_logs = self.db.collection("logs").where("timestamp", "<", cutoff_date).stream()

        batch = self.db.batch()
        count = 0

        for doc in old_logs:
            batch.delete(doc.reference)
            count += 1

            if count % 500 == 0:
                batch.commit()
                batch = self.db.batch()

        if count % 500 != 0:
            batch.commit()

        return count

    async def get_all_tenants(self) -> List[Dict]:
        if not self.db:
            return []

        docs = self.db.collection("tenants").where("enabled", "==", True).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    async def create_tenant(self, tenant_data: dict) -> str:
        if not self.db:
            return "firestore_not_configured"

        doc_ref = self.db.collection("tenants").document(tenant_data["id"])
        tenant_data.update({"createdAt": datetime.utcnow(), "enabled": True})
        doc_ref.set(tenant_data)
        return doc_ref.id

    async def get_policies_by_tenant(self, tenant_id: str) -> List[Dict]:
        if not self.db:
            return []

        docs = self.db.collection("policies").where("tenantId", "==", tenant_id).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    async def get_active_policies_by_tenant(self, tenant_id: str) -> List[Dict]:
        if not self.db:
            return []

        docs = self.db.collection("policies").where("tenantId", "==", tenant_id).where("enabled", "==", True).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    async def verify_policy_tenant(self, policy_id: str, tenant_id: str) -> bool:
        if not self.db:
            return False

        doc = self.db.collection("policies").document(policy_id).get()
        if not doc.exists:
            return False

        policy_data = doc.to_dict()
        return policy_data.get("tenantId") == tenant_id
