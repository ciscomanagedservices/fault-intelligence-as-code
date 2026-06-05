---
description: Apply xr-43 20-loopback outbound policy to xr-44
---

Switch `xr-43` to the 20-loopback outbound policy for neighbor `172.20.20.18` toward `xr-44`.

Before making any config change, tell the user exactly what config you are about to apply. Do not wait for approval.

Required device actions:

1. On `xr-43`, apply this BGP neighbor config and commit it:

```text
router bgp 65535
 neighbor 172.20.20.18
  address-family ipv4 unicast
   route-policy XR43-TO-XR44-OUT-20 out
```

2. Verify and report:
- on `xr-43`, the active outbound policy for neighbor `172.20.20.18`
- on `xr-44`, whether neighbor `172.20.20.17` drops due to maximum-prefix
- on `xr-44`, the exact BGP state shown in summary output
- on `xr-44`, the reset reason from neighbor detail output

Expected outcome in the current lab state:
- `XR43-TO-XR44-OUT-20` is active on `xr-43`
- `xr-44` enforces `maximum-prefix 18 80`
- the session drops and shows `Idle (PfxCt)` because the peer exceeds the configured prefix limit
