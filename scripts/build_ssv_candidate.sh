#!/usr/bin/env bash
# Compile-only experiment. Does not install firmware or load a module.
set -euo pipefail
kernel=${1:?Kernel source path required}
kernel_out=${2:?Matching completed kernel build output required}
driver=${3:?New driver checkout directory required}
diagnostics=${4:?Diagnostics directory required}
project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
kernel=$(realpath "$kernel")
kernel_out=$(realpath "$kernel_out")
test "$(git -C "$kernel/../../.." rev-parse HEAD)" = 250eabfc529518b7f26432663ed0a867ab2f625d
test -f "$kernel_out/Module.symvers"
test -f "$kernel_out/include/generated/autoconf.h"
grep -q '^CONFIG_ARM64=y$' "$kernel_out/.config"
grep -Eq '^CONFIG_CFG80211=[ym]$' "$kernel_out/.config"
test ! -e "$driver" || { echo 'Refusing to overwrite a driver directory' >&2; exit 2; }
mkdir -p "$driver" "$diagnostics"
driver=$(realpath "$driver")
diagnostics=$(realpath "$diagnostics")
revision=43c2ede238b39ba3abb1129323a998495c6b8be9
repo=https://github.com/cdhigh/armbian_sv6256p.git
printf 'source=%s\nrevision=%s\nrole=compile-experiment-NOT-H20-validated\n' "$repo" "$revision" > "$diagnostics/SSV-SOURCE.txt"
git -C "$driver" init
git -C "$driver" remote add origin "$repo"
git -C "$driver" fetch --depth 1 origin "$revision"
git -C "$driver" checkout --detach FETCH_HEAD
test "$(git -C "$driver" rev-parse HEAD)" = "$revision"
git -C "$driver" apply --check "$project_root/patches/ssv6x5x/0001-procfs-5.4-compat.patch"
git -C "$driver" apply "$project_root/patches/ssv6x5x/0001-procfs-5.4-compat.patch"
git -C "$driver" apply --check "$project_root/patches/ssv6x5x/0002-mac80211-pre-MLO-compat.patch"
git -C "$driver" apply "$project_root/patches/ssv6x5x/0002-mac80211-pre-MLO-compat.patch"
git -C "$driver" apply --check "$project_root/patches/ssv6x5x/0003-beacon-pre-MLO-compat.patch"
git -C "$driver" apply "$project_root/patches/ssv6x5x/0003-beacon-pre-MLO-compat.patch"
sha256sum "$project_root"/patches/ssv6x5x/*.patch > "$diagnostics/SSV-PATCH.sha256"
make -C "$kernel" O="$kernel_out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  KERNEL_SRC="$kernel" INSTALL_MOD_PATH="$kernel_out/modules-staging" \
  M="$driver" -j2 modules 2>&1 | tee "$diagnostics/ssv-build.log"
test -s "$driver/ssv6x5x.ko"
cp "$driver/ssv6x5x.ko" "$diagnostics/ssv6x5x-NOT-HARDWARE-TESTED.ko"
aarch64-linux-gnu-readelf -h "$driver/ssv6x5x.ko" > "$diagnostics/ssv-elf.txt"
sha256sum "$driver/ssv6x5x.ko" > "$diagnostics/ssv-sha256.txt"
echo 'Compile experiment passed; SDIO, firmware, RF and Android integration remain untested.'
