[app]
# Visible app name on the device
title = Dead By NightLight
# Package name (no spaces, only letters and numbers)
package.name = nightlight
# Reverse-DNS style domain (change to your own if you want)
package.domain = org.harshvardhan

# Where your source code lives. '.' means repository root
source.dir = .
# File extensions to include in the APK
source.include_exts = py,kv,png,jpg,ttf,otf,wav,ogg,mp3,json

# App version
version = 0.1.0
# Orientation: portrait, landscape or all
orientation = landscape
# Fullscreen app
fullscreen = 1

# Python and framework requirements. Add more separated by commas.
# For KivyMD, use: python3,kivy,kivymd
# If you use other pure-Python libraries, add them here as well.
requirements = python3,kivy

# The main entry point for the app is in the code/ subdirectory
source.include_patterns = code/*.py,assets/*
entrypoint = code/main.py

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Target Android SDK/NDK versions known to work on CI
android.sdk = 33
android.ndk = 25c
android.archs = arm64-v8a,armeabi-v7a
# Use the master branch of python-for-android by default
p4a.branch = master

# If you hit Gradle memory issues, uncomment:
# android.gradle_args = -Xmx4g
