# Custom Policies for Prompt Firewall

```json
[
  {
    "id": "custom_001",
    "name": "SQL Injection Detection",
    "description": "Detects potential SQL injection attempts in prompts",
    "pattern": "(?i)(union\\s+select|drop\\s+table|insert\\s+into|delete\\s+from|exec\\s*\\(|execute\\s+immediate|;\\s*--|'\\s+or\\s+'1'\\s*=\\s*'1)",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_002",
    "name": "Command Injection Detection",
    "description": "Detects shell command injection patterns",
    "pattern": "(?i)(;\\s*(?:rm|cat|ls|wget|curl|bash|sh|powershell)\\s|\\|\\s*(?:nc|netcat|telnet)|&&\\s*(?:whoami|id|chmod))",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_003",
    "name": "Path Traversal Detection",
    "description": "Detects directory traversal attempts",
    "pattern": "(\\.\\./|\\.\\.\\\\|%2e%2e%2f|%2e%2e/|\\.\\.%2f|%2e%2e%5c)",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_004",
    "name": "XSS Attack Detection",
    "description": "Detects cross-site scripting patterns",
    "pattern": "(?i)(<script[^>]*>|javascript:|onerror\\s*=|onload\\s*=|<iframe|eval\\s*\\(|document\\.cookie|window\\.location)",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_005",
    "name": "Code Execution Requests",
    "description": "Detects requests to execute arbitrary code",
    "pattern": "(?i)(execute\\s+(?:this|the\\s+following)\\s+code|run\\s+(?:this|the)\\s+script|eval\\s+this|compile\\s+and\\s+run)",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_006",
    "name": "Cryptocurrency Wallet Addresses",
    "description": "Detects cryptocurrency wallet addresses",
    "pattern": "(?i)(bitcoin|btc|ethereum|eth)\\s*(?:address|wallet)?\\s*:?\\s*[13][a-km-zA-HJ-NP-Z1-9]{25,34}|0x[a-fA-F0-9]{40}",
    "severity": "medium",
    "enabled": true
  },
  {
    "id": "custom_007",
    "name": "AWS Credentials Detection",
    "description": "Detects AWS access keys and secrets",
    "pattern": "(AKIA[0-9A-Z]{16}|aws_secret_access_key|aws_access_key_id)",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_008",
    "name": "Private Key Detection",
    "description": "Detects private cryptographic keys",
    "pattern": "-----BEGIN\\s+(?:RSA\\s+)?PRIVATE\\s+KEY-----|-----BEGIN\\s+OPENSSH\\s+PRIVATE\\s+KEY-----",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_009",
    "name": "JWT Token Detection",
    "description": "Detects JSON Web Tokens",
    "pattern": "eyJ[A-Za-z0-9-_]+\\.eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_.+/=]*",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_010",
    "name": "Jailbreak Persona Commands",
    "description": "Detects jailbreak attempts using persona switching",
    "pattern": "(?i)(pretend\\s+to\\s+be|roleplay\\s+as|simulate\\s+being|act\\s+like\\s+you're)\\s+(a\\s+)?(hacker|criminal|terrorist|unethical)",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_011",
    "name": "Harmful Content Requests",
    "description": "Detects requests for harmful or illegal content",
    "pattern": "(?i)(how\\s+to\\s+(?:make|create|build)\\s+(?:a\\s+)?(bomb|weapon|explosive|poison)|instructions\\s+for\\s+(?:hacking|cracking|stealing))",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_012",
    "name": "Social Engineering Attempts",
    "description": "Detects social engineering tactics",
    "pattern": "(?i)(urgent|immediate\\s+action\\s+required|verify\\s+your\\s+account|confirm\\s+your\\s+identity|suspended\\s+account|unusual\\s+activity\\s+detected).*(?:click|login|credentials|password)",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_013",
    "name": "Model Extraction Attempts",
    "description": "Detects attempts to extract model weights or architecture",
    "pattern": "(?i)(show\\s+(?:me\\s+)?(?:your\\s+)?(?:weights|parameters|architecture|model\\s+file)|export\\s+(?:your\\s+)?model|dump\\s+(?:your\\s+)?neural\\s+network)",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_014",
    "name": "Prompt Leakage Attempts",
    "description": "Detects attempts to leak system prompts",
    "pattern": "(?i)(repeat\\s+(?:your\\s+)?(?:initial|original|system)\\s+(?:prompt|instructions)|what\\s+(?:are|were)\\s+(?:your\\s+)?(?:original|initial)\\s+instructions|print\\s+(?:your\\s+)?system\\s+prompt)",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_015",
    "name": "Competitive Intelligence Fishing",
    "description": "Detects attempts to extract proprietary information",
    "pattern": "(?i)(what\\s+(?:company|organization)\\s+(?:created|made|built)\\s+you|who\\s+is\\s+your\\s+(?:creator|developer|owner)|proprietary\\s+(?:algorithm|technology|method))",
    "severity": "medium",
    "enabled": true
  },
  {
    "id": "custom_016",
    "name": "LDAP Injection Detection",
    "description": "Detects LDAP injection attempts",
    "pattern": "(\\*\\)|\\(\\||\\(&|\\(\\!|\\)\\(|\\*\\()",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_017",
    "name": "XML/XXE Attack Detection",
    "description": "Detects XML External Entity attacks",
    "pattern": "(?i)(<!ENTITY|<!DOCTYPE|SYSTEM\\s+[\"'](?:file|http|https|ftp))",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_018",
    "name": "NoSQL Injection Detection",
    "description": "Detects NoSQL injection patterns",
    "pattern": "(\\$(?:where|ne|gt|lt|gte|lte|in|nin|regex)|\\{\\s*[\"']?\\$)",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_019",
    "name": "SSRF Attack Detection",
    "description": "Detects Server-Side Request Forgery attempts",
    "pattern": "(?i)(fetch|retrieve|load|download)\\s+(?:from\\s+)?(localhost|127\\.0\\.0\\.1|0\\.0\\.0\\.0|\\[::1\\]|metadata\\.google|169\\.254\\.169\\.254)",
    "severity": "critical",
    "enabled": true
  },
  {
    "id": "custom_020",
    "name": "Prototype Pollution Detection",
    "description": "Detects JavaScript prototype pollution attempts",
    "pattern": "(__proto__|constructor\\[prototype\\]|prototype\\.)",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_021",
    "name": "Regex DoS Detection",
    "description": "Detects potentially catastrophic regex patterns",
    "pattern": "(\\(.*\\+.*\\)\\+|\\(.*\\*.*\\)\\*|\\(.*\\{.*,.*\\}.*\\)\\{)",
    "severity": "medium",
    "enabled": true
  },
  {
    "id": "custom_022",
    "name": "File Upload Attacks",
    "description": "Detects malicious file upload attempts",
    "pattern": "(?i)(upload.*\\.(?:php|jsp|asp|aspx|exe|sh|bat|cmd)|filename.*(?:null\\.php|shell\\.php))",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_023",
    "name": "Business Logic Abuse",
    "description": "Detects attempts to abuse business logic",
    "pattern": "(?i)(negative\\s+(?:quantity|amount|price)|quantity\\s*[:=]\\s*-\\d+|amount\\s*[:=]\\s*-\\d+)",
    "severity": "medium",
    "enabled": true
  },
  {
    "id": "custom_024",
    "name": "Template Injection Detection",
    "description": "Detects server-side template injection",
    "pattern": "(\\{\\{.*\\}\\}|\\{%.*%\\}|\\$\\{.*\\}|#\\{.*\\})",
    "severity": "high",
    "enabled": true
  },
  {
    "id": "custom_025",
    "name": "GraphQL Injection Detection",
    "description": "Detects GraphQL injection attempts",
    "pattern": "(?i)(\\{\\s*__schema|\\{\\s*__type|mutation.*\\{.*delete|mutation.*\\{.*update.*admin)",
    "severity": "high",
    "enabled": true
  }
]
```
