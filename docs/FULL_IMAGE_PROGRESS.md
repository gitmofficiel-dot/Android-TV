# Full stock image analysis — 2026-10-25

## Executed
Downloaded the release asset (1493189716 bytes) and matched its SHA256:
4e25a18c945f3d28445cb48875ae567715f72a05e5ab3aef9048aff76953c456.
XZ decompression completed to exactly 7818182656 bytes. Uncompressed SHA256:
dd2db326486d188f94f4de1a7710049377ab645f122ee3bffc2ade7f442db293.

Both GPT header/table CRCs passed; primary and backup entry tables are identical.
All four LP metadata copies (primary/backup slots0/1) passed header/table SHA256,
with valid single-device linear extents. Extracted system/vendor/product images:
1834414080 / 206163968 / 57372672 bytes. Read-only e2fsck -fn returned0 on all three.
Boot/recovery hashes match the previously attached individual image files.
Only system/vendor/product were inspected as filesystems; userdata was not inspected.

## Android state
The system build declares Android10 SDK29, ARM32 ABI and security patch2019-12-05.
The first API level in vendor is29. No Android16 system has been built or booted.
The JSON audit contains additional integrity evidence and explicit AVB trust limits.

## Development work
Added a tested raw-super metadata reader/extractor. Added Soong module definitions
for the original FE01 decoder and its host test; Soong has NOT been run.
Added a GitHub Actions build of the immutable H618 reference kernel source:
BPI-SINOVOIP/BPI-H618-Android12 @ 250eabfc529518b7f26432663ed0a867ab2f625d.
The reference defconfig is sun50iw9p1smp_h618_android_defconfig (blob
423d625b4437e0e598c80a63440155eab5ee7770). The kernel Makefile reports5.4.125.
It is a source/build feasibility test, NOT an LP3 image or Android16 firmware.
Do not flash a reference Image; LP3 DTS, DDR, USB role, SSV and GPU matching remain.

## Full Android16 build blockers
AOSP documented baseline requires400GB free and64GB RAM; local Work disk is32GB.
No sufficiently provisioned full Android build host has been connected. No paid
host or paid GitHub runner has been provisioned. Normal host CI success does not
mean an Android build can fit or has happened.
Stock FCM4 vendor does not match the documented Android16 supported FCM range.
Vendor/kernel/HAL migration and validated recovery remain prerequisites.
Google TV branding/services are not claimed; direct target remains AOSP TV16.

## Boot-chain evidence in the full disk
The reserved region before named partitions contains eGON.BT0 headers at8192
and262144, and sunxi-package headers at12582912 and16793600 bytes.
Both packages contain the version string U-Boot2018.05, dated2024-04-09.
Embedded main DTBs at13725696 and17936384 are byte-identical (139912 bytes,
SHA256 a5e9f46fe9df8bab9382a3a699e4517c4b56a3e893a2e6d0233567ee449df0aa).
These observations do not verify the package checksums or device boot selection.
The DT includes numerous alternate DRAM profiles; their presence does not establish
which profile was used for memory training. Keep the original boot chain intact.
The full user-area disk contains these reserved boot-chain copies, but is not a
capture of the separate eMMC hardware boot0/boot1 regions or RPMB.

## Reference build attempts
Actions run40206676417 configured the reference kernel successfully, then failed
because the vendor NAND Makefile requires KERNEL_SRC/LICHEE_KDIR even when entered
from normal Kbuild. Its own source explicitly accepts KERNEL_SRC as a fallback.
The build script now passes that source path and preserves provenance before
compilation. Run40206920820 is the retry; no success is claimed until it finishes.
