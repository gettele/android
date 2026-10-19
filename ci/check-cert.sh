#!/usr/bin/env bash
# check-cert.sh APK PINNED_FILE APKSIGNER
# fails unless the apk verifies and is signed by exactly the pinned certificate (sha256, hex with or without colons)
set -euo pipefail

apk=$1
pinned=$(tr -d ':[:space:]' < "$2" | tr 'A-F' 'a-f')
apksigner=$3

if ! [[ "$pinned" =~ ^[0-9a-f]{64}$ ]]; then
  echo "::error::$2 doesn't hold a sha256 certificate digest"
  exit 1
fi
output=$("$apksigner" verify --print-certs "$apk")
signers=$(sed -n 's/^Signer #[0-9]* certificate SHA-256 digest: //p' <<< "$output")
if [ "$signers" != "$pinned" ]; then
  echo "::error::the apk is signed by ${signers:-nobody}, expected $pinned"
  exit 1
fi
echo "signed by the pinned certificate $pinned"
