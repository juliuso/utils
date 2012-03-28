#!/usr/bin/env python
import os
import re
# Cleans up dirty filenames containing %20, can be improved.


def replace(filename):
    return re.sub('%20', '_', filename)

for filename in os.listdir("."):
    os.rename(filename, replace(filename))