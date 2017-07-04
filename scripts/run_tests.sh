echo "start content tests"

SECRET_CONF_PATH=$(cat secret_conf_path)
SERVER_IP=$(cat public_ip)
SERVER_URL="https://$SERVER_IP"
CONF_PATH="./Tests/conf.json"
USERNAME="admin"
PASSWORD=$(cat $SECRET_CONF_PATH | jq '.adminPassword')

# remove quotes from password
temp="${PASSWORD%\"}"
temp="${temp#\"}"
PASSWORD=$temp

IS_NIGHTLY=$(-n "${WITH_COVERAGE}")
echo "IS_NIGHTLY - $IS_NIGHTLY"

echo "Starts tests with server url - $SERVER_URL"
python ./Tests/test_content.py -u "$USERNAME" -p "$PASSWORD" -s "$SERVER_URL" -c "$CONF_PATH" -e "$SECRET_CONF_PATH" -n $IS_NIGHTLY