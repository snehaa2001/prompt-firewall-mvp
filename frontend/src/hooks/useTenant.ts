import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";

export interface Tenant {
  id: string;
  name: string;
  color: string;
}

export const DEMO_TENANTS: Tenant[] = [
  { id: "tenant-a", name: "Tenant A", color: "blue" },
  { id: "tenant-b", name: "Tenant B", color: "green" },
  { id: "tenant-c", name: "Tenant C", color: "purple" },
];

const TENANT_STORAGE_KEY = "selected_tenant_id";

export function useTenant() {
  const [tenantId, setTenantIdState] = useState<string>("tenant-a");
  const [tenants, setTenants] = useState<Tenant[]>(DEMO_TENANTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTenants = async () => {
      try {
        const fetchedTenants = await apiClient.getTenants();
        if (fetchedTenants && fetchedTenants.length > 0) {
          setTenants(fetchedTenants);
        }
      } catch (error) {
        console.error("Failed to fetch tenants, using defaults:", error);
      } finally {
        setLoading(false);
      }
    };

    loadTenants();

    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(TENANT_STORAGE_KEY);
      if (stored) {
        setTenantIdState(stored);
      }
    }
  }, []);

  const setTenantId = (id: string) => {
    setTenantIdState(id);
    if (typeof window !== "undefined") {
      localStorage.setItem(TENANT_STORAGE_KEY, id);
    }
  };

  const currentTenant = tenants.find((t) => t.id === tenantId) || tenants[0];

  return {
    tenantId,
    setTenantId,
    currentTenant,
    tenants,
    loading,
  };
}
