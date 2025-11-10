"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Pencil, Trash2, RefreshCw, History, RotateCcw } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface Policy {
  id: string;
  name: string;
  type: string;
  pattern: string;
  action: string;
  severity: string;
  enabled: boolean;
  version?: number;
  updatedAt?: any;
  updatedBy?: string;
  createdAt?: any;
  createdBy?: string;
}

interface HistoryEntry {
  version: number;
  data: any;
  updatedAt: any;
  updatedBy: string;
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<Policy | null>(null);
  const [isHistoryDialogOpen, setIsHistoryDialogOpen] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    type: "pii",
    pattern: "",
    action: "block",
    severity: "high",
    enabled: true,
  });

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiClient.getPolicies();
      setPolicies(data);
    } catch (err: any) {
      setError(err.message || "Failed to load policies");
    } finally {
      setLoading(false);
    }
  };

  const openCreateDialog = () => {
    setEditingPolicy(null);
    setFormData({
      name: "",
      type: "pii",
      pattern: "",
      action: "block",
      severity: "high",
      enabled: true,
    });
    setIsDialogOpen(true);
  };

  const openEditDialog = (policy: Policy) => {
    setEditingPolicy(policy);
    setFormData({
      name: policy.name,
      type: policy.type,
      pattern: policy.pattern,
      action: policy.action,
      severity: policy.severity,
      enabled: policy.enabled,
    });
    setIsDialogOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingPolicy) {
        await apiClient.updatePolicy(editingPolicy.id, formData);
      } else {
        await apiClient.createPolicy(formData);
      }
      setIsDialogOpen(false);
      await loadPolicies();
    } catch (err: any) {
      setError(err.message || "Failed to save policy");
    }
  };

  const handleDelete = async (policyId: string) => {
    if (!confirm("Are you sure you want to delete this policy?")) return;

    try {
      await apiClient.deletePolicy(policyId);
      await loadPolicies();
    } catch (err: any) {
      setError(err.message || "Failed to delete policy");
    }
  };

  const formatTimestamp = (timestamp: any) => {
    if (!timestamp) return "N/A";
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const handleViewHistory = async (policy: Policy) => {
    setSelectedPolicy(policy);
    setIsHistoryDialogOpen(true);
    setLoadingHistory(true);
    setError("");

    try {
      const historyData = await apiClient.getPolicyHistory(policy.id);
      setHistory(historyData);
    } catch (err: any) {
      setError(err.message || "Failed to load policy history");
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleRollback = async (version: number) => {
    if (!selectedPolicy) return;
    if (!confirm(`Are you sure you want to rollback to version ${version}?`)) return;

    try {
      await apiClient.rollbackPolicy(selectedPolicy.id, version);
      setIsHistoryDialogOpen(false);
      await loadPolicies();
    } catch (err: any) {
      setError(err.message || "Failed to rollback policy");
    }
  };

  const getChangedFields = (oldData: any, newData: any): string[] => {
    const changed: string[] = [];
    const fields = ['name', 'type', 'pattern', 'action', 'severity', 'enabled'];

    fields.forEach(field => {
      if (oldData[field] !== newData[field]) {
        changed.push(field);
      }
    });

    return changed;
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      pii: "bg-blue-100 text-blue-800",
      injection: "bg-purple-100 text-purple-800",
      custom: "bg-gray-100 text-gray-800",
    };
    return colors[type] || "bg-gray-100 text-gray-800";
  };

  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      block: "bg-red-100 text-red-800",
      redact: "bg-yellow-100 text-yellow-800",
      warn: "bg-orange-100 text-orange-800",
    };
    return colors[action] || "bg-gray-100 text-gray-800";
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      low: "bg-blue-100 text-blue-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
    };
    return colors[severity] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Policy Management</h1>
          <p className="text-gray-600 mt-1">
            Configure firewall rules and security policies
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadPolicies} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button onClick={openCreateDialog}>
            <Plus className="w-4 h-4 mr-2" />
            New Policy
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Active Policies</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 text-center text-gray-600">Loading policies...</div>
          ) : policies.length === 0 ? (
            <div className="p-8 text-center text-gray-600">
              No policies found. Create your first policy to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Pattern</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {policies.map((policy) => (
                  <TableRow key={policy.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        {policy.name}
                        {policy.version && (
                          <Badge variant="outline" className="text-xs">
                            v{policy.version}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getTypeColor(policy.type)}>{policy.type}</Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {policy.pattern}
                      </code>
                    </TableCell>
                    <TableCell>
                      <Badge className={getActionColor(policy.action)}>
                        {policy.action}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getSeverityColor(policy.severity)}>
                        {policy.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={policy.enabled ? "default" : "secondary"}>
                        {policy.enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleViewHistory(policy)}
                              >
                                <History className="w-4 h-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>View History</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openEditDialog(policy)}
                        >
                          <Pencil className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(policy.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[550px] bg-white">
          <DialogHeader className="pb-4 border-b">
            <DialogTitle className="text-xl">
              {editingPolicy ? "Edit Policy" : "Create New Policy"}
            </DialogTitle>
            <DialogDescription className="text-sm mt-1.5">
              {editingPolicy
                ? "Update the policy configuration below."
                : "Configure a new security policy for the firewall."}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-5 py-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-sm font-medium text-gray-900">
                Name
              </Label>
              <Input
                id="name"
                placeholder="e.g., Block SSN Numbers"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="h-10 bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="type" className="text-sm font-medium text-gray-900">
                Type
              </Label>
              <Select
                value={formData.type}
                onValueChange={(value) => setFormData({ ...formData, type: value })}
              >
                <SelectTrigger className="h-10 bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="pii">PII Detection</SelectItem>
                  <SelectItem value="injection">Prompt Injection</SelectItem>
                  <SelectItem value="custom">Custom Rule</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="pattern" className="text-sm font-medium text-gray-900">
                Pattern
              </Label>
              <Input
                id="pattern"
                placeholder="e.g., ssn, email, or custom regex"
                value={formData.pattern}
                onChange={(e) => setFormData({ ...formData, pattern: e.target.value })}
                className="h-10 bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 font-mono text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter a pattern identifier or regex pattern
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="action" className="text-sm font-medium text-gray-900">
                  Action
                </Label>
                <Select
                  value={formData.action}
                  onValueChange={(value) =>
                    setFormData({ ...formData, action: value })
                  }
                >
                  <SelectTrigger className="h-10 bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="block">Block</SelectItem>
                    <SelectItem value="redact">Redact</SelectItem>
                    <SelectItem value="warn">Warn</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="severity" className="text-sm font-medium text-gray-900">
                  Severity
                </Label>
                <Select
                  value={formData.severity}
                  onValueChange={(value) =>
                    setFormData({ ...formData, severity: value })
                  }
                >
                  <SelectTrigger className="h-10 bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-start space-x-3 pt-2">
              <input
                type="checkbox"
                id="enabled"
                checked={formData.enabled}
                onChange={(e) =>
                  setFormData({ ...formData, enabled: e.target.checked })
                }
                className="w-4 h-4 mt-0.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
              <div className="flex flex-col">
                <Label htmlFor="enabled" className="text-sm font-medium text-gray-900 cursor-pointer">
                  Enable this policy
                </Label>
                <p className="text-xs text-gray-500 mt-0.5">
                  Active policies will be enforced immediately
                </p>
              </div>
            </div>
          </div>

          <DialogFooter className="pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => setIsDialogOpen(false)}
              className="h-10 px-6"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              className="h-10 px-6 bg-blue-600 hover:bg-blue-700"
            >
              {editingPolicy ? "Update Policy" : "Create Policy"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isHistoryDialogOpen} onOpenChange={setIsHistoryDialogOpen}>
        <DialogContent className="sm:max-w-[700px] bg-white max-h-[80vh]">
          <DialogHeader className="pb-4 border-b">
            <DialogTitle className="text-xl">Policy Version History</DialogTitle>
            <DialogDescription className="text-sm mt-1.5">
              {selectedPolicy && (
                <span>
                  {selectedPolicy.name} - Current Version: v{selectedPolicy.version || 1}
                </span>
              )}
            </DialogDescription>
          </DialogHeader>

          <ScrollArea className="h-[500px] pr-4">
            {loadingHistory ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-gray-400" />
              </div>
            ) : history.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No version history available
              </div>
            ) : (
              <div className="space-y-6">
                {selectedPolicy && (
                  <div className="border rounded-lg p-4 bg-blue-50 border-blue-200">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className="bg-blue-600 text-white">
                            Current: v{selectedPolicy.version || 1}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600">
                          Updated by {selectedPolicy.updatedBy || "admin"} on{" "}
                          {formatTimestamp(selectedPolicy.updatedAt)}
                        </p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Type:</span>{" "}
                        <Badge className={getTypeColor(selectedPolicy.type)}>
                          {selectedPolicy.type}
                        </Badge>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Action:</span>{" "}
                        <Badge className={getActionColor(selectedPolicy.action)}>
                          {selectedPolicy.action}
                        </Badge>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Severity:</span>{" "}
                        <Badge className={getSeverityColor(selectedPolicy.severity)}>
                          {selectedPolicy.severity}
                        </Badge>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Status:</span>{" "}
                        <Badge variant={selectedPolicy.enabled ? "default" : "secondary"}>
                          {selectedPolicy.enabled ? "Enabled" : "Disabled"}
                        </Badge>
                      </div>
                      <div className="col-span-2">
                        <span className="font-medium text-gray-700">Pattern:</span>{" "}
                        <code className="text-xs bg-white px-2 py-1 rounded border">
                          {selectedPolicy.pattern}
                        </code>
                      </div>
                    </div>
                  </div>
                )}

                {history.map((entry, index) => {
                  const nextEntry = index === 0 ? selectedPolicy : history[index - 1]?.data;
                  const changedFields = nextEntry ? getChangedFields(entry.data, nextEntry) : [];

                  return (
                    <div key={entry.version}>
                      <div className="relative pl-8 pb-6">
                        <div className="absolute left-0 top-2 w-3 h-3 rounded-full bg-gray-300 border-2 border-white" />
                        {index < history.length - 1 && (
                          <div className="absolute left-1.5 top-5 w-0.5 h-full bg-gray-200" />
                        )}

                        <div className="border rounded-lg p-4 bg-white">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <Badge variant="outline">v{entry.version}</Badge>
                                {changedFields.length > 0 && (
                                  <span className="text-xs text-gray-500">
                                    Changed: {changedFields.join(", ")}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-gray-600">
                                Updated by {entry.updatedBy} on {formatTimestamp(entry.updatedAt)}
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleRollback(entry.version)}
                              className="flex items-center gap-1"
                            >
                              <RotateCcw className="w-3 h-3" />
                              Rollback
                            </Button>
                          </div>

                          <div className="grid grid-cols-2 gap-3 text-sm">
                            <div>
                              <span className="font-medium text-gray-700">Type:</span>{" "}
                              <Badge className={getTypeColor(entry.data.type)}>
                                {entry.data.type}
                              </Badge>
                            </div>
                            <div>
                              <span className="font-medium text-gray-700">Action:</span>{" "}
                              <Badge className={getActionColor(entry.data.action)}>
                                {entry.data.action}
                              </Badge>
                            </div>
                            <div>
                              <span className="font-medium text-gray-700">Severity:</span>{" "}
                              <Badge className={getSeverityColor(entry.data.severity)}>
                                {entry.data.severity}
                              </Badge>
                            </div>
                            <div>
                              <span className="font-medium text-gray-700">Status:</span>{" "}
                              <Badge variant={entry.data.enabled ? "default" : "secondary"}>
                                {entry.data.enabled ? "Enabled" : "Disabled"}
                              </Badge>
                            </div>
                            <div className="col-span-2">
                              <span className="font-medium text-gray-700">Pattern:</span>{" "}
                              <code className="text-xs bg-gray-50 px-2 py-1 rounded border">
                                {entry.data.pattern}
                              </code>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </ScrollArea>

          <DialogFooter className="pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => setIsHistoryDialogOpen(false)}
              className="h-10 px-6"
            >
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
