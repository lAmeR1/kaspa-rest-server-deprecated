#!/bin/sh
PUSH=$1

DOCKER_REPO=supertypo/kaspa-rest-server

BUILD_DIR="$(dirname $0)"
REPO_URL="https://github.com/lAmeR1/kaspa-rest-server.git"
REPO_DIR="$BUILD_DIR/work/kaspa-rest-server"

set -e

if [ ! -d "$REPO_DIR" ]; then
  git clone "$REPO_URL" "$REPO_DIR"
  echo $(cd "$REPO_DIR" && git reset --hard HEAD~1)
fi

(cd "$REPO_DIR" && git pull)
tag=$(cd "$REPO_DIR" && git log -n1 --format="%cs.%h")

docker build --pull --build-arg REPO_DIR="$REPO_DIR" -t $DOCKER_REPO:$tag "$BUILD_DIR"
docker tag $DOCKER_REPO:$tag $DOCKER_REPO:latest
echo Tagged $DOCKER_REPO:latest

if [ "$PUSH" = "push" ]; then
  docker push $DOCKER_REPO:$tag
  docker push $DOCKER_REPO:latest
fi

