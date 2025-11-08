#! /bin/bash

# Get latest release info
REPO="numediart/MBROLA"
RELEASE=$(curl --silent "https://api.github.com/repos/${REPO}/releases/latest" | grep -Po "(?<=\"tag_name\": \").*(?=\")")
echo "Fetching latest MBROLA release $RELEASE"

# Check if MBROLA exists
DEST="/usr/bin/mbrola"
if [ -f "$DEST" ]; then
  while true; do
    read -p "$DEST already exists. Do you want to replace the current installation? [Y/N]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes [Y] or no [N].";;
      esac
  done
fi

# Download and unzip MBROLA
FNAME="mbrola-${RELEASE}.tar.gz"
curl -L https://github.com/${REPO}/archive/refs/tags/${RELEASE}.tar.gz > ${FNAME}
tar -xvf ${FNAME}

# Compile MBROLA
cd MBROLA-${RELEASE}
make
cp Bin/mbrola /usr/bin/mbrola

# Download voices
VOICES_REPO="numediart/MBROLA-voices"
if [ -d "voices" ]; then
  rm -rf voices
fi
git clone "https://github.com/${VOICES_REPO}" voices
cp -r voices/data/ /usr/share/mbrola/

echo "Installation successful!"