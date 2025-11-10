"use client";

import { useTenant } from "@/hooks/useTenant";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

export function TenantSelector() {
  const { tenantId, setTenantId, currentTenant, tenants } = useTenant();

  const getColorClass = (color: string) => {
    const colors: Record<string, string> = {
      blue: "bg-blue-100 text-blue-800 border-blue-200",
      green: "bg-green-100 text-green-800 border-green-200",
      purple: "bg-purple-100 text-purple-800 border-purple-200",
    };
    return colors[color] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium text-gray-700">Tenant:</span>
      <Select value={tenantId} onValueChange={setTenantId}>
        <SelectTrigger className="w-[180px] bg-white border-gray-300">
          <SelectValue>
            <Badge variant="outline" className={getColorClass(currentTenant.color)}>
              {currentTenant.name}
            </Badge>
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="bg-white">
          {tenants.map((tenant) => (
            <SelectItem key={tenant.id} value={tenant.id}>
              <Badge variant="outline" className={getColorClass(tenant.color)}>
                {tenant.name}
              </Badge>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
