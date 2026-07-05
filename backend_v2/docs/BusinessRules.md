# Engine Business Rules Specifications — Product Guardian Network (PGN)

This document formalizes the validation, classification, and scoring algorithms built into PGN.

---

## 1. Consumer Report Credibility Engine (CRCE)
The credibility score ($0-100$) of a product report is calculated as follows:

| Rule | Base Points | Description |
|---|---|---|
| **Barcode Exists** | $+20$ | Matches a valid registered product in catalogue. |
| **Batch Provided** | $+15$ | A batch identifier string is supplied. |
| **Image Uploaded** | $+15$ | At least one evidence image is attached. |
| **Receipt Uploaded** | $+15$ | Image URL contains "receipt" keyword. |
| **User Verified** | $+10$ | User holds a verified community status. |
| **Valid Purchase Date** | $+10$ | Purchase date matches standard bounds. |
| **Location Provided** | $+5$ | Store location is supplied. |
| **Description Length** | Up to $+15$ | $+5$ for $\ge 20$ chars, $+10$ for $\ge 50$ chars, $+15$ for $\ge 100$ chars. |
| **Duplicates Penalty** | Up to $-30$ | $-10$ for each matching duplicate report by same user. |

---

## 2. Product Issue Clustering Engine (PICE)
Reports automatically join a cluster if they match the following criteria:
- Same **Barcode** (product ID).
- Same **Batch Number**.
- Same **Report Type**.
- Submitted within **30 days** of the last reported activity of that cluster.

---

## 3. Community Intelligence Engine (CIE)
- **Growth Rate**: Compare reports in the last 24h against reports in the previous 24h.
- **Trend Categorization**:
  - Growth $< -20\%$: `DECLINING`
  - Growth $-20\%$ to $+20\%$: `STABLE`
  - Growth $+20\%$ to $+75\%$: `GROWING`
  - Growth $> 75\%$: `RAPIDLY_GROWING`
- **Spread Categorization**:
  - $1$ city: `LOCAL`
  - $2-5$ cities: `REGIONAL`
  - $6-10$ cities: `MULTI_REGION`
  - $> 10$ cities: `NATIONAL`

---

## 4. Community Safety Alert Engine (CSAE)
A Safety Alert is automatically generated if ANY of the following conditions are met:
- **Risk Score** $\ge 80$
- **Cluster Severity** is `CRITICAL`
- **Reports Count** $> 20$
- **Affected Cities** $> 5$
- **Trend** is `RAPIDLY_GROWING`
- **Average Credibility** $> 80.0$
- **Escalation Level** is `URGENT` or `CRITICAL`

---

## 5. Investigation & Case Management Engine (ICME)
- **Eligibility**: Cases can only be spawned for alerts that are `HIGH_RISK` or `CRITICAL`.
- **Constraint**: Only one active (non-resolved, non-closed) case is permitted per alert.
- **Alert Synch**: When a case is closed, the associated alert is closed automatically if the cluster risk score is $< 75$ and severity is not `CRITICAL`.
