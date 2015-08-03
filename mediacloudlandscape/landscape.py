from networkx.readwrite import json_graph
import networkx as nx
import community
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

# ----------------------------------

basedir = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser.ConfigParser()
config.read(os.path.join(basedir, 'app.config'))
api_key = config.get('mediacloud', 'key')

mc = mediacloud.api.MediaCloud(api_key)
print(api_key)

# ----------------------------------

current_gen = 1
generation_md = { 1: { 'controversy_id': 720, 'top_word_count': 100 }}

# ----------------------------------

def build_top_words(media_list, timeslice_id=None, remove_words=None):
    # TODO: Add parameters for wordCount resolution (sample size, etc.)
    # Output word count run statistics to file for metadata / paradata record
    top_words = {}
    if(remove_words == None):
        remove_words=[]
    media_sources = {ms['media_id']: ms['name'] for ms in media_list}
    for m in [ms['media_id'] for ms in media_list]:
        if(timeslice_id == None):
            top_words[m] = mc.wordCount('{~ controversy:%s } and media_id:%s' % (generation_md[current_gen]['controversy_id'], m), num_words=generation_md[current_gen]['top_word_count']+len(remove_words))
            print('Got %d words from %s' % (len(top_words[m]), media_sources[m]))
        else:
            top_words[m] = mc.wordCount('{~ controversy_dump_time_slice:%s } and media_id:%s' % (timeslice_id, m), num_words=generation_md[current_gen]['top_word_count']+len(remove_words))
            print('Got %d words from %s' % (len(top_words[m]), media_sources[m]))
    
    print('\nAll Media Sources Complete!')
    return top_words

def clean_top_words(word_set, remove_words_list, word_limit=None):
    for media_source in word_set:
        # remove stopwords        
        word_set[media_source] = [w for w in word_set[media_source] if w['term'] not in remove_words_list]

        # trim any extra words above the word limit
        if(word_limit != None):
            word_set[media_source] = word_set[media_source][:generation_md[current_gen]['top_word_count']]
        
        # maybe output some summary data
        return word_set

def build_network(top_words, sources, media_attribs=None):
    source_ids = [ms['media_id'] for ms in sources]
    media_sources = {ms['media_id']: ms['name'] for ms in sources}
    
    # Media Source / Word Network
    msw_network = nx.DiGraph()
    # msw_network = nx.Graph()

    pairwise_sources = {}

    for m in source_ids:
        # pairwise_sources[m] = nx.DiGraph()
        
        if(m in top_words.keys()):
            for w in top_words[m]:
                msw_network.add_node(w['term'], type='word', viz = {'color':{'r':77,'g':7,'b':0}, 'position':{'x':1.0,'y':1.0,'z':0.0}, 'size':42})
                if(media_attribs == None):
                    msw_network.add_node(media_sources[m], type='media_source')
                else:
                    msw_network.add_node(media_sources[m], type='media_source', category=media_attribs[m])
                        
                msw_network.add_edge(media_sources[m], w['term'], weight=w['count'])

                # pairwise_sources[m].add_node(w['term'], type='word')
                # pairwise_sources[m].add_node(media_sources[m], type='media_source')
                # pairwise_sources[m].add_edge(media_sources[m], w['term'], weight=w['count'])
        else:
            print('Skipping %s...' % media_sources[m])

    # for node in msw_network.nodes_iter():
    #     msw_network[node]['viz'] = {}
    #     msw_network[node]['viz']['position'] = {}
    #     msw_network[node]['viz']['position']['x'] = "1.0"
    #     msw_network[node]['viz']['position']['y'] = "1.0"
    #     msw_network[node]['viz']['position']['z'] = "0.0"
    #     msw_network[node]['viz']['color'] = {}
    #     msw_network[node]['viz']['color']['r'] = "100"
    #     msw_network[node]['viz']['color']['g'] = "100"
    #     msw_network[node]['viz']['color']['b'] = "100"
    #     msw_network[node]['viz']['size'] = "10"

    # print "== COMMUNITY DETECTION ==\n\n"
    # partition = community.best_partition(msw_network)
    # count = 0.
    # for com in set(partition.values()):
    #     count = count + 1.
    #     list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
    #     for node in list_nodes:
    #         print "- {0}\n".format(node)
    #         n = msw_network[node]
    #         n['modularity_class'] = str(count)

    return msw_network

def export_gexf_network(network, filename):
    print('Writing %d nodes to network in %s.' % (network.number_of_nodes(), filename))
    nx.write_gexf(network, filename)
    
def export_d3_network(network, filename):
    print('Writing %d nodes to network as D3 JSON graph.' % (network.number_of_nodes()))
    data = json_graph.node_link_data(network)
    with open(filename + '.json', 'w') as f:
        f.write(json.dumps(data))
    
def get_dumps(controversy_id):
    query = 'https://api.mediacloud.org/api/v2/controversy_dumps/list?controversies_id=%s&key=%s' % (controversy_id, api_key)
    return json.loads(requests.get(query).text)

def get_dump(dump_id):
    query = 'https://api.mediacloud.org/api/v2/controversy_dumps/single/%s?key=%s' % (dump_id, api_key)
    return json.loads(requests.get(query).text)

def get_timeslices(dump_id, period=None):
    if(period == None):
        query = 'https://api.mediacloud.org/api/v2/controversy_dump_time_slices/list?controversy_dumps_id=%s&key=%s' % (dump_id, api_key)
    else:
        query = 'https://api.mediacloud.org/api/v2/controversy_dump_time_slices/list?controversy_dumps_id=%s&period=%s&key=%s' % (dump_id, period, api_key)
    return json.loads(requests.get(query).text)

def get_timeslice(timeslice_id):
    query = 'https://api.mediacloud.org/api/v2/controversy_dump_time_slices/single/%s?key=%s' % (timeslice_id, api_key)
    return json.loads(requests.get(query).text)
    
def get_top_influential_mediasources(controversy_dump_time_slices_id, count):
    media_sources = list()
    last_media_id = 0
    while(count > 0):
        if(count > 100):
            query = 'https://api.mediacloud.org/api/v2/media/list?controversy_dump_time_slices_id=%s&rows=%s&last_media_id=%s&key=%s' % (str(controversy_dump_time_slices_id), 100, last_media_id, api_key)
            count = count - 100
            ms_response = json.loads(requests.get(query).text)
            if(len(ms_response) < 100):
                count = 0
            if(len(ms_response) != 0):
                last_media_id = max([m['media_id'] for m in ms_response])
        else:
            query = 'https://api.mediacloud.org/api/v2/media/list?controversy_dump_time_slices_id=%s&rows=%s&key=%s' % (str(controversy_dump_time_slices_id), count, api_key)
            count = 0
            ms_response = json.loads(requests.get(query).text)
        media_sources = media_sources + ms_response
    return media_sources

def get_top_x_sources(controversy_id, source_count, dump_id=None, timeslice_id=None):
    if(dump_id == None):
        dumps = get_dumps(controversy_id)
    else:
        dumps = get_dump(dump_id)
        
    if(timeslice_id == None):
        timeslices = get_timeslices(dumps[0]['controversy_dumps_id'])
        top = get_top_influential_mediasources(timeslices[-1]['controversy_dump_time_slices_id'], source_count)
        return top
    else:
        timeslices = get_timeslice(timeslice_id)
        top = get_top_influential_mediasources(timeslices[0]['controversy_dump_time_slices_id'], source_count)
        return top

def list_top_sources(controversy_id, source_count, dump_id=None, timeslice_id=None):
    print('Listing top %d sources for Controversy ID %s\n' % (source_count, controversy_id))
    top = get_top_x_sources(controversy_id, source_count, dump_id=dump_id, timeslice_id=timeslice_id)
    print('%d sources found.\n' % len(top))
    for idx, t in enumerate(top):
        print('%s - Name: %s, MediaID: %s, Inlink Count: %s)' % (idx+1, t['name'], t['media_id'], t['inlink_count']))
    print('\n')
    
def plot_top_sources(controversy_id, source_count, dump_id=None, timeslice_id=None, title=None):
    top = get_top_x_sources(controversy_id, source_count, dump_id=dump_id, timeslice_id=timeslice_id)
    inlink_counts = [t['inlink_count'] for t in top]
    fig = plt.figure(figsize=(16,5))
    fig.suptitle(title, fontsize=20)
    plt.xticks(range(len(top)), [t['name'] for t in top], size='small', rotation=90)
    plt.xlabel('Media Sources')
    plt.ylabel('In-Link Count')
    ax = fig.add_subplot(111)
    ind = np.arange(len(inlink_counts))
    rects1 = ax.bar(ind, inlink_counts, alpha=0.8, align='center')
    plt.show()
        
def list_dumps(controversy_id):
    print('Dumps for Controversy ID %s:' % (controversy_id))
    dumps = get_dumps(controversy_id)
    for d in dumps:
        print('-%s [%s through %s]' % (d['controversy_dumps_id'], d['start_date'], d['end_date']))
    print('\n')

def list_timeslices(controversy_id, dump_id=None, period=None):
    print('Timeslices for %s:' % (controversy_id))
    # If no dump specified, list the most recent one.
    if(dump_id == None):
        dumps = get_dumps(controversy_id)
        timeslices = get_timeslices(dumps[0]['controversy_dumps_id'])
    else:
        timeslices = get_timeslices(dump_id, period)
    for idx, t in enumerate(timeslices):
        print('- %d.)%s [%s through %s]' % (idx, t['controversy_dump_time_slices_id'], t['start_date'], t['end_date']))
    print('\n')
    
# Remove Media Source from Network 
def remove_word_source_from_network(ms_name, word_list):
    ms = mc.mediaList(name_like=ms_name)
    if(len(ms) == 1):
        try:
            del word_list[ms[0]['media_id']]
        except KeyError:
            print('Media Source not present in list.')
    elif(len(ms) == 0):
        print('No match for %s.' % ms_name)
    else:
        print('Multiple matches for Media Source. No action taken.')
        
# Remove Media Source from Media Source List
def remove_media_source(remove_name, media_sources):
    for idx, ms in enumerate(media_sources):
        if(ms['name'] == remove_name):
            print('Deleting %s (%d)' % (ms['name'], ms['media_id']))
            del media_sources[idx]
            return media_sources
    print('Media Source %s Not Present.' % remove_name)
    return media_sources

# TODO: Enable media source range based on significance, and allow selection of social or inlink, 
def generate_network_of_frames(controversy_id, dump_id, timeslice_id, num_of_sources, out_name=None, remove_media_list=None, remove_word_list=[], generate_word_lists=False, include_media_list=None, media_attribs=None):
    if(out_name == None):
        out_name = 'network_of_frames-%s' % datetime.datetime.now().isoformat()
    
    if(remove_media_list == None):
        remove_media_list = []
        
#     if(media_attribs == None):
#         media_attribs = {}
        
    if(include_media_list == None):
        media_sources_md = get_top_x_sources(controversy_id, num_of_sources+len(remove_media_list), dump_id, timeslice_id)
    else:
        media_sources_md = include_media_list

    if(remove_media_list != None):
        for r in remove_media_list:
            media_sources_md = remove_media_source(r, media_sources_md)

    top_words = build_top_words(media_sources_md, timeslice_id, remove_word_list)
    if(remove_word_list != None):
        top_words = clean_top_words(top_words, remove_word_list)

    frame_network = build_network(top_words, media_sources_md, media_attribs)

    export_gexf_network(frame_network, '%s.gexf' % out_name)
    export_d3_network(frame_network, '%s' % out_name)
    
    if(generate_word_lists == True):
        with open('%s-word-usage.txt' % out_name, 'wb') as wl:
            all_words = []
            media_sources = {ms['media_id']: ms['name'] for ms in media_sources_md}
            counts = {}
            for ms in top_words:
                wl.write("\n\n%s (media id: %d):\n" % (media_sources[ms].encode('ascii', 'ignore'), ms))
                for w in top_words[ms]:
                    all_words.append(w['term'])

                    # increment count to see how many media source include each word
                    # counts[ms]

                    wl.write("- %s (%d)\n" % (w['term'].encode('ascii', 'ignore'), w['count']))
                wl.write("\n")
    
    linefeed=chr(10) # linefeed=\n
    s=linefeed.join(nx.generate_gexf(frame_network))  # doctest: +SKIP
    # for line in nx.generate_gexf(frame_network):  # doctest: +SKIP
    #     print line

    return s

def create_landscape(controversy_id, dump_id, timeslice_id):
    # Defaults
    num_of_sources = 25
    num_of_words = 100
    # remove_media_sources = ['digg.com', 'delicious.com', 'en-gb.facebook', 'newsvine.com', 'nationalservice.gov', 'nobelprize.org', 'Twitter', 'YouTube', 'selmamovie.com', 'hollywoodreporter.com', 'variety.com', 'imdb.com']
    remove_media_sources = []
    remove_words = []
    filename = 'static/mc_network_{0}'.format(datetime.datetime.now().isoformat())
    # list_top_sources(cid, num_of_sources, dump_id, slice_id)
    # plot_top_sources(cid, num_of_sources, dump_id, slice_id, title='MTV MLK - Top {0} Sources / Overall'.format(num_of_sources))
    nof = generate_network_of_frames(controversy_id, dump_id, timeslice_id, num_of_sources, filename, remove_media_sources, remove_words, generate_word_lists=True)
    return filename
