#!/bin/sh
# Run the frozen binary against a throwaway project.
#
# The test suite imports ddb as a package, so nothing else exercises what pyinstaller bundles: two startup bugs
# (missing binaryornot data files, missing cookiecutter VERSION.txt) already shipped unnoticed this way.
set -e

if [ -z "$1" ]; then
	echo "usage: $0 <path to the ddb binary>" >&2
	exit 2
fi

ddb="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
# BSD mktemp, on macOS, wants an explicit template.
project="$(mktemp -d 2>/dev/null || mktemp -d -t ddb-smoke)"

# Reaches api.github.com, which covers the certificate bundle pyinstaller has to ship.
"$ddb" --version
"$ddb" features

cd "$project"
cat > ddb.yml <<-'EOF'
	core:
	  project:
	    name: smoke
	  check_updates: false
EOF

"$ddb" configure
"$ddb" config > /dev/null
"$ddb" download

test -f .gitignore

echo "Smoke test passed: $ddb"
