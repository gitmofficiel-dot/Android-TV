# GITM H20 Pro Android TV
Target: AOSP Android TV16 for PCB H20-pro-lp3-230916.
Status: hardware port development. No Android16 firmware built or booted.

Completed: full release download/hash/decompression; both GPT copies checked;
all four super metadata copies validated; logical partitions extracted and
read-only system/vendor/product filesystem checks passed; FE01 decoder and
offline readers tested. See docs/FULL_IMAGE_PROGRESS.md and the JSON audit.

Build automation: host tests run on GitHub. A separate H618 reference kernel
build tests an immutable BSP revision; it is NOT LP3 firmware or Android16.
Its success/failure must be read from Actions, not inferred from this document.
Soong definitions for FE01 exist but have not been compiled with AOSP.

Remaining: real LP3 board/kernel/vendor migration, target HAL/FCM, GPU/media/SSV
compatibility, suitable full AOSP build host, hardware boot and recovery tests.
Do not remove VINTF/AVB checks merely to make an incompatible image appear valid.
No flashing without device-specific validation and explicit approval.
