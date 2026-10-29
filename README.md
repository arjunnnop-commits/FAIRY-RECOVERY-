# Fairy Recovery - POCO X6 Pro (duchamp, MT6897)

## 1. Phone se SAHI images dump karo (Termux, root, active slot)
    su
    S=$(getprop ro.boot.slot_suffix)
    dd if=/dev/block/by-name/boot$S        of=/sdcard/boot.img
    dd if=/dev/block/by-name/vendor_boot$S of=/sdcard/vendor_boot.img
    dd if=/dev/block/by-name/init_boot$S   of=/sdcard/init_boot.img

## 2. Prebuilt nikalo (Termux: pkg install python git)
    python3 tools/extract.py /sdcard/boot.img /sdcard/vendor_boot.img device/xiaomi/duchamp/prebuilt
"OK: kernel aur modules match karte hain" aana chahiye.

## 3. Push + Build
    git add -A && git commit -m init && git push
GitHub -> Actions -> "Build Fairy Recovery" -> Run workflow. Output artifact me `vendor_boot.img`.

## 4. Test
    fastboot flash vendor_boot_a vendor_boot.img   (stock backup pehle rakho)

TODO flags: BOARD_SUPER_PARTITION_SIZE, TW_BRIGHTNESS_PATH / TW_MAX_BRIGHTNESS, OF_STATUS_H.
