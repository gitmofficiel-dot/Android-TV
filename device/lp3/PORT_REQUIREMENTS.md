# LP3 hardware port requirements — not buildable board support
The accompanying JSON is derived from the stock DTB using the included bounded
FDT reader. It records raw cells, selected strings, phandle references and GPIO
annotations. It is evidence, NOT a DTS overlay or a set of safe voltage settings.
Min/max regulator ranges are bounds, not observed operating voltages.

## Facts to preserve and verify across BSP versions
- DT PMIC compatible x-powers,axp1530, I2C address 0x36.
- PMIC dcdc2 is referenced by CPU supply in the stock tree; resolve clock/OPP
  dependencies separately. Do not import another board's voltage-frequency table.
- Wi-Fi wlan_regon is PG18; wlan_hostwake is PG15 in the stock Allwinner GPIO
  encoding. SDIO busnum=1; module actually loaded is SSV6x5x. Do not substitute
  UWE5622/BCM based on bundled alternate firmware files.
- Stock eMMC node /soc@03000000/sdmmc@04022000: 8-bit bus, max-frequency=50000000.
  card2 boot parameters name controller2, 8 lines, sdc_io_1v8=1. This does NOT
  authorize changing hardware voltages, bus speed or U-Boot DRAM setup.
- USB0: stock DT usb_port_type=1 (host); runtime USB0 Device setting produces ADB.
  Preserve and investigate the runtime switch; do not freeze USB0 into host-only
  just because a reference board uses host-only A-A flashing.
- Remote FE01 commands for six buttons measured; matched prospective decoder
  emits standard Linux key codes. Stock daemon/keylayout use another convention.
- Sleep/wake power chain must be validated independently; functioning normal
  remote input does not establish BL31/U-Boot wake behavior.

## Build-critical missing evidence/source work
DDR training/bootstrap values, matching bootloader source/format, regulator OPP
selection, pin controller binding translation 4.9->5.4, USB role switching,
SSV5.4 buildable source, Mali kernel/userspace ABI pairing, display/video/audio
userspace dependencies, target FCM/HAL implementation, recovery proof.

## Reference source result
BPI-SINOVOIP/BPI-H618-Android12 contains inspectable kernel5.4.125, PMIC AXP1530
code in drivers/mfd/axp2101.c, and board DTS examples with AXP1530/eMMC.
The M4Zero board is a comparison candidate, not selected as compatible.
README requires additional oversized files outside GitHub: a clone alone is not
claimed complete. Full repository not downloaded. Source licenses and complete
repository commit must be pinned before importing code into a build.

The guessed kernel path drivers/net/wireless/ssv6x5x/Makefile returned 404 and
repository code search found no result. SSV5.4 source location remains unresolved;
this does not prove its absence from the full SDK or partner source archives.
