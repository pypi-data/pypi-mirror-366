#!/bin/bash
# Setup script for portaudio with Nix

# Set portaudio paths for pyaudio installation
export PORTAUDIO_PATH="/nix/store/07zbxmhjj5rzilcc4l0dh8ya14gr4br4-portaudio-190700_20210406"
export CFLAGS="-I${PORTAUDIO_PATH}/include"
export LDFLAGS="-L${PORTAUDIO_PATH}/lib"
export LD_LIBRARY_PATH="${PORTAUDIO_PATH}/lib:${LD_LIBRARY_PATH}"
export DYLD_LIBRARY_PATH="${PORTAUDIO_PATH}/lib:${DYLD_LIBRARY_PATH}"

echo "PortAudio environment configured:"
echo "  PORTAUDIO_PATH: ${PORTAUDIO_PATH}"
echo "  CFLAGS: ${CFLAGS}"
echo "  LDFLAGS: ${LDFLAGS}"
echo ""
echo "You can now install pyaudio with:"
echo "  pip install pyaudio"
echo "Or install gensay with ElevenLabs support:"
echo "  pip install -e ."