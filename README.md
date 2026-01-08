## Import Firmware

To include the device-specific firmware configuration, add the following line to your BoardConfig.mk:

```makefile
-include vendor/xiaomi/device-firmware/config.mk
