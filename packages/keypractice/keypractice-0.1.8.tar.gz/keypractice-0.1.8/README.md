# Maintenance Scripts

## Publishing to PyPI

1. Make sure you have an API token from https://pypi.org/account/ (starts with `pypi-`).
2. Run the script:
   ```sh
   bash maintenance/publish_pypi.sh
   ```
   - You will be prompted for your API token if not set as the `PYPI_API_TOKEN` environment variable.
   - The script will build and upload your package to PyPI.

## Publishing to the AUR

1. Update `maintenance/PKGBUILD`:
   - Set your name/email as Maintainer.
   - Set the correct `pkgver` and update the `url` to your GitHub repo.
   - Download the release tarball and update the `sha256sums` (use `sha256sum` on the tarball).
2. Create a new directory and copy `PKGBUILD` into it:
   ```sh
   mkdir keypractice-aur && cp maintenance/PKGBUILD keypractice-aur/
   cd keypractice-aur
   makepkg
   ```
3. If the package builds, upload it to the AUR:
   - Create a new package at https://aur.archlinux.org/
   - Push your PKGBUILD and `.SRCINFO` to the AUR git repo as instructed by the AUR web interface.

---

**Never share your PyPI API key publicly!** 