#!/usr/bin/env python
# coding: utf-8
import pickle
import json

inp_file =  open(".coverage", "rb")
coverage_results = pickle.load(inp_file)
inp_file.close()

main_results ={"lines": coverage_results['lines']}

out_file = open(".coverage","w")
out_file.write("!coverage.py: This is a private format, don't read it directly!")
out_file.write(json.dumps(main_results))
out_file.close()
