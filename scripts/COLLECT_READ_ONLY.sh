#!/usr/bin/env bash
# No root/reboot/remount/setprop/push/flash. Writes only to the host output folder.
set -euo pipefail
umask 077
command -v adb >/dev/null || { echo 'Install adb on Ubuntu first.' >&2; exit 1; }
command -v timeout >/dev/null
out=${1:-H20-evidence-$(date -u +%Y%m%dT%H%M%SZ)}
mkdir -- "$out" # refuse to overwrite an existing evidence directory
adb get-state | grep -qx device
capture() {
  local name=$1 command=$2
  if timeout 45 adb shell "$command" >"$out/$name" 2>"$out/$name.stderr"; then
    printf '%s\tOK\n' "$name" >>"$out/STATUS.tsv"
  else
    printf '%s\tFAILED_OR_UNAVAILABLE\n' "$name" >>"$out/STATUS.tsv"
  fi
}
capture identity.txt 'uname -a; id; for p in ro.hardware ro.board.platform ro.product.board ro.product.cpu.abi ro.product.cpu.abilist ro.product.cpu.abilist64 ro.zygote ro.build.version.release ro.build.version.sdk ro.treble.enabled ro.vndk.version ro.boot.verifiedbootstate ro.boot.vbmeta.device_state ro.boot.flash.locked; do echo "$p=$(getprop "$p")"; done'
capture device-tree.txt 'for p in compatible model; do echo "=== $p"; cat /proc/device-tree/$p 2>/dev/null | tr "\000" "\n"; done'
capture resources.txt 'cat /proc/meminfo; cat /proc/partitions; df -k /system /vendor /data; cat /sys/block/mmcblk0/size; cat /sys/block/mmcblk0/device/name'
capture drivers.txt 'cat /proc/modules; ls -l /vendor/lib /vendor/lib64 /vendor/lib/modules /vendor/firmware; ls -l /sys/bus/platform/drivers; ls -l /sys/bus/sdio/devices/*/driver /sys/bus/usb/devices/*/driver; cat /sys/bus/sdio/devices/*/uevent'
capture partitions.txt 'ls -l /dev/block/by-name /dev/block/platform/*/by-name /dev/block/mapper; cat /proc/mounts'
capture vintf.txt 'for d in /vendor/etc/vintf /odm/etc/vintf /system/etc/vintf; do echo "=== $d"; find "$d" -type f -name "*.xml" -exec cat {} \;; done'
capture hal.txt 'lshal'
capture super.txt 'lpdump'
capture input.txt 'cat /proc/bus/input/devices; ls -l /vendor/usr/keylayout /system/usr/keylayout'
capture thermal.txt 'for f in /sys/class/thermal/thermal_zone*/type /sys/class/thermal/thermal_zone*/temp; do echo "$f"; cat "$f"; done'
# Raw logs and full getprop are deliberately excluded (identifiers/network data).
if timeout 45 adb exec-out cat /sys/firmware/fdt >"$out/stock.dtb" 2>"$out/stock.dtb.stderr"; then
  printf 'stock.dtb\tCAPTURED_NEEDS_MAGIC_CHECK\n' >>"$out/STATUS.tsv"
else
  printf 'stock.dtb\tUNAVAILABLE\n' >>"$out/STATUS.tsv"
fi
cat >"$out/READ_BEFORE_SHARING.txt" <<'NOTE'
Keep this folder private until reviewed. HAL, mount and device information may
contain identifiers. No automatic redaction is claimed. Missing/failed commands
are evidence gaps, not proof that hardware features are absent. This script did
not enable root; permissions are those of the existing adb session.
NOTE
printf 'Saved locally: %s\nReview STATUS.tsv and privacy note before sharing.\n' "$out"
