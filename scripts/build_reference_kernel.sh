#!/usr/bin/env bash
# Builds an upstream BSP reference kernel. NOT LP3 board firmware or Android16.
set -euo pipefail
src_root=${1:?Usage: build_reference_kernel.sh NEW_SOURCE_DIR OUTPUT_DIR}
out_root=${2:?Output directory required}
revision=250eabfc529518b7f26432663ed0a867ab2f625d
repo=https://github.com/BPI-SINOVOIP/BPI-H618-Android12.git
if [[ -e "$src_root" ]]; then
  echo 'Refusing to reuse or overwrite a source directory' >&2; exit 2
fi
mkdir -p "$src_root" "$out_root"
src_root=$(realpath "$src_root")
out_root=$(realpath "$out_root")
git -C "$src_root" init
git -C "$src_root" remote add origin "$repo"
git -C "$src_root" sparse-checkout init --cone
git -C "$src_root" sparse-checkout set longan/kernel/linux-5.4
git -C "$src_root" -c protocol.version=2 fetch --depth=1 --filter=blob:none origin "$revision"
git -C "$src_root" checkout --detach FETCH_HEAD
test "$(git -C "$src_root" rev-parse HEAD)" = "$revision"
kernel="$src_root/longan/kernel/linux-5.4"
make -C "$kernel" O="$out_root" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- sun50iw9p1smp_h618_android_defconfig
make -C "$kernel" O="$out_root" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j2 Image modules
printf 'source=%s\nrevision=%s\nrole=H618-reference-only-not-LP3-firmware\n' "$repo" "$revision" > "$out_root/SOURCE.txt"
aarch64-linux-gnu-gcc --version > "$out_root/compiler-version.txt"
sha256sum "$out_root/arch/arm64/boot/Image" > "$out_root/Image.sha256"
