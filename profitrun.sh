#!/bin/bash

ROOT_DIR=$(cd $(dirname $0) && pwd )
echo $ROOT_DIR
cd $ROOT_DIR

python main.py --adcostprofit

