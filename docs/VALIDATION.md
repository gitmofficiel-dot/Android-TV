# Validation — 2026-10-24
Executed in Work:
- bash -n scripts/COLLECT_READ_ONLY.sh: exit 0.
- python3 -m unittest discover -s tests -v: four tests passed: valid synthetic GPT, bad header CRC, overlapping partitions, absent/truncated GPT.

Not executed: collector against an Android device; real eMMC audit; AOSP build; boot; hardware tests; restoration.
The collector uses bounded adb calls and no device mutation commands. Local output remains private and requires review before sharing. Synthetic fixtures do not validate the stock image.
