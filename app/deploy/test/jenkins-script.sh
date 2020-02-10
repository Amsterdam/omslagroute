#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

DIR="$(dirname $0)"

COMMIT_HASH=$(git rev-parse HEAD)

dc() {
	docker-compose -p ${COMMIT_HASH}_omslagroute_test -f ${DIR}/docker-compose.yml $*
}

trap 'dc stop; dc rm --force; dc down' EXIT

dc stop
dc rm --force
dc down
dc pull
dc build

dc up -d database

dc run --rm tests

dc stop
dc rm --force
dc down
