[app]
title = Счётчик трат
package.name = schetchiktrat
package.domain = org.trat
source.dir = .
source.include_exts = py,png
version = 1.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
