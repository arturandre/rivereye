#!/bin/bash

# This creates the rivereyedb in postgres.
# Configure the username, hostname and password as needed.

# Based on:
# Ref: https://stackoverflow.com/a/57505242/3562468

username="postgres"
hostname="172.19.0.3"
password="1234"

#psql -h 172.19.0.3 -U postgres
#echo $password createdb -h $hostname -U $username rivereyedb

createdb -h $hostname -U $username rivereyedb
