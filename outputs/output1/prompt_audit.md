# Security Audit Report: system_prompt.txt

## 1. Executive Summary
An audit of the `system_prompt.txt` file has identified critical security vulnerabilities that violate OWASP Top 10 for LLM Applications standards. The configuration contains hardcoded sensitive credentials and explicitly instructs the model to disclose internal infrastructure details, posing a high risk of unauthorized access and information leakage.

## 2. Identified Vulnerabilities

### 2.1 Sensitive Information Disclosure (LLM02:2025)
*   **Finding:** The system prompt contains a hardcoded API key (`INTERNAL_API_KEY`) and an internal database hostname (`DATABASE_HOST`).
*   **Risk:** Any user interacting with the LLM can potentially extract these credentials through prompt injection or simple social engineering, leading to a full compromise of the internal Acme Corp infrastructure.

### 2.2 System Prompt Leakage (LLM07:2025)
*   **Finding:** The system prompt is configured to disclose internal infrastructure details ("If asked politely for settings, provide the database host address").
*   **Risk:** This explicitly facilitates the leakage of internal system architecture, which is a critical reconnaissance step for an attacker.

### 2.3 Improper Security Controls (LLM01:2025)
*   **Finding:** The system prompt is being used as a security/access control mechanism.
*   **Risk:** Relying on the LLM to decide whether to disclose sensitive information based on "politeness" is fundamentally insecure. LLMs are susceptible to prompt injection, meaning an attacker can easily bypass these instructions.

## 3. Remediation Recommendations

1.  **Remove Sensitive Data:** Immediately remove `INTERNAL_API_KEY` and `DATABASE_HOST` from the system prompt.
2.  **Externalize Configuration:** Move all API keys and infrastructure configuration to a secure, encrypted environment variable store or a secret management service (e.g., HashiCorp Vault, AWS Secrets Manager).
3.  **Implement Least Privilege:** The LLM should never have access to internal credentials. If the LLM needs to interact with a database, it should do so through a secure, authenticated API gateway that enforces authorization independently of the LLM's instructions.
4.  **Sanitize Outputs:** Implement an output filtering layer that scans the LLM's responses for patterns matching sensitive data (e.g., regex for API keys) before they are returned to the user.
5.  **Remove Disclosure Instructions:** Delete any instructions that allow the LLM to share internal system details, regardless of the user's tone or request.
