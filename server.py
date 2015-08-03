from flask import render_template
from flask import Flask

from networkx.readwrite import json_graph
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import requests
import mediacloud
import json
import os
import copy
import ConfigParser
from mediacloudlandscape.landscape import *

# base directory for relative paths
basedir = os.path.dirname(os.path.abspath(__file__))

# logging setup
import logging
logging.basicConfig(filename=os.path.join(basedir, 'log', 'landscape.log'), level=logging.DEBUG)

# set up base directory and init mediacloud

config = ConfigParser.ConfigParser()
config.read(os.path.join(basedir, 'app.config'))
api_key = config.get('mediacloud', 'key')
logging.info('MediaCloud API Initializing...')
mc = mediacloud.api.MediaCloud(api_key)
logging.info('MediaCloud API Initialized.')

def get_dumps(controversy_id):
    query = 'https://api.mediacloud.org/api/v2/controversy_dumps/list?controversies_id=%s&key=%s' % (controversy_id, api_key)
    return json.loads(requests.get(query).text)

def list_dumps(controversy_id):
    print('Dumps for Controversy ID %s:' % (controversy_id))
    dumps = get_dumps(controversy_id)
    for d in dumps:
        print('-%s [%s through %s]' % (d['controversy_dumps_id'], d['start_date'], d['end_date']))
    print('\n')
    return dumps

# For Community Detection / color coding programmatically:
#   http://nbviewer.ipython.org/github/dcalacci/hubway-vis/blob/master/notebooks/Visualizing%20hubway%20data%20using%20sigma.js.ipynb

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Media Cloud Landscapes</h1>'

# Test: 977, 865, 7197

# @app.route('/landscape/<int:controversy_id>/<int:dump_id>/<int:timeslice_id>')
@app.route('/landscape')
def landscape():
	# create_landscape(controversy_id, dump_id, timeslice_id)
	return render_template('landscape_main.html')

@app.route('/landscape_live/<int:controversy_id>/<int:dump_id>/<int:timeslice_id>')
def landscape_live(controversy_id, dump_id, timeslice_id):
	gexf_path = create_landscape(controversy_id, dump_id, timeslice_id)
	return render_template('landscape_live.html', gexf_path=gexf_path)

@app.route('/landscape_file/<string:graph_file>')
def landscape_file(graph_file):
    if(graph_file == 'ebola'):
        f = '/static/ebola-15-2.gexf'

    if(graph_file == 'mlk'):
        f = '/static/mlk-2015-export-test-2.gexf'

    return render_template('landscape_file.html', file=f)

@app.route('/dumps/<int:controversy_id>')
def dumps(controversy_id):
	ds = list_dumps(controversy_id)
	return render_template('dumps.html', controversy_id=controversy_id, dumps=ds)
	# return str([d['controversy_dumps_id'] for d in ds])

@app.route('/controversy_list')
def controversy_list():
    return json.dumps(mc.controversyList())

if __name__ == '__main__':
    app.run(debug=True)

