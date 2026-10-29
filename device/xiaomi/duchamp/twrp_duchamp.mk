$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota.mk)
$(call inherit-product, vendor/twrp/config/common.mk)
$(call inherit-product, $(LOCAL_PATH)/device.mk)

PRODUCT_DEVICE := duchamp
PRODUCT_NAME := twrp_duchamp
PRODUCT_BRAND := POCO
PRODUCT_MODEL := POCO X6 Pro
PRODUCT_MANUFACTURER := Xiaomi
