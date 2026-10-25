# SSV6x5x kernel5.4 port attempt

Upstream revision:43c2ede238b39ba3abb1129323a998495c6b8be9 (cdhigh/armbian_sv6256p).
No hardware support is claimed. Patches retain upstream file licensing; the new
compatibility header is MIT. The changed original source is GPL-3.0-or-later.

## Reproduced failure
GitHub job121214114785/run40208375559 built the BSP kernel successfully, then
failed compiling ssvdevice/ssvdevice.c. Kernel5.4 expects file_operations/PDE_DATA;
upstream unconditionally uses proc_ops/pde_data. These produced unknown types,
missing designated fields and incompatible proc_create_data pointer arguments.

## Patch0001
Namespaced field/type macros select file_operations before5.6 and proc_ops after.
Private-data accessor selects PDE_DATA before5.17 and pde_data after. The old API
also receives THIS_MODULE ownership. Callbacks and private data are preserved;
no pointer casts, warning suppression or permissions changes are introduced.
Primary references checked: torvalds/linux v5.4, v5.6 and v5.17 include/linux/proc_fs.h.
All4 operation tables and4 private-data lookups are covered.

Validation executed locally: applies/reverses cleanly against the pinned source;
git diff --check; shell syntax; YAML parse;11 Python tests and host IR test passed.
Full kernel translation after patch is pending in GitHub Actions. Other kernel
API differences may surface once this first translation unit compiles.

The downloaded upstream also contains pre-existing unsafe proc callbacks (for
example a writable string-literal pointer for p2pStatus). Compile success alone
must not be used to release this driver for users. Runtime review remains open.
The kernel cache is saved before the separate driver experiment so subsequent
port fixes can reuse the successfully compiled base rather than rebuilding it.
