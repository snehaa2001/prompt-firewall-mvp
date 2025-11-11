from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv
from google.cloud import error_reporting
from app.core.firewall import PromptFirewall
from app.core.anomaly_detector import AnomalyDetector
from app.services.llm_service import LLMService
from app.services.firestore_service import FirestoreService
from app.services.firebase_auth_service import verify_firebase_token, require_admin, create_admin_user
from app.models.requests import QueryRequest, PolicyRequest
from app.models.responses import QueryResponse
from pydantic import BaseModel
from app.core.logging_config import logger, set_request_id
from firebase_admin import auth as firebase_auth

load_dotenv()

error_client = error_reporting.Client()

app = FastAPI(title="Prompt Firewall API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins_list = allowed_origins_env.split(",") if allowed_origins_env else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://prompt-firewall-frontend-390735445343.us-central1.run.app",
        *allowed_origins_list,
    ],
    allow_origin_regex=r"https://prompt-firewall-frontend.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = set_request_id()
    request.state.request_id = request_id

    start_time = time.time()

    logger.info("request_started", method=request.method, url=str(request.url), client_ip=request.client.host)

    response = await call_next(request)

    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "request_completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        latency_ms=latency_ms,
    )

    response.headers["X-Request-ID"] = request_id

    return response


firewall = PromptFirewall()
llm_service = LLMService()
db_service = FirestoreService()
anomaly_detector = AnomalyDetector()


class AdminCreationRequest(BaseModel):
    email: str
    password: str
    admin_secret: str


@app.post("/v1/admin/create-admin-user")
async def create_first_admin(request: AdminCreationRequest):
    admin_secret = os.getenv("ADMIN_CREATION_SECRET", "")
    if request.admin_secret != admin_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")

    try:
        uid = await create_admin_user(request.email, request.password)
        return {"uid": uid, "message": "Admin user created"}
    except Exception:
        error_client.report_exception()
        raise HTTPException(status_code=500, detail="Failed to create admin user")


class GrantAdminRequest(BaseModel):
    tenantId: str = "tenant-a"


@app.post("/v1/admin/grant-self-admin")
async def grant_self_admin(request: GrantAdminRequest, user: dict = Depends(verify_firebase_token)):
    try:
        firebase_auth.set_custom_user_claims(user["uid"], {"role": "admin", "tenantId": request.tenantId})
        return {
            "message": "Admin role and tenant assigned. Please refresh your token.",
            "uid": user["uid"],
            "tenantId": request.tenantId,
        }
    except Exception:
        error_client.report_exception()
        raise HTTPException(status_code=500, detail="Failed to grant admin role")


@app.post("/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    start_time = time.time()

    logger.info("firewall_analysis_started", prompt_length=len(request.prompt), model=request.model, user_id=request.userId)

    try:
        tenant_id = request.tenantId or "default"
        policies = await db_service.get_active_policies_by_tenant(tenant_id)

        prompt_decision = await firewall.analyze_request(prompt=request.prompt, policies=policies)

        if prompt_decision.decision == "block":
            await db_service.log_request(
                prompt=request.prompt,
                response="[BLOCKED]",
                decision=prompt_decision.model_dump(),
                latency=time.time() - start_time,
                user_id=request.userId,
                tenant_id=tenant_id,
            )

            return QueryResponse(
                decision="block",
                originalPrompt=request.prompt,
                modifiedPrompt=prompt_decision.promptModified,
                llmResponse=prompt_decision.responseModified,
                risks=prompt_decision.risks,
                explanations=prompt_decision.explanations,
                severity=prompt_decision.severity,
                latency=time.time() - start_time,
                metadata=prompt_decision.metadata,
            )

        prompt_to_send = prompt_decision.promptModified if prompt_decision.decision == "redact" else request.prompt

        model = request.model or "gpt-3.5-turbo"
        llm_response = await llm_service.generate_response(prompt=prompt_to_send, model=model)

        response_decision = await firewall.analyze_request(prompt=request.prompt, response=llm_response, policies=policies)

        final_response = (
            response_decision.responseModified if response_decision.decision in ["block", "redact"] else llm_response
        )

        latency = time.time() - start_time

        risk_score = await anomaly_detector.calculate_risk_score(
            user_id=request.userId or "anonymous",
            tenant_id=tenant_id,
            current_decision=response_decision.model_dump(),
        )

        logger.info(
            "firewall_decision",
            decision=response_decision.decision,
            severity=response_decision.severity,
            risk_count=len(response_decision.risks),
            risk_score=risk_score,
            latency_seconds=round(latency, 3),
            pii_count=response_decision.metadata.get("pii_count", 0),
            injection_count=response_decision.metadata.get("injection_count", 0),
        )

        await db_service.log_request(
            prompt=request.prompt,
            response=final_response,
            decision=response_decision.model_dump(),
            latency=latency,
            user_id=request.userId,
            tenant_id=tenant_id,
        )

        response_decision.metadata["risk_score"] = risk_score

        return QueryResponse(
            decision=response_decision.decision,
            originalPrompt=request.prompt,
            modifiedPrompt=prompt_decision.promptModified,
            llmResponse=final_response,
            risks=response_decision.risks,
            explanations=response_decision.explanations,
            severity=response_decision.severity,
            latency=latency,
            metadata=response_decision.metadata,
        )

    except Exception as e:
        logger.error("firewall_error", error=str(e), error_type=type(e).__name__, exc_info=True)
        error_client.report_exception()
        raise HTTPException(status_code=500, detail="Firewall analysis failed")


@app.get("/v1/policy")
async def get_policies(user: dict = Depends(require_admin)):
    tenant_id = user.get("tenantId", "default")
    policies = await db_service.get_policies_by_tenant(tenant_id)
    return {"policies": policies}


@app.post("/v1/policy")
async def create_policy(policy: PolicyRequest, user: dict = Depends(require_admin)):
    policy_data = policy.model_dump()
    policy_data["tenantId"] = user.get("tenantId", "default")
    policy_id = await db_service.create_policy(policy_data)
    return {"policyId": policy_id, "status": "created"}


@app.put("/v1/policy/{policy_id}")
async def update_policy(policy_id: str, policy: PolicyRequest, user: dict = Depends(require_admin)):
    tenant_id = user.get("tenantId", "default")
    if not await db_service.verify_policy_tenant(policy_id, tenant_id):
        raise HTTPException(status_code=403, detail="Access denied to this policy")

    await db_service.update_policy(policy_id, policy.model_dump(), updated_by=user.get("email", "unknown"))
    return {"status": "updated"}


@app.delete("/v1/policy/{policy_id}")
async def delete_policy(policy_id: str, user: dict = Depends(require_admin)):
    tenant_id = user.get("tenantId", "default")
    if not await db_service.verify_policy_tenant(policy_id, tenant_id):
        raise HTTPException(status_code=403, detail="Access denied to this policy")

    await db_service.delete_policy(policy_id)
    return {"status": "deleted"}


@app.get("/v1/policy/{policy_id}/history")
async def get_policy_history(policy_id: str, user: dict = Depends(require_admin)):
    try:
        tenant_id = user.get("tenantId", "default")
        if not await db_service.verify_policy_tenant(policy_id, tenant_id):
            raise HTTPException(status_code=403, detail="Access denied to this policy")

        history = await db_service.get_policy_history(policy_id)
        return {"history": history}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class RollbackRequest(BaseModel):
    version: int


@app.post("/v1/policy/{policy_id}/rollback")
async def rollback_policy(policy_id: str, request: RollbackRequest, user: dict = Depends(require_admin)):
    try:
        tenant_id = user.get("tenantId", "default")
        if not await db_service.verify_policy_tenant(policy_id, tenant_id):
            raise HTTPException(status_code=403, detail="Access denied to this policy")

        await db_service.rollback_policy(policy_id, request.version)
        return {"status": "rolled_back", "version": request.version}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/v1/logs")
async def get_logs(limit: int = 50, offset: int = 0, filterType: str = "all", user: dict = Depends(require_admin)):
    tenant_id = user.get("tenantId", "default")
    result = await db_service.get_logs(limit=limit, offset=offset, filter_type=filterType, tenant_id=tenant_id)
    return result


@app.post("/admin/cleanup-logs")
async def cleanup_logs(retention_days: int = 90, user: dict = Depends(require_admin)):
    count = await db_service.cleanup_old_logs(retention_days)
    return {"deleted_count": count, "retention_days": retention_days}


@app.get("/v1/tenants")
async def get_tenants():
    tenants = await db_service.get_all_tenants()
    return {"tenants": tenants}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "prompt-firewall"}
