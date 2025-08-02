#!/bin/bash

dnf update && dnf upgrade
dnf install -y curl wget vim openssh python3 python3-pip java-17-openjdk