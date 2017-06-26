#!/usr/bin/env bash
set -e

cat ./conf.json

echo cat ./conf.json | jq '.admin'

exit 0

ADMIN_EXP=$(echo $ADMIN_CREDENTIALS | sed -e 's/\(.\)/send -- "\1"\nexpect -exact "*"\n/g')
echo "ADMIN_EXP = ${ADMIN_EXP}"

echo "BEFORE"
cat ./Tests/scripts/installer_commands-centos.exp
sed -i 's/<PASSWORD>/${ADMIN_EXP}/g' ./Tests/scripts/installer_commands-centos.exp

echo "AFTER"
cat ./Tests/scripts/installer_commands-centos.exp