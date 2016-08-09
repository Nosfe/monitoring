#!/bin/bash
base_dir=$(readlink -f $(dirname ${0}))

echo "# Stopping running programs..."
sudo pkill -u root -f 'monitoring_daemon'
echo "# Done."
