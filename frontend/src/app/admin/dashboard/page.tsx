"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Shield, AlertTriangle, Activity, XCircle, RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api-client";

interface Stats {
  totalRequests: number;
  blockedCount: number;
  piiDetected: number;
  injectionAttempts: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats>({
    totalRequests: 0,
    blockedCount: 0,
    piiDetected: 0,
    injectionAttempts: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiClient.getLogs({ limit: 500 });
      const logs = data.logs;

      const blocked = logs.filter((l) => l.decision === "block").length;
      const pii = logs.filter((l) =>
        l.risks?.some((r: any) => r.type === "PII")
      ).length;
      const injection = logs.filter((l) =>
        l.risks?.some((r: any) => r.type === "PROMPT_INJECTION")
      ).length;

      setStats({
        totalRequests: logs.length,
        blockedCount: blocked,
        piiDetected: pii,
        injectionAttempts: injection,
      });
    } catch (err: any) {
      setError(err.message || "Failed to load statistics");
    } finally {
      setLoading(false);
    }
  };

  const blockedPercentage =
    stats.totalRequests > 0
      ? ((stats.blockedCount / stats.totalRequests) * 100).toFixed(1)
      : "0.0";

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Overview of firewall activity and security metrics
          </p>
        </div>
        <Button onClick={loadStats} disabled={loading} variant="outline">
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Requests
            </CardTitle>
            <Activity className="w-4 h-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {stats.totalRequests.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500 mt-1">All processed requests</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Blocked Requests
            </CardTitle>
            <XCircle className="w-4 h-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {stats.blockedCount.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {blockedPercentage}% of total requests
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              PII Detected
            </CardTitle>
            <Shield className="w-4 h-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {stats.piiDetected.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500 mt-1">Sensitive data found</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Injection Attempts
            </CardTitle>
            <AlertTriangle className="w-4 h-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {stats.injectionAttempts.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500 mt-1">Attack patterns detected</p>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">System Status</p>
                    <p className="text-sm text-gray-600">
                      Firewall is active and monitoring requests
                    </p>
                  </div>
                </div>
                <span className="text-green-600 font-semibold">Active</span>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="font-medium text-gray-900">Detection Rate</p>
                    <p className="text-sm text-gray-600">
                      {stats.totalRequests > 0
                        ? `${(
                            ((stats.piiDetected + stats.injectionAttempts) /
                              stats.totalRequests) *
                            100
                          ).toFixed(1)}%`
                        : "0%"}{" "}
                      of requests flagged
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
