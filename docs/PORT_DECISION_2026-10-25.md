# H20 Pro LP3 port decision — 2026-10-25

## Current decision
Direct stock-vendor + Android16 system replacement is NOT a supported baseline.
The captured device manifest has target-level 4. Current AOSP FCM documentation
lists Android16 levels 6,7,8,202404,202504; level 4 is absent. This is a concrete
compatibility gate, not proof that a heavily modified custom port is impossible.
https://source.android.com/docs/core/architecture/vintf/fcm

Recommended engineering sequence: reconstruct the LP3 board on an inspectable
H618 Android12 BSP/kernel5.4 baseline, validate its vendor/hardware independently,
then assess the migration to an explicitly pinned Android16 release. Android12
is an intermediate experiment only; no replacement of the user's Android16 goal.
No BSP downloaded, full AOSP build or device boot performed.

## Candidate sources reviewed
1. https://github.com/well83/t95-h616-android12
   Reference patches + board configs, not a complete BSP or compatible LP3 ROM.
   README says official Orange Pi H618-Android12-Src is the base and the p2 board
   uses AXP1530. Review the base instead of copying T95 voltage/pin values.
2. Fetched T95 AXP313 board.dts blob SHA
   38fc2b927e7f9ac3d3b525f4dad082a79ae05d5a.
   It enables NAND and disables sdc2/eMMC, sets USB0 host, BCM-family Wi-Fi/BT,
   and IR FE02. These conflict with LP3 eMMC, working USB0 ADB, SSV Wi-Fi, FE01.
   PMIC naming similarity does not make the rest of the board interchangeable.
3. tools/t95_axp313_board_dts.py blob SHA
   1ab4b644eb6857b3f0abade0c8a81e6ace61808f.
   The script explicitly describes board-specific NAND/GPIO/OPP/PMIC changes.
4. https://github.com/YAJATapps/h618patch
   Useful OEM-versus-AOSP12 diffs, explicitly excludes longan/device/vendor.
   Not a replacement for BSP and not a patch set to apply blindly to Android16.
5. Official vendor documentation:
   https://www.orangepi.org/orangepiwiki/index.php/Orange_Pi_Zero_2W
   Search indexed H618 source/build instructions; archive not downloaded or verified.

## Remaining gates
- Obtain versioned BSP source with provenance/license and match PMIC/DDRx/GPIO,
  boot chain, USB0 role and eMMC parameters to the stock DT evidence.
- Build kernel and SSV module against the same tree/config; stock module has
  vermagic 4.9.170 aarch64 and is not a drop-in kernel5.4 module.
- Resolve GPU userspace/kernel ABI and HWC/gralloc/ION, then audio/media/CEC.
- Raise vendor compatibility by implementing required HAL versions; test using
  target checkvintf rather than merely editing manifest target-level.
- Provision x86-64 Linux build resources (400GB free/64GB RAM documented baseline).
  Neither user's nearly-full Ubuntu partition nor an unverified temporary host
  is accepted as a full build environment.
- Verify recovery route and boot security before any device write.

No flash/bootloader/security changes authorized by this report.
