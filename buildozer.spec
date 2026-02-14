[app]

# (str) Title of your application
title = Food Ordering App

# (str) Package name
package.name = foodapp

# (str) Package domain (needed for android/ios packaging)
package.domain = com.foodapp

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,pillow

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (str) Android SDK version to use
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 23b

# (bool) Use --private data storage
android.private_storage = True

# (str) Android app theme
android.theme = @android:style/Theme.NoTitleBar

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
