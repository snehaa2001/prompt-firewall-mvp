export interface QueryRequest {
  prompt: string;
  model?: string;
  userId?: string;
  tenantId?: string;
}

export interface Risk {
  type: string;
  subtype: string;
  match: string;
  severity: string;
  position: number;
  confidence?: number;
  pattern?: string;
}

export interface QueryResponse {
  decision: "allow" | "block" | "redact" | "warn";
  originalPrompt: string;
  modifiedPrompt: string;
  llmResponse: string;
  risks: Risk[];
  explanations: string[];
  severity: string;
  latency: number;
  metadata: Record<string, any>;
}

export class PromptFirewallClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('firebase_token');
    }
    return null;
  }

  async query(request: QueryRequest): Promise<QueryResponse> {
    const tenantId = typeof window !== 'undefined'
      ? localStorage.getItem('selected_tenant_id') || 'tenant-a'
      : 'tenant-a';

    const response = await fetch(`${this.baseUrl}/v1/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...request,
        tenantId: request.tenantId || tenantId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getPolicies(): Promise<any[]> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/v1/policy`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') {
        window.location.href = '/admin/login';
      }
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.policies;
  }

  async createPolicy(policyData: any): Promise<{ policyId: string; status: string }> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/v1/policy`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(policyData),
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') {
        window.location.href = '/admin/login';
      }
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async updatePolicy(policyId: string, policyData: any): Promise<{ status: string }> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/v1/policy/${policyId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(policyData),
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') {
        window.location.href = '/admin/login';
      }
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async deletePolicy(policyId: string): Promise<{ status: string }> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/v1/policy/${policyId}`, {
      method: "DELETE",
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') {
        window.location.href = '/admin/login';
      }
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getLogs(params?: {
    limit?: number;
    offset?: number;
    filterType?: string;
  }): Promise<{ logs: any[]; hasMore: boolean }> {
    const token = this.getAuthToken();
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(`${this.baseUrl}/v1/logs?${queryParams}`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') {
        window.location.href = '/admin/login';
      }
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getPolicyHistory(policyId: string): Promise<any[]> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/v1/policy/${policyId}/history`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') {
        window.location.href = '/admin/login';
      }
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.history;
  }

  async rollbackPolicy(policyId: string, version: number): Promise<void> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/v1/policy/${policyId}/rollback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify({ version }),
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') {
        window.location.href = '/admin/login';
      }
      throw new Error(`API error: ${response.statusText}`);
    }
  }

  async getTenants(): Promise<any[]> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/v1/tenants`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.tenants;
  }
}

export const apiClient = new PromptFirewallClient();
