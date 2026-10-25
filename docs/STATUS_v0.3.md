# v0.3 — 2026-10-25
## Work completed
- Inspected BPI published Android12 BSP README, kernel Makefile (5.4.125), M4Zero
  board DTS and PMIC driver. Stored exact file blob IDs and URLs, no copied code.
- Added strict offline FDT parser, selected board inventory and LP3 requirements.
- Parsed actual stock DT: 533 nodes; generated selected hardware facts without
  /chosen, MAC/serial identifiers or keys. DTB provenance retained as SHA256.
- Eight Python fixture tests pass (GPT + FDT), including malformed input checks.
- FE01 C unit test still passes with strict compiler warnings enabled.

## Corrections
Earlier comparison said reference USB0 host differs from LP3 working ADB.
The stock DT ALSO specifies host by default. Runtime device-mode switching makes
ADB work; the required distinction is preserving that runtime behavior.

## Not completed
No BSP sync, kernel build, Android16 vendor migration, Android image, actual-device
execution of new code, flash, recovery validation or cryptographic AVB verification.
This Work host has about 30GiB free, insufficient for a full AOSP build. User's
Ubuntu root previously had ~11GB. Build provisioning remains a real blocker.
Do not run large repo sync on either environment.
