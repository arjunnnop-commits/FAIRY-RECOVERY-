LOCAL_PATH := $(call my-dir)

PRODUCT_PLATFORM := mt6897
PRODUCT_USE_DYNAMIC_PARTITIONS := true

AB_OTA_UPDATER := true
AB_OTA_PARTITIONS += boot init_boot vendor_boot dtbo vbmeta vbmeta_system vbmeta_vendor system system_ext product vendor

PRODUCT_PACKAGES += \
    update_engine update_engine_sideload update_verifier \
    android.hardware.boot@1.2-impl-recovery android.hardware.boot@1.2-impl \
    android.hardware.fastboot@1.1-impl-mock

PRODUCT_PACKAGES_DEBUG += update_engine_client
