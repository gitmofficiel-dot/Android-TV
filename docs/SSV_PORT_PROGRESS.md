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
