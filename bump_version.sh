#!/usr/bin/env bash
# Bump project version, commit, and create a git tag.
# Usage:
#   ./bump_version.sh <major> <minor> <patch> [--push]
# Examples:
#   ./bump_version.sh 1 2 0         # Bump to 1.2.0, commit and tag (no push)
#   ./bump_version.sh 1 2 1 --push # Bump to 1.2.1, commit, tag and push tag to origin
set -e

if [ $# -lt 3 ]; then
    echo "Usage: $0 <major> <minor> <patch> [--push]"
    echo "Example: $0 1 2 0        # Bump to 1.2.0 and create tag v1.2.0"
    echo "Example: $0 1 2 0 --push # Same and push the tag to origin"
    exit 1
fi

MAJOR=$1
MINOR=$2
PATCH=$3
PUSH=false
[ "${4:-}" = "--push" ] && PUSH=true

VERSION="${MAJOR}.${MINOR}.${PATCH}"
TAG="v${VERSION}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Bumping version to ${VERSION}..."
python3 update_version.py "$MAJOR" "$MINOR" "$PATCH" || exit 1

echo "Committing..."
git add version.py org.videoteka.app.appdata.xml
git commit -m "Bump version to ${VERSION}"

echo "Creating tag ${TAG}..."
git tag -a "$TAG" -m "Release version ${VERSION}"

if [ "$PUSH" = true ]; then
    echo "Pushing commit and tag to origin..."
    git push origin HEAD
    git push origin "$TAG"
else
    echo "Done. To push the tag: git push origin ${TAG}"
fi
