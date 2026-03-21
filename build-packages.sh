#!/usr/bin/env bash
# build-packages.sh — builds verba installer packages
#
#   On Ubuntu/Debian  → produces .deb
#   On Fedora/RHEL    → produces .rpm  (requires rpm-build)
#   On macOS          → produces .dmg  (requires create-dmg: brew install create-dmg)
#
# Usage: bash build-packages.sh

set -e

VERSION="1.5.0"
ARCH="$(uname -m)"
# normalise arch names
[ "$ARCH" = "x86_64" ] && DEB_ARCH="amd64" || DEB_ARCH="$ARCH"

echo "==> Building binary with PyInstaller..."
pip install pyinstaller --quiet
pyinstaller verba-linux.spec --noconfirm

BINARY="dist/verba"

# ── detect OS ────────────────────────────────────────────────────────────────
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [ -f /etc/debian_version ]; then
    OS="debian"
elif [ -f /etc/redhat-release ] || [ -f /etc/fedora-release ]; then
    OS="redhat"
else
    echo "Unsupported OS. Build .deb/.rpm on Linux, .dmg on macOS."
    exit 1
fi

# ── .deb ─────────────────────────────────────────────────────────────────────
build_deb() {
    PKG="verba_${VERSION}_${DEB_ARCH}"
    mkdir -p "${PKG}/usr/local/bin" "${PKG}/DEBIAN"
    cp "$BINARY" "${PKG}/usr/local/bin/verba"
    chmod 755 "${PKG}/usr/local/bin/verba"
    cat > "${PKG}/DEBIAN/control" <<EOF
Package: verba
Version: ${VERSION}
Section: interpreters
Priority: optional
Architecture: ${DEB_ARCH}
Maintainer: Verba Contributors
Description: Verba — a natural English programming language interpreter
 Run .vrb scripts with: verba run yourfile.vrb
EOF
    dpkg-deb --build "${PKG}"
    echo "==> Done: ${PKG}.deb"
}

# ── .rpm ─────────────────────────────────────────────────────────────────────
build_rpm() {
    command -v rpmbuild >/dev/null || { echo "Install rpm-build: sudo dnf install rpm-build"; exit 1; }
    RPMROOT="$HOME/rpmbuild"
    mkdir -p "${RPMROOT}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    mkdir -p "${RPMROOT}/BUILDROOT/verba-${VERSION}-1.${ARCH}/usr/local/bin"
    cp "$BINARY" "${RPMROOT}/BUILDROOT/verba-${VERSION}-1.${ARCH}/usr/local/bin/verba"
    chmod 755 "${RPMROOT}/BUILDROOT/verba-${VERSION}-1.${ARCH}/usr/local/bin/verba"
    cat > "${RPMROOT}/SPECS/verba.spec" <<EOF
Name:       verba
Version:    ${VERSION}
Release:    1
Summary:    Verba — a natural English programming language interpreter
License:    MIT
BuildArch:  ${ARCH}

%description
Run .vrb scripts with: verba run yourfile.vrb

%install
mkdir -p %{buildroot}/usr/local/bin
cp ${RPMROOT}/BUILDROOT/verba-${VERSION}-1.${ARCH}/usr/local/bin/verba %{buildroot}/usr/local/bin/verba

%files
/usr/local/bin/verba
EOF
    rpmbuild -bb "${RPMROOT}/SPECS/verba.spec"
    find "${RPMROOT}/RPMS" -name "verba-*.rpm" -exec cp {} . \;
    echo "==> Done: verba-${VERSION}-1.${ARCH}.rpm"
}

# ── .dmg ─────────────────────────────────────────────────────────────────────
build_dmg() {
    command -v create-dmg >/dev/null || { echo "Install create-dmg: brew install create-dmg"; exit 1; }
    APPDIR="verba-app"
    mkdir -p "${APPDIR}"
    cp "$BINARY" "${APPDIR}/verba"
    chmod 755 "${APPDIR}/verba"
    create-dmg \
        --volname "Verba ${VERSION}" \
        --window-size 400 200 \
        --icon-size 80 \
        --app-drop-link 300 100 \
        "verba_${VERSION}_macos.dmg" \
        "${APPDIR}"
    rm -rf "${APPDIR}"
    echo "==> Done: verba_${VERSION}_macos.dmg"
}

# ── dispatch ─────────────────────────────────────────────────────────────────
case "$OS" in
    debian) build_deb ;;
    redhat) build_rpm ;;
    macos)  build_dmg ;;
esac
