# جرد العتاد
المصدر: ملف التسليم المقروء بتاريخ 2026-10-24؛ لم نصل إلى الجهاز مباشرة.

| العنصر | الدليل المنقول | حالة التحقق الحالي |
|---|---|---|
| PCB | H20-pro-lp3-230916 / ملصق LP3-B | صورة ومراجعة مطلوبة |
| SoC | sun50iw9p1 / cupid / exdroid | الطراز الدقيق مجهول |
| CPU | 4 Cortex-A53؛ armv8l | لا يثبت سلسلة إقلاع 64 بت |
| Android | 10 / SDK29؛ ABI armeabi-v7a,armeabi | من التسليم |
| Kernel | 4.9.170 | من التسليم |
| RAM | 1934336 kB | من التسليم |
| eMMC | 7818182656 بايت؛ boot0/1 كل منهما 4194304 | لم نفحص الصورة |
| Treble/VNDK | true / 29 | لا يثبت توافق Android16 |
| Wi-Fi | SV6256P محتمل | يلزم driver/firmware |
| GPU | Mali-G31 محتمل | يلزم HAL/driver |
| PMIC/BT/IR | غير مثبتة | أدلة مطلوبة |

الأقسام المنقولة: bootloader, env, boot, super, misc, recovery, cache, vbmeta, vbmeta_system, vbmeta_vendor, metadata, private, frp, empty, media_data, Reserve0, UDISK. البدايات الفعلية غير متاحة؛ لا ننشئ partition map تخمينياً.
