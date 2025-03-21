#!/bin/sh

kill $(head -n 1 ladeRegler.log)
nohup /data/home/root/ladeRegler.py > /data/home/root/ladeRegler.log&
