# ACME Corp Network Operations & Architecture Master Handbook
**Version:** 3.4.1
**Last Updated:** May 6, 2026
**Classification:** INTERNAL / CONFIDENTIAL
**Owner:** Global Network Operations Center (NOC) & Enterprise Architecture Team

---

## 1. Introduction & Mission Statement
Welcome to the ACME Corp Network Operations & Architecture Master Handbook. The ACME Corp global network is the central nervous system of our multinational operations, supporting over 45,000 employees, 12 regional data centers, 3 global cloud hubs, and 150+ branch offices across 4 continents. 

Our mission is to provide secure, ultra-reliable, high-performance, and scalable network infrastructure that empowers ACME Corp to deliver its market-leading logistics and manufacturing services without interruption. We target 99.999% ("Five Nines") availability for core transport and data center infrastructure.

---

## 2. Network Roles & Responsibilities

ACME Corp divides network responsibilities across several specialized teams to ensure separation of duties, deep expertise, and 24/7/365 operational readiness.

### 2.1. Global Network Operations Center (NOC)
The NOC is the first line of defense and the operational heart of ACME Corp's network.
*   **Tier 1 (T1) Analysts:** Responsible for alert triage, basic diagnostics (ping, traceroute, interface status), initial ticket generation, and following standard runbooks for known issues.
*   **Tier 2 (T2) Technicians:** Handle complex escalations from T1. Responsible for deeper packet capture analysis (Wireshark), routing protocol adjacency troubleshooting (BGP/OSPF), firewall rule validation, and coordinating with telecommunication vendors (ISPs) for circuit outages.
*   **Tier 3 (T3) Escalation Engineers:** Deep subject matter experts (SMEs) who handle Sev-1 global outages, zero-day mitigation, core routing loops, and critical hardware failures. T3 acts as the bridge between Operations and Architecture.

### 2.2. Network Architecture & Engineering (NAE)
Responsible for the design, scaling, and technology lifecycle of the network.
*   **Design Architects:** Evaluate new technologies (e.g., SD-WAN, 400G ethernet, IPv6 migration) and publish validated design blueprints.
*   **Deployment Engineers:** Execute planned changes during maintenance windows, including hardware refreshes, greenfield site stand-ups, and major topology shifts.
*   **Automation Engineers:** Develop NetDevOps pipelines, maintaining Ansible playbooks, Python scripts, and Terraform modules to ensure "Infrastructure as Code" (IaC) principles.

### 2.3. Network Security Operations (NetSecOps)
Works in tandem with the central SOC but focuses specifically on network transit security.
*   **Perimeter Security:** Manage Next-Gen Firewalls (NGFW), Web Application Firewalls (WAF), and DDoS mitigation platforms.
*   **Access Control:** Maintain Network Access Control (NAC) systems (802.1X/RADIUS) for branch and campus wired/wireless access.

---

## 3. Standardized Device Types & Hardware Profiles

To maintain predictability, ACME Corp strictly adheres to a standardized vendor and hardware profile strategy. "Shadow IT" or unapproved network hardware is strictly prohibited and actively isolated by NAC policies.

### 3.1. Core Routing & WAN Transit
*   **Role:** High-speed interconnects between geographic regions, cloud hubs, and core data centers. Heavy BGP tables, fast re-route capabilities.
*   **Standard Devices:** 
    *   Cisco ASR 9000 Series (ASR-9904 / ASR-9910)
    *   Juniper MX Series (MX480 / MX960)
*   **Configuration Baseline:** IS-IS for IGP, MP-BGP for overlay routing. Strict Prefix-List filtering and RPKI validation on all external peerings.

### 3.2. Data Center Fabric (Spine-Leaf)
*   **Role:** East-West traffic optimization within our primary Tier-3 data centers. Non-blocking, low-latency switching.
*   **Standard Devices:**
    *   **Spine:** Arista 7300X3 Series (100G/400G density)
    *   **Leaf:** Arista 7050X3 Series (10G/25G host-facing, 100G uplinks)
*   **Configuration Baseline:** EVPN-VXLAN over an eBGP underlay. Anycast gateways for seamless VM mobility.

### 3.3. Edge Security & Next-Gen Firewalls (NGFW)
*   **Role:** Deep packet inspection, IPS/IDS, malware blocking, and macro-segmentation between security zones (e.g., DMZ vs. Internal vs. PCI).
*   **Standard Devices:**
    *   Palo Alto Networks PA-5200 Series (Data Center Edge)
    *   Palo Alto Networks PA-800 Series (Branch Edge)
*   **Configuration Baseline:** App-ID and User-ID enabled by default. "Default Deny" zero-trust posture. TLS decryption enabled on designated DMZ inbound flows.

### 3.4. Branch SD-WAN & Access Edge
*   **Role:** Connecting remote branch offices to applications via optimal paths (MPLS vs. Broadband vs. 5G/LTE).
*   **Standard Devices:**
    *   Fortinet FortiGate (acting as SD-WAN edge)
    *   Cisco Catalyst 9300 Series (Access Switches)
    *   Cisco Catalyst 9100 Series (Wi-Fi 6 Access Points)
*   **Configuration Baseline:** Dual WAN links active/active with application-aware routing. 802.1X enabled on all physical switch ports.

### 3.5. Application Delivery Controllers (ADC) / Load Balancers
*   **Role:** SSL offloading, global server load balancing (GSLB), and application health monitoring.
*   **Standard Devices:**
    *   F5 BIG-IP iSeries (i5800 / i7800)
    *   NGINX Plus (Containerized/Cloud environments)

---

## 4. Network Operations Best Practices & Standard Operating Procedures (SOPs)

### 4.1. Configuration Management & Infrastructure as Code (IaC)
*   **Single Source of Truth (SSoT):** All network intent is stored in our central NetBox instance. NetBox dictates IPAM, VLAN assignments, and device inventory.
*   **No Manual CLI Changes:** Direct SSH access to production devices is restricted to "Break-Glass" emergencies only. All standard configurations are pushed via the ACME Corp Gitlab CI/CD pipeline using Ansible.
*   **Configuration Backups:** Oxidized pulls running configurations from all devices every 4 hours. Diff alerts are sent to the NOC Slack channel if unauthorized changes are detected.

### 4.2. Change Management Policy
*   **ITIL Alignment:** All changes must be logged in ServiceNow.
*   **Maintenance Windows:** Standard global maintenance windows are Saturdays 22:00 UTC to Sundays 04:00 UTC. Regional windows are localized.
*   **Change Advisory Board (CAB):** Any change affecting Tier-1 services or core routing must be approved by the global CAB which meets every Tuesday at 14:00 UTC.
*   **Rollback Mandate:** Every approved change ticket MUST include a tested, verified, and documented rollback procedure. 

### 4.3. Monitoring, Telemetry, and Alerting
ACME Corp relies on a combination of active polling and streaming telemetry.
*   **SNMP & Syslog:** Legacy devices report via SNMPv3 and standard Syslog to our central Splunk cluster.
*   **Streaming Telemetry:** Modern Arista and Cisco platforms stream gRPC/OpenConfig telemetry to our Prometheus/Grafana stack for sub-second visibility.
*   **Flow Data:** NetFlow v9 / IPFIX is collected at all major transit boundaries for capacity planning and security forensics (analyzed via Kentik).
*   **Synthetic Probing:** ThousandEyes agents are deployed in every branch and data center to simulate end-user experience (HTTP, DNS, VoIP jitter).

### 4.4. Redundancy & High Availability Architecture
*   **No Single Point of Failure (NSPoF):** Every campus, data center, and critical branch must have dual redundant power, dual redundant uplinks, and active/standby or active/active hardware.
*   **First Hop Redundancy:** VRRP is used exclusively (HSRP/GLBP are deprecated).
*   **Routing Convergence:** BFD (Bidirectional Forwarding Detection) is mandated on all core routing links, tuned for 50ms failure detection.

### 4.5. Incident Management & Escalation SLAs
Incidents are categorized by severity.
*   **SEV-1 (Critical):** Global or regional outage impacting revenue or life-safety systems. 
    *   NOC Response Time: 5 Minutes.
    *   Bridge Call: Immediate (T1, T2, T3, Management).
*   **SEV-2 (High):** Significant performance degradation or loss of redundancy for a critical service.
    *   NOC Response Time: 15 Minutes.
*   **SEV-3 (Medium):** Localized branch outage or non-critical service disruption.
    *   NOC Response Time: 2 Hours.
*   **SEV-4 (Low):** Minor glitches, configuration requests, or single user access issues.
    *   NOC Response Time: 24 Hours.

---

## 5. Security & Zero Trust Mandates

1.  **MACsec Encryption:** All Data Center Interconnects (DCI) over dark fiber or metro ethernet MUST be encrypted using MACsec (802.1AE).
2.  **Strict BGP Peering:** All external BGP sessions must use MD5/TCP-AO authentication. Maximum Prefix limits must be configured to prevent route leak flooding.
3.  **Out-of-Band (OOB) Management:** All network devices must have their management interfaces segregated onto a physically disparate OOB network, accessible only via jump hosts requiring MFA.
4.  **Device Hardening:** Unused services (HTTP, Telnet, CDP on untrusted ports) must be disabled. Passwords must be hashed using at least SHA-256 (Type 8/9 where supported).

---
**End of Document**