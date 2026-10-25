# T95 Android12 donor → H20 Pro LP3: offline port experiment

Status: downloaded, decompressed and inspected. An incomplete DT candidate was
created and checked offline. NO complete H20 firmware was built or booted.
The Android16 goal remains separate; this donor is Android12.

## Exact downloaded image
Upstream: https://github.com/well83/t95-h616-android12/releases/tag/axp313-final
Asset: T95-AXP313-eMMC-a12-final-user.img.xz
Compressed: 653115936 bytes, SHA256
`de6d272e10297fbe6332734845966da5b92bc660c92bcff318cb17552aa72126`.
Decompressed IMAGEWTY v3 container:1855805440 bytes, SHA256
`35884d993ae67ae3cb2b76de7adf1710bba7546c3890300d7c4f4ef7278349b7`.
The XZ decoder verified the stream while decompressing. Container lists45 entries.
Container entry checksums/signatures were not independently all verified.

Source tag resolves to9f5d7ff1c5ca92f9467e2f2718225a665dcd4c80.
The release source folder is not a byte-for-byte description of the packed image:
inspect extracted files rather than assuming source layout matches release layout.
Reader: apritzel/sunxi-fw @2e2aaf484efe2fc0218561d2c4f231f7fd76fb34.
Local libfdt built from dgibson/dtc @f99e3af0ecb67a9085478a9b8ddbcc25aa64931d.
No upstream signing keys were obtained, changed or bypassed.

## Actual packed image findings
- `boot.fex`:64MiB, Android boot header v3. Kernel23701512 bytes and
  generic ramdisk13229968 bytes: their sum alone exceeds stock H20 boot32MiB.
- `vendor_boot.fex`:32MiB, VNDRBOOT header v3. H20 stock has no matching
  named vendor_boot partition. An Android12 boot-chain/layout migration is required.
- Extracted partition file uses A/B boot and vendor_boot, plus3GiB super.
  H20 stock partition layout must not be overwritten by this donor layout.
- Both toc0/toc1 and nonsecure-format components are bundled.
  Extracted sys_config sets `burn_secure_mode=1`. Do not execute donor flashing
  tools on H20: it could permanently change SoC secure mode. A different recovery
  and packaging plan must be validated first. Changing a text flag alone is not
  proof that every flasher/boot-stage permanent write has been removed.
- Extracted DT identifies T95 H616 AXP313A and uses x-powers,axp1530 at0x36,
  matching H20 stock DT identity at this level. Rail values remain unverified.
- Despite the eMMC-labelled release, packed DT has sdc2 disabled and NAND enabled.
  Upstream boot-stage runtime fixups may account for this; not investigated yet.
- Wi-Fi GPIOs PG18/PG15 match stock wiring evidence. The donor BCM driver is not
  H20 SSV6x5x. The ARM64 stock4.9 module cannot simply load into a5.4 kernel.
- FE01 wake address already exists in donor DT; full Android navigation mapping,
  USB0 ADB role switching, media/GPU HALs and sleep remain untested on H20.

## Changes actually generated
`scripts/prepare_t95_dtb.c` uses libfdt to edit a regular offline DT file:
1. Mark model as H20 Pro LP3 EXPERIMENTAL INCOMPLETE.
2. Enable sdc2 and cap it at50MHz, matching captured H20 stock maximum.
3. Disable NAND to avoid conflicting eMMC pin use.
4. Disable unresolved Bluetooth and btlpm.
It deliberately does not copy donor PMIC/DDR settings into a bootloader or alter
voltages. The remaining donor settings are inherited and are NOT validated H20
settings. Preserving them does not make them compatible.

Input DT SHA256:0a657fd232a6a2c094b7707cc99d3fdcc6ca5aa9fae38c28c778e3e41c444d8f.
The workflow verifies this exact input. The C tool additionally checks expected
model, eMMC frequency and state before modifying anything; other donor releases
are not supported. It refuses an existing output path and malformed FDT input.

Executed locally: strict C compilation; libfdt structural check; independent
Python parser verified exactly5 changed nodes,6 changed properties and all other
properties preserved; overwrite and malformed-input rejection passed.
No DTS kernel-binding validation, electrical validation or hardware boot test
was performed. DT candidate alone is not a boot image or flashable firmware.

## Reproducible GitHub job
`.github/workflows/donor-analysis.yml` downloads the pinned release, verifies both
hashes, builds the pinned container reader, extracts the DT and creates/checks the
same incomplete candidate. Its artifact is explicitly NOT-FIRMWARE. The workflow
performs no packaging or flashing and never runs vendor boot/flashing binaries.
Host test success is not proof of Android boot or hardware compatibility.

## Required before any H20 firmware image
Validated H20 DDR/PMIC configuration and boot-chain plan without permanent writes;
H20 partition-compatible boot/vendor_boot strategy; rebuilt SSV driver/firmware
integration; GPU/media/HAL matching; complete IR mapping; USB0 switching; full
Android product build, signature chain, recovery validation and real-device tests.
Android16 additionally needs an Android16-compatible vendor/FCM migration.
