#!/bin/bash

wget https://raw.githubusercontent.com/golemfactory/golem/develop/apps/entrypoint.sh
cp entrypoint.sh torch_image/
cp entrypoint.sh spearmint_image/
rm entrypoint.sh

