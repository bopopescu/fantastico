#!/bin/bash

PATH=/bin:/usr/bin:/usr/sbin

VERSION=$FANTASTICO_VERSION
WORKDIR=`pwd`

if [ -z $VERSION ]; then
	echo "You must provide a fantastico version to package."
	exit 1
fi

# Publish release code.
echo "Create release tag $VERSION"
git tag -a v$VERSION -m "Fantastico version $VERSION released."

if [ $? -gt 0 ]; then
	exit $?
fi

git push origin --tags

# Publish release documentation.
echo "Create release doc tag $VERSION"
cd ../fantastico-doc
git tag -a v$VERSION-doc -m "Fantastico doc version $VERSION released."
git push origin --tags

if [ $? -gt 0 ]; then
	exit $?
fi


# Publish Fantastico on PyPi.
cd $WORKDIR
echo "Publishing Fantastico $VERSION on PyPi."
./setup.py register clean sdist upload

if [ $? -gt 0 ]; then
	exit $?
fi

echo "Fantastico $VERSION released successfully."