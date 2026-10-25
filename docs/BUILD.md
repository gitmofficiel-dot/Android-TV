# بيئة البناء
لا تنفذ repo sync على قسم Ubuntu ذي 11GB المتاحة. توثيق AOSP الحالي يحدد x86-64 Linux و400GB حرة و64GB RAM. لم نجهز مضيفاً مطابقاً، ولم ننزل شجرة AOSP.

عند توفر مضيف مناسب: اختيار tag Android16 TV صريح؛ تثبيت متطلبات ذلك الإصدار؛ تثبيت manifest ومصادر kernel/BSP بالـSHA؛ مراجعة التراخيص؛ إعداد منتج LP3 بعد تحديد العتاد؛ ثم بناء userdebug للتجارب. لا نتبع latest release لأنه قد يشير لإصدار آخر.

لا توجد BoardConfig أو lunch target في هذه الحزمة؛ إنشاؤها بقيم افتراضية سيعطي انطباع توافق زائف. مطلوب: partition offsets، kernel config/source، DTB/DTBO، boot image header، ABI vendor، HAL/VINTF، SELinux، IR keylayout، Wi-Fi/BT firmware، GPU/media blobs وتراخيصها.
