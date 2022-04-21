import argparse
import os
import subprocess
from build_report import *

"""
Prepare report dictionary
"""
gps_data=(23.5558,46.6396)
area_results = {'i':1,
            'gps_S' : gps_data[0],
            'gps_W' : gps_data[1],
            'irregular_area' :  2,
            'river_area' :  1,
            'veg_area' :  2,
            'nveg_area' :  5,
            'fname' :  'map.jpg',
            'cost' :  20000}

"""
Each call to generate_result() will append to results and generate a new section in the report.
"""
results = ""
results += generate_result(area_results)
area_results['i'] = 2
results += generate_result(area_results)

"""
Generate the report
"""
content = base_structure({'result':results})
with open('cover.tex','w') as f:
    f.write(content)

###############################################################################

cmd = ['pdflatex', '-interaction', 'nonstopmode', 'cover.tex']
# proc = subprocess.Popen('dir', cwd=os.getcwd())
print(os.getcwd())
proc = subprocess.Popen(cmd, shell = True )

proc.communicate()

retcode = proc.returncode
if not retcode == 0:
    os.unlink('cover.pdf')
    raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 