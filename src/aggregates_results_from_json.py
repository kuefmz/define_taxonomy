import json
import csv
import os
from collections import defaultdict
from pathlib import Path

# Initialize a dictionary to hold the details of each category pair
match_touples = set()

data = {}

