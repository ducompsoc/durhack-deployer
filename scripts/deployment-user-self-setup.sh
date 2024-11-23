#!/bin/bash

# setup nvm
export PROFILE="/dev/null"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

NVM_BASHRC="$HOME/.bashrc.d/nvm.bashrc"

cat <<EOF > "$NVM_BASHRC"
# ~/.bashrc.d/nvm.bashrc

grep -F a <<< "$-"; allexport_unset=$?
((allexport_unset)) && set -o allexport

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

((allexport_unset)) && set +o allexport
EOF
# setup nvm end

# setup pnpm
curl -fsSL https://get.pnpm.io/install.sh | sh -

PNPM_ENV_START_LINE_NUMBER=$(grep -Fxn "# pnpm" ~/.bashrc | cut -f1 -d:)
PNPM_ENV_END_LINE_NUMBER=$(grep -Fxn "# pnpm end" ~/.bashrc | cut -f1 -d:)
PNPM_ENV=$(sed -n "$((PNPM_ENV_START_LINE_NUMBER+1)),$((PNPM_ENV_END_LINE_NUMBER-1))"p ~/.bashrc)

cp ~/.bashrc ~/.bashrc.save
sed -i "$((PNPM_ENV_START_LINE_NUMBER-1)),$PNPM_ENV_END_LINE_NUMBER"d ~/.bashrc

PNPM_BASHRC="$HOME/.bashrc.d/pnpm.bashrc"

cat <<EOF > "$PNPM_BASHRC"
# ~/.bashrc.d/pnpm.bashrc

EOF
printf "%s\n" "$PNPM_ENV" >> "$PNPM_BASHRC"
# setup pnpm end

# reload ~/.profile
# shellcheck disable=SC1090
source ~/.profile

# setup node
nvm install --lts
nvm alias default
# setup node end

# setup pm2
pnpm i -g pm2@latest
pm2 startup systemd | tail -1 > ~/create-pm2-service.sh
chmod a+x ~/create-pm2-service.sh  # this script will be executed as root from the add-deployment-user script, then deleted
# setup pm2 end
