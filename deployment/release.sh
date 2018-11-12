#!/bin/bash

# 代码发布脚本

rsync -cvrP --exclude={.git,.hg,.svn,.venv} $PROJECT $USER@$HOST:$PATH
