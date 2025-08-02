#!/bin/bash

yum update && dnf upgrade
yum install -y curl wget vim openssh python3 python3-pip java-17-openjdk