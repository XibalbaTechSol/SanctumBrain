#!/bin/bash

# 1. Back up the original configuration
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# 2. Disable Root Login and Password Authentication
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config

# 3. Verify the configuration for errors
sshd -t

# 4. If no errors, restart the SSH service
if [ $? -eq 0 ]; then
    systemctl restart ssh
    echo "SUCCESS: Server locked down."
    echo "Root login: DISABLED"
    echo "Password login: DISABLED"
else
    echo "ERROR: Configuration error detected. Reverting to backup."
    cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
fi
