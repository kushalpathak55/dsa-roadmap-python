# Deploying the mobile app

The native iOS/Android projects here are a thin Capacitor shell - the
WebView just loads the live deployed app (`capacitor.config.json`'s
`server.url`), the same one at https://dsa-roadmap-python.onrender.com. No
separate backend or build step for the web content itself.

## iOS -> TestFlight / App Store

Everything on the CI side is already wired up
(`.github/workflows/ios-release.yml`, `ios/App/fastlane/Fastfile`) - it just
needs these one-time steps in the Apple Developer / App Store Connect portals
(developer.apple.com / appstoreconnect.apple.com), which only you can do
since they require your Apple ID login.

### 1. Register the App ID
Developer portal -> **Certificates, IDs & Profiles** -> **Identifiers** -> **+**
- Bundle ID: `com.kushalpathak.dsaroadmap` (explicit, not wildcard)
- Capabilities: none needed to start

### 2. Create a Distribution Certificate
**Certificates, IDs & Profiles** -> **Certificates** -> **+** -> **Apple Distribution**
- Follow the CSR (Certificate Signing Request) steps - on Windows without
  Keychain Access, the easiest route is generating the CSR through the portal
  itself or asking me to help generate one via `openssl` locally.
- Download the resulting `.cer`, then export it as a **`.p12`** with a
  password you choose (this normally happens in Keychain Access on a Mac -
  since you don't have one, let me know once you're at this step and I'll
  walk through the Windows-side alternative, e.g. using `openssl` to combine
  the cert + private key into a `.p12`).

### 3. Create a Provisioning Profile
**Certificates, IDs & Profiles** -> **Profiles** -> **+** -> **App Store Connect** (distribution)
- App ID: the one from step 1
- Certificate: the one from step 2
- Give it a name you'll remember - you'll need this **exact name** for a secret below.
- Download the `.mobileprovision` file.

### 4. Create an App Store Connect API Key
**App Store Connect** -> **Users and Access** -> **Integrations** -> **App Store Connect API** -> **+**
- Role: **App Manager** (or Admin)
- Download the `.p8` key file **immediately** - Apple only lets you download it once.
- Note the **Key ID** and **Issuer ID** shown on that page.

### 5. Create the app record in App Store Connect
**App Store Connect** -> **My Apps** -> **+** -> **New App**
- Platform: iOS
- Name: "DSA Roadmap" (or whatever you'd like it listed as - must be unique across the App Store)
- Bundle ID: select the one from step 1
- SKU: any unique string, e.g. `dsa-roadmap-001`
This step must happen before the first TestFlight upload will succeed - the
API can't upload a build to an app that doesn't exist yet.

### 6. Add these as GitHub repo secrets
Repo -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**

| Secret name | Value |
|---|---|
| `IOS_CERTIFICATE_P12_BASE64` | `.p12` from step 2, base64-encoded |
| `IOS_CERTIFICATE_PASSWORD` | the password you chose when exporting the `.p12` |
| `IOS_PROVISIONING_PROFILE_BASE64` | `.mobileprovision` from step 3, base64-encoded |
| `IOS_PROVISIONING_PROFILE_NAME` | the exact profile name from step 3 |
| `ASC_KEY_ID` | Key ID from step 4 |
| `ASC_ISSUER_ID` | Issuer ID from step 4 |
| `ASC_KEY_CONTENT_BASE64` | the `.p8` file from step 4, base64-encoded |
| `FASTLANE_APPLE_ID` | your Apple ID email |
| `APPLE_TEAM_ID` | your 10-character Team ID (top-right of the developer portal) |

To base64-encode a file on Windows (PowerShell):
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("certificate.p12")) | Set-Clipboard
```
This copies the value straight to your clipboard, ready to paste into the GitHub secret field.

### 7. Run the workflow
Repo -> **Actions** tab -> **iOS TestFlight release** -> **Run workflow**.
Once it succeeds, the build shows up in **App Store Connect -> TestFlight**
within a few minutes (Apple processes it server-side after upload).

## Android -> Play Store

Not yet wired up in CI (no priority set on this yet) - but buildable entirely
on this Windows machine once Android Studio is installed:
```
cd mobile
npx cap open android
```
Then build/run from Android Studio directly, or `./gradlew assembleDebug`
from `mobile/android` for an installable APK without any store account at
all. Ask if/when you want the Play Store side (signing keystore + a Google
Play Console listing, $25 one-time developer fee) set up too.
