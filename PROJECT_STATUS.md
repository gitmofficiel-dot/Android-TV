# GITM H20 Pro Android TV
Target: AOSP Android TV16 for PCB H20-pro-lp3-230916.
Status: pre-port engineering. No Android16 image built or booted.

Implemented: tested offline GPT/FDT evidence tooling, FE01 IR decode component,
board evidence inventory, source review and hardware acceptance plan.
GitHub Actions validates these components only; it does not build Android OS.

Blocked full build: complete version-pinned BSP and target vendor migration,
compatible graphics/media/Wi-Fi source/blobs, adequate build host, verified
recovery. Current vendor FCM4 is outside Android16 documented supported levels.

Private stock dumps and proprietary binaries must remain outside this repository.
No flashing without device-specific validation and explicit user approval.
