# Evidence update
Authoritative corrections to the initial intake docs:
- Stock kernel is ARM64: CONFIG_ARM64=y, CONFIG_64BIT=y, CONFIG_COMPAT=y;
  ARM64 Image magic in boot/recovery independently confirms this.
- Android userspace/init and sampled HAL libraries are ARM32. ro.zygote=zygote32.
- DT reports allwinner,h616 and x-powers,axp1530 at address 0x36. Physical chip
  marking not independently confirmed. Merely listing axp2101 drivers was not proof.
- FE01 remote path measured: scan event -> stock multi_ir -> uinput key event.
  Mouse-mode interception was reproduced and disabled; six buttons then emitted
  down/up. Mapping names KEY_R/T/Y/U/I/3 are Linux labels for stock daemon codes.
- multi_ir and libmultiirservice are ARM32 with Binder/private framework links.
- Full collection archive SHA256 matches:
  c9c0291d2701c495b724498b6c3eed3f73fe4e3eaee2764f91d17d80f76c851a
  125366119 bytes, 907 regular files fully read. No proprietary binaries included
  in this engineering package.
- All 17 live partition starts/sizes match the backup audit. This does not prove
  live data contents equal backup contents or that the backup can be restored.
- Stock SELinux getenforce=Permissive. Bootloader identity unknown. AVB headers
  have algorithm IDs 2/1/1 and flags0; descriptors parse within the files.
  No cryptographic verification or inference of unlocked bootloader.
- SSV module is /vendor/modules/ssv6x5x.ko (not /system/lib/modules), ARM64,
  vermagic 4.9.170 SMP preempt mod_unload modversions aarch64.
- Vendor firmware inventory contains many alternative chips; presence does not
  imply installed hardware. Bluetooth vendor property is NULL, still unresolved.

## New validation
Host C compiler with -std=c11 -Wall -Wextra -Werror -pedantic: successful.
FE01 decoder tested against six observed press/release command pairs, repeated
down, foreign address, invalid flag/command, mismatched release, key switching
and reset. No Android/device execution of decoder. No service or full ROM built.
