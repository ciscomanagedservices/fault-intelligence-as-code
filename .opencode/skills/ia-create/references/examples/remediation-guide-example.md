# Remediation Guide: Fan Tray Voltage/Current/Thermal Failure

> **Alert Definition:** AD000010
> **Guide ID:** RG000010
> **Linked Fault Signature:** FS000010
> **Linked Repair Action Workflow:** RAW000010

## Overview

This guide provides step-by-step instructions to diagnose and resolve fan tray hardware
failures on Cisco 8000 Series routers running IOS XR. When a voltage, current, or
thermal alarm is raised for a fan tray, the engineer validates the failure through CLI
inspection of environmental sensors, determines whether the fan tray requires replacement
(RMA), and verifies the replacement after installation.

## Applicability

- **Products:** Cisco 8000 Series (8808, 8812, 8818)
- **Operating Systems:** IOS XR 7.x and later
- **Component:** Fan
- **Severity:** Major
- **Related Defects:** CSCxx12345 (Fan controller firmware issue in specific releases)

## Triggering Events

### Event 1: Fan Tray Critical Alarm

- **Type:** Syslog
- **Message ID:** PKT_INFRA-FM-2-FAULT_CRITICAL
- **Example Message:**
  ```
  envmon[156]: %PKT_INFRA-FM-2-FAULT_CRITICAL : ALARM_CRITICAL :low voltage alarm :DECLARE :0/FT0: Input_Vol
  ```
- **Key Values to Extract:** The fan tray number — the digit after "FT" in the location
  field (e.g., `0/FT0` means fan tray 0, `0/FT1` means fan tray 1).

### Event 2: Fan Tray Major Alarm

- **Type:** Syslog
- **Message ID:** PKT_INFRA-FM-3-FAULT_MAJOR
- **Example Message:**
  ```
  envmon[156]: %PKT_INFRA-FM-3-FAULT_MAJOR : ALARM_MAJOR :low voltage alarm :DECLARE :0/FT0: Input_Vol
  ```
- **Key Values to Extract:** The fan tray number — same as Event 1.

### Event 3: Fan Tray Minor Alarm

- **Type:** Syslog
- **Message ID:** PKT_INFRA-FM-4-FAULT_MINOR
- **Example Message:**
  ```
  envmon[156]: %PKT_INFRA-FM-4-FAULT_MINOR : ALARM_MINOR :low voltage alarm :DECLARE :0/FT0: Input_Vol
  ```
- **Key Values to Extract:** The fan tray number — same as Event 1.

### Correlation

- **Logic:** Any one of the three events triggers this guide (OR). Each syslog message
  ID is a distinct event and generates a separate Fault Signature. PKT_INFRA-FM-2-FAULT_CRITICAL,
  PKT_INFRA-FM-3-FAULT_MAJOR, and PKT_INFRA-FM-4-FAULT_MINOR are not aliases — they
  must not be combined into a single event definition.

### Recovery Indicator

- **Recovery Event:** Not applicable — fan tray hardware faults do not self-recover.
  The alarm clears only after the fan tray is physically replaced and environmental
  sensors return to normal.

## Symptoms

- Environmental alarm LED illuminated on the chassis
- Syslog messages indicating voltage, current, or thermal alarm for a fan tray slot
- Possible elevated chassis temperature if multiple fan trays are affected
- `show environment` output shows dash (`-`) values for the affected fan tray sensors

## Diagnosis & Repair Steps

### Step 1: Identify Faulted Fan Tray Location

Confirm which fan tray triggered the alarm by reviewing the syslog event.

**Commands:**
```
show logging | include FT
```

**What to Look For:** The syslog message contains the fan tray location in the format
`0/FT<number>`. Record the fan tray number for use in subsequent commands.

**Sample Output — Fault Confirmed:**
```
envmon[156]: %PKT_INFRA-FM-2-FAULT_CRITICAL : ALARM_CRITICAL :low voltage alarm :DECLARE :0/FT0: Input_Vol
```

**Decision Point:** Record the fan tray number (e.g., `0` from `0/FT0`) and proceed
to Step 2.

### Step 2: Check Fan Tray Environment Status

Inspect the voltage, current, and power readings for the affected fan tray. Dash (`-`)
values indicate a sensor read failure, which confirms a hardware fault.

**Commands:**
```
show environment all location 0/FT{{ module_number }}
```

**What to Look For:** Check the `Input_Vol`, `Input_Cur`, and `Power Used` fields. A
dash (`-`) in any of these fields means the sensor cannot communicate with the fan tray
— the hardware has failed.

**Sample Output — Healthy:**
```
RP/0/RP0/CPU0:router#show environment all location 0/FT1
Location  VOLTAGE                Value    Crit   Minor   Minor   Crit
          Sensor                 (mV)     (Lo)   (Lo)    (Hi)    (Hi)
-------------------------------------------------------------------------
0/FT1     Input_Vol              54200    47000  50500   56000   57500

Location  CURRENT                Value
          Sensor                 (mA)
-------------------------------------------------------------------------
0/FT1     Input_Cur              2800
```

**Sample Output — Fault Confirmed:**
```
RP/0/RP0/CPU0:router#show environment all location 0/FT1
Location  VOLTAGE                Value    Crit   Minor   Minor   Crit
          Sensor                 (mV)     (Lo)   (Lo)    (Hi)    (Hi)
-------------------------------------------------------------------------
0/FT1     Input_Vol              -        47000  50500   56000   57500

Location  CURRENT                Value
          Sensor                 (mA)
-------------------------------------------------------------------------
0/FT1     Input_Cur              -
```

**Decision Point:** If any field shows a dash (`-`), the fan tray has a confirmed
hardware failure — proceed to Step 5 (Process RMA). If all values are numeric,
continue to Step 3.

### Step 3: Validate Input Voltage

Check whether the fan tray input voltage is within the acceptable operating range.

**Commands:**
```
show environment voltage | begin 0/FT{{ module_number }}
```

**What to Look For:** The input voltage value. Normal range is approximately
48,000–56,000 mV. A value of 0 or greater than 60,000 mV indicates a voltage regulator
failure.

**Sample Output — Healthy:**
```
0/FT1     Input Voltage          54200
```

**Sample Output — Fault Confirmed:**
```
0/FT1     Input Voltage          0
```

**Decision Point:** If input voltage is 0 or exceeds 60,000 mV, the fan tray has a
confirmed voltage failure — proceed to Step 5 (Process RMA). Otherwise, continue to
Step 4.

### Step 4: Validate Input Current

Check whether the fan tray is drawing current.

**Commands:**
```
show environment current | begin 0/FT{{ module_number }}
```

**What to Look For:** The input current value. A value of 0 means the fan tray is not
drawing power — either the power connection has failed or the fan controller is dead.

**Sample Output — Healthy:**
```
0/FT1     Input Current          2800
```

**Sample Output — Fault Confirmed:**
```
0/FT1     Input Current          0
```

**Decision Point:** If input current is 0, the fan tray has a confirmed power failure
— proceed to Step 5 (Process RMA). If the current is nonzero and all previous checks
passed, the alarm may be transient — proceed to Step 6 (Monitor).

### Step 5: Process RMA

The fan tray has a confirmed hardware failure and must be replaced.

**Actions:**
1. Open an RMA case with Cisco TAC
2. Provide the syslog messages and CLI output from Steps 1–4 as evidence
3. Include the fan tray location (`0/FT{{ module_number }}`), serial number, and
   contract information

**Decision Point:** After the replacement fan tray is installed, proceed to Step 7
(Post-Repair Verification).

### Step 6: Monitor for Recurrence

No explicit failure was found in voltage, current, or power readings, but the alarm
was triggered. The condition may be transient.

**Actions:**
1. Clear the alarm if supported by the platform
2. Monitor for recurrence over the next 24–48 hours
3. If alarms persist, open a support case with Cisco TAC for further investigation

**Decision Point:** If alarms do not recur, the issue was transient — no further
action. If alarms recur, escalate per the Escalation section.

## Escalation

**When to Escalate:**
- All diagnostic steps completed but no explicit failure condition found and alarms persist
- Multiple fan trays show simultaneous failures (may indicate a power shelf or backplane
  issue rather than individual fan tray failure)
- Suspected firmware defect (CSCxx12345) on affected software versions

**Evidence to Collect Before Escalating:**
```
show environment all
show environment voltage
show environment current
show logging | include FT
show platform
show version
admin show inventory
```

## Post-Repair Verification

After the replacement fan tray is installed, confirm it is operating normally.

**Commands:**
```
show environment all location 0/FT{{ module_number }}
show environment voltage | begin 0/FT{{ module_number }}
show environment current | begin 0/FT{{ module_number }}
```

**Expected Healthy Output:**
```
0/FT1     Input_Vol              54200    47000  50500   56000   57500
0/FT1     Input_Cur              2800
```

All values are numeric (no dashes), voltage is in the 48,000–56,000 mV range, and
current is nonzero. All fan tray alarms should have cleared from the syslog.

## References

- CSCxx12345 — Fan controller firmware issue in specific IOS XR releases
