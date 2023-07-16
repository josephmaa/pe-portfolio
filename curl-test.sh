#!/bin/bash

curl http://localhost:5000/api/timeline_post
curl -X POST http://localhost:5000/api/timeline_post -d 'name=Joseph&email=josephgmaa@berkeley.edu&content=Testing my endpoints'
curl http://localhost:5000/api/timeline_post

