# Media Cloud Landscape
Web-Based Media Landscape Tool for Media Cloud

Media Cloud Landscape is an interactive visualization that allows exploration of media activity and the language used around specific topics. 

# Installation
`chown www-data:www-data log`

## How It Works
It works by selecting a set of influential media sources (blogs, citizen media, mainstream media) for a given topic and collecting the most frequently used words for each. With this set of language used by each source, a bipartite network graph is built to represent the usage of words by media sources, with the connections weighted by the frequency of usage. This allows for for laying out the network visualization by clustering (Force Atlas 2) and identifying communities of discourse using network community detection.

## How To Read It
There are a few ways to read the resulting visualization. 

1.	Node Type: There are two types of nodes visualized: Media Sources and Words. Looking at Media Source nodes allows one to see which media sources use the most similar language about the topic. Similar Media Source nodes will be pulled together because they use many words in common. Media Sources that have less language in common will be further apart. Word Nodes appear close to words that are used in the same context. 

2.	Color: Communities of discourse in the network are represented by categorical colors. Each color represents a community, identifying that there are a cluster of words and media sources that use language in a similar way. These communities do not represent completely distinct conversations, but rather clusters of word usage that occur frequently together. Similar colors do not indicate similar word usage.

3.	Center to Edge: Words that are commonly used by many or all of the media sources appear in the center of the graph. At the outer edge, clusters of words that are only used frequently by one or a few media sources appear together, frequently giving a sense of what is unique about an individual media source's coverage.

