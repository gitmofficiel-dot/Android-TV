# SSV port progress — 2026-10-25

Run40208375559: BSP5.4.125 kernel/Image/modules built successfully; SSV source
failed in ssvdevice.c at the procfs boundary. No SSV module was produced.

Commit8bd55a6 adds a namespaced compatibility header and patch to use
file_operations before5.6 and PDE_DATA before5.17. No warning/error suppression
was added. Run40215615750 is the retry; its result is pending at this checkpoint.

Host validation:14 unittest cases passed, including3 API-contract smoke tests
that compile and invoke the compatibility mappings for5.4,5.6,5.17. These use
minimal kernel API stubs; they do not replace building against real headers.
Host IR decoder test also passed. Patch application and reverse application
checks passed against pinned upstream43c2ede238b39ba3abb1129323a998495c6b8be9.

Stock boot.img was re-read from the user attachment, hash matched the previously
recorded original, and header/footer bounds were checked. Details are recorded
in STOCK_BOOT_HEADER.json. Header v2/page2048/boot32MiB differ from T95 v3 with
vendor_boot/A-B layout. This analysis did not modify or re-sign stock boot.img.

Important ABI boundary: an SSV module compiled against the reference5.4.125 BSP
is not a module for the donor5.4.302 kernel. A final port must use one matching
kernel source/config, Module.symvers, kernel modules and userspace hardware ABI.
Even successful compilation does not prove SDIO/RF/firmware/Android integration.

No complete H20 Android12/16 image has been produced, installed or boot-tested.

## Boot packing size experiment
The donor asset was downloaded again and its pinned SHA256 and XZ stream test
passed. Its boot/vendor_boot entries were read from the bounded IMAGEWTY table.
Legacy-LZ4 ramdisk blocks were decoded with liblz4 into27287808 bytes of newc CPIO.
GZIP9 round-trip preserved all CPIO bytes, but kernel+generic ramdisk alone still
needed35090432 bytes at2048-byte alignment, exceeding32MiB.
A second in-memory experiment omitted only system/bin/{fastbootd,recovery,
update_engine_sideload}, retaining ADB/init/shared libraries. Its gzip output was
8976219 bytes; the hypothetical aligned boot payload was32681984 bytes, before
vendor ramdisk, DTB and AVB. This is a potential size strategy, not an approved
ramdisk change. Recovery-service dependencies, boot mode, header/AVB acceptance
and actual board settings remain unresolved. No boot.img was repacked or signed.
See RAMDISK_SIZE_EXPERIMENT.json. Removing binaries is not proof of compatibility.

## Retry40215615750 actual result
Base kernel built and its workspace was cached. Procfs errors were resolved;
the compiler advanced to smac/dev.c and rate-control files. It then failed at
pre-MLO mac80211 differences: vif.cfg, sta.deflink, bss_info_changed u64 vs u32,
conf_tx link_id and missing ieee80211_handle_wake_tx_queue.
Patch0002 adds versioned accessors/callback argument types from primary Linux
headers: sta.deflink since5.19; vif.cfg and callback/link_id changes since6.0;
default wake_tx_queue helper since6.2. Older kernels retain the existing direct
.tx path. No incompatible function pointer casts or error suppression are used.
Actual translation of this second patch is pending; no driver success is claimed.

## Current checkpoint
Patch0002 was committed as4fda4d5. Its host validation run40216909769 passed;
the suite contains17 tests, including6 compatibility contract tests.
Actual module retry: https://github.com/gitmofficiel-dot/Android-TV/actions/runs/40216909746
At this checkpoint the runner is still installing build tools, so the patched
module has not yet been compiled in that run. This is not a successful module
build and does not change the no-firmware/no-device-boot status above.
