#!/usr/bin/env bash
nixprofile=${HOME}/.nix-profile

export PATH="$nixprofile/bin:${PATH}"
export LD_LIBRARY_PATH="$nixprofile/lib:${LD_LIBRARY_PATH}"
export NIX_LDFLAGS="-L$nixprofile/lib -L$nixprofile/lib/pkgconfig:${NIX_LDFLAGS}"
export NIX_CFLAGS_COMPILE="-I$nixprofile/include -I$nixprofile/include/sasl:${NIX_CFLAGS_COMPILE}"
export PKG_CONFIG_PATH="$nixprofile/lib/pkgconfig:${PKG_CONFIG_PATH}"
export PYTHONPATH="$nixprofile/lib/python2.7/site-packages:${PYTHONPATH}"
# export PS1="py27 $PS1"

export INCLUDE="$nixprofile/include:$INCLUDE"
export LIB="$nixprofile/lib:$LIB"
export C_INCLUDE_PATH="$nixprofile/include:$C_INCLUDE_PATH"
export LD_RUN_PATH="$nixprofile/lib:$LD_RUN_PATH"
export LIBRARY_PATH="$nixprofile/lib:$LIBRARY_PATH"
export CFLAGS=$NIX_CFLAGS_COMPILE
export LDFLAGS=$NIX_LDFLAGS

"$@"
