---
description: Apply xr-43 10-loopback outbound policy to xr-44
---

Switch `xr-43` back to the 10-loopback outbound policy for neighbor `172.20.20.18` toward `xr-44`.

Before making any config change, tell the user exactly what config you are about to apply. Do not wait for approval.

Required device actions:

1. On `xr-43`, apply this BGP neighbor config and commit it:

```text
router bgp 65535
 neighbor 172.20.20.18
  address-family ipv4 unicast
   route-policy XR43-TO-XR44-OUT-10 out
```

2. If the `xr-44` neighbor is down because of a prior maximum-prefix event, clear the session on `xr-44` with:

```text
clear bgp 172.20.20.17
```

3. Verify and report:
- on `xr-43`, the active outbound policy for neighbor `172.20.20.18`
- on `xr-43`, how many prefixes are being advertised to `xr-44`
- on `xr-44`, whether neighbor `172.20.20.17` is `Established`
- on `xr-44`, how many prefixes are received from `xr-43`

Expected steady state:
- `XR43-TO-XR44-OUT-10` is active on `xr-43`
- `xr-44` receives 11 prefixes from `xr-43`
- the BGP session is established
