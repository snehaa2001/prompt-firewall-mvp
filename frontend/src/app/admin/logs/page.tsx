"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2 } from "lucide-react";

interface LogEntry {
  id: string;
  timestamp: any;
  prompt_preview: string;
  response_preview: string;
  decision: string;
  risks: any[];
  severity: string;
  latency: number;
  tenantId?: string;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [hasMore, setHasMore] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const limit = 50;

  const loadLogs = useCallback(async (isInitialLoad = false) => {
    if (isLoadingMore) return;

    if (isInitialLoad) {
      setLoading(true);
      setOffset(0);
    } else {
      setIsLoadingMore(true);
    }

    setError("");

    try {
      const currentOffset = isInitialLoad ? 0 : offset;
      const data = await apiClient.getLogs({
        limit,
        offset: currentOffset,
        filterType
      });

      if (isInitialLoad) {
        setLogs(data.logs);
        setOffset(limit);
      } else {
        setLogs(prev => [...prev, ...data.logs]);
        setOffset(prev => prev + limit);
      }

      setHasMore(data.hasMore);
    } catch (err: any) {
      setError(err.message || "Failed to load logs");
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  }, [filterType, limit, offset, isLoadingMore]);

  useEffect(() => {
    loadLogs(true);
  }, [loadLogs]);

  useEffect(() => {
    const currentRef = loadMoreRef.current;
    if (!currentRef) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoadingMore && !loading) {
          loadLogs(false);
        }
      },
      { threshold: 1.0 }
    );

    observer.observe(currentRef);

    return () => {
      observer.unobserve(currentRef);
    };
  }, [hasMore, isLoadingMore, loading, loadLogs]);

  const getDecisionColor = (decision: string) => {
    const colors: Record<string, string> = {
      allow: "bg-green-100 text-green-800",
      block: "bg-red-100 text-red-800",
      redact: "bg-yellow-100 text-yellow-800",
      warn: "bg-orange-100 text-orange-800",
    };
    return colors[decision] || "bg-gray-100 text-gray-800";
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

  const formatTimestamp = (timestamp: any) => {
    if (!timestamp) return "N/A";
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(date);
  };

  const truncateText = (text: string, maxLength: number) => {
    if (!text) return "N/A";
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
  };

  return (
    <div className="p-8 h-screen flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Request Logs</h1>
          <p className="text-gray-600 mt-1">View and filter firewall request history</p>
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Filter Logs</CardTitle>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by decision" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Requests</SelectItem>
                <SelectItem value="block">Blocked Only</SelectItem>
                <SelectItem value="redact">Redacted Only</SelectItem>
                <SelectItem value="warn">Warnings Only</SelectItem>
                <SelectItem value="allow">Allowed Only</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
      </Card>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <Card className="flex-1 overflow-hidden flex flex-col">
        <CardContent className="p-0 flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-full text-gray-600">
              <Loader2 className="w-6 h-6 animate-spin mr-2" />
              Loading logs...
            </div>
          ) : logs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-600">
              No logs found
            </div>
          ) : (
            <div className="space-y-2 p-4">
              {logs.map((log, index) => (
                <div
                  key={log.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  style={{
                    animationDelay: `${(index % 50) * 20}ms`,
                    animation: "slideInUp 0.3s ease-out forwards",
                  }}
                >
                  <div className="grid grid-cols-12 gap-4 items-center">
                    <div className="col-span-2">
                      <span className="text-sm text-gray-600">
                        {formatTimestamp(log.timestamp)}
                      </span>
                    </div>
                    <div className="col-span-4">
                      <span className="text-sm text-gray-900">
                        {truncateText(log.prompt_preview, 80)}
                      </span>
                    </div>
                    <div className="col-span-1">
                      <Badge variant="outline" className="text-xs">
                        {log.tenantId || 'default'}
                      </Badge>
                    </div>
                    <div className="col-span-2">
                      <Badge className={getDecisionColor(log.decision)}>
                        {log.decision}
                      </Badge>
                    </div>
                    <div className="col-span-1 text-center">
                      <span className="text-sm font-medium text-gray-700">
                        {log.risks?.length || 0} risks
                      </span>
                    </div>
                    <div className="col-span-1">
                      <Badge className={getSeverityColor(log.severity)}>
                        {log.severity}
                      </Badge>
                    </div>
                    <div className="col-span-1 text-right">
                      <span className="text-sm text-gray-600">
                        {log.latency ? `${log.latency.toFixed(2)}s` : "N/A"}
                      </span>
                    </div>
                  </div>
                </div>
              ))}

              {hasMore && (
                <div ref={loadMoreRef} className="flex justify-center items-center p-6">
                  {isLoadingMore && (
                    <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                  )}
                </div>
              )}

              {!hasMore && logs.length > 0 && (
                <div className="text-center p-4 text-gray-500 text-sm">
                  No more logs to load
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <style jsx>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
