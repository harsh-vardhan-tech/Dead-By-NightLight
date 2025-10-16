# Build Android APK Online (GitHub Actions)

This repository is configured to build an Android APK entirely online using GitHub Actions. You do NOT need to install Android Studio, SDK/NDK, Java, or Buildozer on your Windows 11 machine.

## How to build a debug APK

1. Push your latest code to the `main` branch (or open this repo on GitHub).
2. Go to the **Actions** tab.
3. Click **Build Android APK (Kivy/Buildozer)**.
4. Click **Run workflow** and confirm.
5. Wait ~15–30 minutes. When it finishes, scroll to the bottom of the run page.
6. Under **Artifacts**, download the `apk` artifact. Inside you will find your debug APK from the `bin/` folder.

## Customize buildozer.spec

Edit `buildozer.spec` to match your app:
- `title`, `package.name`, `package.domain`, `version`
- `orientation` and `fullscreen`
- `requirements`: default is `python3,kivy`. If you use KivyMD, set `python3,kivy,kivymd`.
- `source.include_exts`: add any extra asset extensions you need.
- If your entry file is not `main.py`, set `entrypoint` accordingly.

Notes:
- Android builds work best with Kivy-based apps. If your game is pure `pygame`, Android support is not reliable. Consider porting to Kivy for a smoother mobile build.

## Common build issues

- Java/JDK: The workflow action handles Java automatically (JDK 17). No local setup needed.
- SDK/NDK mismatch: We pin `android.sdk = 33` and `android.ndk = 25c`, which are widely compatible on CI.
- Gradle memory: If you see memory errors, open `buildozer.spec` and uncomment `android.gradle_args = -Xmx4g`.
- Missing Python recipes: Prefer pure-Python dependencies. Native/C extensions may require python-for-android recipes.

## Release (signed) builds

Debug APKs are fine for testing. For Play Store or production, make a release build:

1. Generate a keystore on your machine (one-time):
   ```bash
   keytool -genkey -v -keystore my.keystore -alias myalias -keyalg RSA -keysize 2048 -validity 10000
   ```
2. In GitHub, go to Settings → Secrets and variables → Actions → New repository secret and add:
   - `ANDROID_KEYSTORE_BASE64`: base64-encoded content of `my.keystore`
   - `ANDROID_KEY_ALIAS`: your alias (e.g., `myalias`)
   - `ANDROID_KEYSTORE_PASSWORD`: your keystore password
   - `ANDROID_KEY_PASSWORD`: your key password (often same as keystore password)
3. Modify the workflow to add a release job (example snippet):
   ```yaml
   - name: Decode keystore
     if: ${{ github.event_name == 'workflow_dispatch' }}
     run: |
       echo "$ANDROID_KEYSTORE_BASE64" | base64 -d > my.keystore
     shell: bash
     env:
       ANDROID_KEYSTORE_BASE64: ${{ secrets.ANDROID_KEYSTORE_BASE64 }}

   - name: Build release
     uses: ArtemSBulgakov/buildozer-action@v1
     with:
       workdir: .
       command: buildozer android release

   - name: Upload release artifact
     uses: actions/upload-artifact@v4
     with:
       name: release-apk
       path: bin/*-release*.apk
   ```
4. In `buildozer.spec`, set:
   ```ini
   [android]
   android.release_keystore = my.keystore
   android.release_keystore_alias = ${ANDROID_KEY_ALIAS}
   android.release_keystore_password = ${ANDROID_KEYSTORE_PASSWORD}
   android.release_keyalias_password = ${ANDROID_KEY_PASSWORD}
   ```

That's it — trigger the workflow and download your signed release APK from the artifact.
