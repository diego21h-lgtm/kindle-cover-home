#!/bin/sh
# Standalone: shell builtins only. No mkdir, date, dirname, common/session scripts.
# Fixed destination: this test must work before any application initialization.
[ ! -L /mnt/us/coverhome-kual-test.txt ] || exit 1
printf '%s\n' 'Kindle Cover Home 0.2.1' 'BASIC_SCRIPT_ENTERED' 'BASIC_SCRIPT_COMPLETED' > /mnt/us/coverhome-kual-test.txt
