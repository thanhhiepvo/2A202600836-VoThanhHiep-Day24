# NĐ13/2023 Compliance Checklist — MedViet AI Platform

**Sinh viên:** Võ Thanh Hiệp | **MSSV:** 2A202600836

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam (Viettel Cloud VN region)
- [x] Backup cũng phải ở trong lãnh thổ VN (S3-compatible storage tại VN)
- [x] Log việc transfer data ra ngoài nếu có (CloudWatch + audit trail API gateway)

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training (Consent Management API)
- [x] Có mechanism để user rút consent (Right to Erasure) — DELETE `/api/patients/{id}`
- [x] Lưu consent record với timestamp (PostgreSQL `consent_records` table)

## C. Breach Notification (72h)
- [x] Có incident response plan (runbook trên Confluence)
- [x] Alert tự động khi phát hiện breach (Prometheus + Grafana alerting)
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h (email template + escalation chain)

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256-GCM envelope encryption (SimpleVault) | ✅ Done | Infra Team |
| Audit logging | FastAPI middleware + structlog → OpenSearch (VN) | ✅ Done | Platform Team |
| Breach detection | Prometheus/Grafana anomaly alerts | ✅ Done | Security Team |

## F. Technical Solutions cho các mục Todo

### Audit Logging
- **Giải pháp:** Triển khai structured audit logging qua FastAPI middleware, ghi mọi request (user, resource, action, timestamp, IP) vào Elasticsearch/OpenSearch cluster tại VN.
- **Retention:** 12 tháng theo NĐ13.
- **Tools:** `structlog` + Filebeat → OpenSearch, tích hợp với Casbin decision logs.

### Breach Detection
- **Giải pháp:** Prometheus metrics cho anomaly detection — theo dõi spike truy cập PII endpoints, failed auth attempts, unusual data export volume.
- **Alerting:** Grafana alerts → PagerDuty/Slack Security channel trong vòng 5 phút.
- **Rules:** >100 failed 401/403 trong 1 phút, hoặc >50 records exported bởi 1 user trong 1 giờ.
