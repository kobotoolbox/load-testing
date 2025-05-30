#!/bin/bash
set -e

if [ -n "$IS_MASTER" ]; then
  TAGS_OPTION=""
  if [ -n "$LOCUST_TAGS" ]; then
    TAGS_OPTION="--tags $LOCUST_TAGS"
  fi
  echo "Starting master with these options: --host $SCHEME://$KPI_SUBDOMAIN.$DOMAIN_NAME $TAGS_OPTION"
  exec locust --master --host $SCHEME://$KPI_SUBDOMAIN.$DOMAIN_NAME $TAGS_OPTION
else
  echo "Starting worker with these options: --master-host=$MASTER_IP"
  exec locust --worker --master-host="$MASTER_IP"
fi
