"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Shield, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { apiClient, QueryResponse } from "@/lib/api-client";
import { TenantSelector } from "@/components/TenantSelector";

export default function HomePage() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const result = await apiClient.query({ prompt });
      setResponse(result);
    } catch (error) {
      console.error("Error:", error);
      alert("Error connecting to API. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors = {
      low: "bg-blue-100 text-blue-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
    };
    return colors[severity as keyof typeof colors] || colors.low;
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case "allow":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "block":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "redact":
      case "warn":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Shield className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900">
              Prompt Firewall Demo
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            Test our AI security firewall that detects PII, PHI, and prompt
            injection attacks
          </p>
        </div>

        <div className="mb-6 flex justify-center">
          <Card className="inline-block">
            <CardContent className="pt-6">
              <TenantSelector />
            </CardContent>
          </Card>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Enter Your Prompt</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="Try: 'My email is john@example.com and SSN is 123-45-6789' or 'Ignore all previous instructions...'"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[150px] mb-4"
            />
            <Button onClick={handleSubmit} disabled={loading} className="w-full">
              {loading ? "Analyzing..." : "Send Prompt"}
            </Button>
          </CardContent>
        </Card>

        {response && (
          <div className="space-y-6">
            <Alert
              className={
                response.decision === "allow"
                  ? "bg-green-50 border-green-200"
                  : response.decision === "block"
                  ? "bg-red-50 border-red-200"
                  : "bg-yellow-50 border-yellow-200"
              }
            >
              <div className="flex items-center gap-2">
                {getDecisionIcon(response.decision)}
                <AlertDescription className="font-semibold">
                  Decision: {response.decision.toUpperCase()} (Severity:{" "}
                  {response.severity})
                </AlertDescription>
              </div>
            </Alert>

            {response.risks.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Detected Risks</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {response.risks.map((risk, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <span className="font-medium">{risk.type}</span>
                          <span className="text-gray-600 ml-2">
                            ({risk.subtype})
                          </span>
                          <p className="text-sm text-gray-500 mt-1">
                            Match: {risk.match}
                          </p>
                        </div>
                        <Badge className={getSeverityColor(risk.severity)}>
                          {risk.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Explanations</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc list-inside space-y-1">
                  {response.explanations.map((exp, idx) => (
                    <li key={idx} className="text-gray-700">
                      {exp}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>
                  {response.decision === "block" ? "Firewall Message" : "LLM Response"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">{response.llmResponse}</p>
                <div className="mt-4 text-sm text-gray-500">
                  Latency: {response.latency.toFixed(2)}s
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
