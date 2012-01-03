#!/usr/bin/env python
# encoding: utf-8
"""
module_IV.py

Code in support of Hacking Social Networks with Python
tutorial on NetworkX

Module IV - Basic Analysis

Author:   Drew Conway
Email:    drew.conway@nyu.edu
Date:     2010-06-01

Copyright (c) 2010, under the Simplified BSD License.  
For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
All rights reserved.
"""

import sys
import os
import networkx as nx
from cjson import *
from urllib import *
from time import *
from scipy import array,unique
import matplotlib.pyplot as P
from numpy import polyfit,setdiff1d
import csv

def snowball_round(G,seeds,myspace=False):
    """Function takes a base graph, and a list of seeds
    and builds out the network data by accessing the
    Google SocialGraph API."""
    t0=time()
    if myspace:
        seeds=get_myspace_url(seeds)
    sb_data=[]
    for s in range(0,len(seeds)):
        s_sg=get_sg(seeds[s])
        new_ego,pen=create_egonet(s_sg) # Create ego net of seed
        # Compose new network data into old abse graph
        for p in pen:
                sb_data.append(p)
        if s<1:
            sb_net=nx.compose(G,new_ego)
        else:
            sb_net=nx.compose(new_ego,sb_net)
        del new_ego
        if s==round(len(seeds)*0.2):
        # Simple progress output, useful for long jobs
            sb_net.name='20% complete'
            nx.info(sb_net)
            print 'AT: '+strftime('%m/%d/%Y, %H:%M:%S', gmtime())
            print ''
        if s==round(len(seeds)*0.4):
            sb_net.name='40% complete'
            nx.info(sb_net)
            print 'AT: '+strftime('%m/%d/%Y, %H:%M:%S', gmtime())
            print ''
        if s==round(len(seeds)*0.6):
            sb_net.name='60% complete'
            nx.info(sb_net)
            print 'AT: '+strftime('%m/%d/%Y, %H:%M:%S', gmtime())
            print ''
        if s==round(len(seeds)*0.8):
            sb_net.name='80% complete'
            nx.info(sb_net)
            print 'AT: '+strftime('%m/%d/%Y, %H:%M:%S', gmtime())
            print ''
        if s==len(seeds)-1:
            print 'NEW NETWORK COMPLETE!'
            print 'AT: '+strftime('%m/%d/%Y, %H:%M:%S', gmtime())
            sb_net.name=G.name+'--> '
    # Return newly discovered seeds
    sb_data=array(sb_data)
    sb_data.flatten()
    sb_data=unique(sb_data)
    nx.info(sb_net)
    return sb_net,sb_data
        
def get_myspace_url(seeds):
    """Special function for parsing myspace.com users"""
    uids=[]
    for s in seeds:
        b=s.split('=')
        b=b[len(b)-1]
        uids.append('http://www.myspace.com/'+str(b))
    return uids

def create_egonet(s):
    """Base function for creating an ego network from some 
    SocialGraph URL"""
    try:
        raw=decode(s)
        G=nx.DiGraph()
        pendants=[]
        n=raw['nodes']
        nk=n.keys()
        G.name=str(nk)
        pendants=[]
        # We simply add edges iteratively
        for a in range(0,len(nk)):
            for b in range(0,len(nk)):
                if a!=b:
                    G.add_edge(nk[a],nk[b])
        for k in nk:
            ego=n[k]
            # Access the appropriate JSON datum for in- and out-degrees
            ego_out=ego['nodes_referenced']     
            for o in ego_out:
                G.add_edge(k,o)
                pendants.append(o)
            ego_in=ego['nodes_referenced_by']
            for i in ego_in:
                G.add_edge(i,k)
                pendants.append(i)
        pendants=array(pendants,dtype=str)
        pendants.flatten()
        pendants=unique(pendants)
        return G,pendants
    except DecodeError:
        print 'WEB ERROR--Returning empty DiGraph'
        G=nx.DiGraph()
        pendants=[]
        return G,pendants
    except KeyError:
        print 'NET BUILD ERROR FOR: '+str(nk)+'--Returning empty DiGraph'
        G=nx.DiGraph()
        pendants=[]
        return G,pendants

def get_sg(seed_url):
    """Create Internet socket for some seed URL"""
    sgapi_url="http://socialgraph.apis.google.com/lookup?q="+seed_url+"&edo=1&edi=1&fme=1&pretty=0"
    try:
        furl=urlopen(sgapi_url)
        fr=furl.read()
        furl.close()
        return fr
    except IOError:
        print "Could not connect to website"
        print sgapi_url
        return {}
        
        
def highest_centrality(cent_dict):
    """Returns node key with largest value from
    NX centrality dict"""
    # Create ordered tuple of centrality data
    cent_items=cent_dict.items()    
    # List comprehension!
    cent_items=[(b,a) for (a,b) in cent_items]
    # Sort in descending order
    cent_items.sort()
    cent_items.reverse()
    return cent_items[0][1]
    
def centrality_scatter(met_dict1,met_dict2,path="",ylab="",xlab="",title="",reg=False):
    """Generates a scatter plot of two network centrality metrics.
    Actor ID's are used as points, and options axis labels and 
    title can be provided.
    
    ### Parameters ###
    met_dict1:  x-axis data
    met_dict2:  y-axis data
    path:       path to save figure
    
    ylab:       y-axis label
    xlab:       x-axis label
    title:      plot title
    reg:        boolean to add a best fit line
    """
    fig=P.figure(figsize=(7,7))
    ax1=fig.add_subplot(111)
    # Create items so actors can be sorted properly
    met_items1=met_dict1.items()
    met_items2=met_dict2.items()
    met_items1.sort()
    met_items2.sort()
    # Grab data
    xdata=[(b) for (a,b) in met_items1]
    ydata=[(b) for (a,b) in met_items2]
    # Add each actor to the plot by ID
    for p in xrange(len(met_items1)):
        ax1.text(x=xdata[p],y=ydata[p],s=str(met_items1[p][0]),color="indigo")
    # If adding a best fit line, we will use NumPy to calculate the points.
    if reg:
        # Function returns y-intercept and slope.  So, we create a function to 
        # draw LOBF from this data
        slope,yint=polyfit(xdata,ydata,1)
        xline=P.xticks()[0]
        yline=map(lambda x: slope*x+yint,xline)
        # Add line
        ax1.plot(xline,yline,ls='--',color='grey')
    # Set new x- and y-axis limits to data
    P.xlim((0.0,max(xdata)+(.15*max(xdata))))   # Give a little buffer
    P.ylim((0.0,max(ydata)+(.15*max(ydata))))
    # Add labels
    ax1.set_title(title)
    ax1.set_xlabel(xlab)
    ax1.set_ylabel(ylab)
    # Save figure
    P.savefig(path,dpi=100)
    
def add_metric(G,met_dict):
    """Adds metric data to G from a dictionary keyed by node labels
    
    ### Parameters ###
    
    G:          NetworkX graph object
    met_dict:   Dictionary of metric keyed by node labels
    """
    if(G.nodes().sort()==met_dict.keys().sort()):
        for i in met_dict.keys():
            G.add_node(i,metric=met_dict[i])
        return G
    else:
        raise ValueError("Node labels do not match")
    
def csv_exporter(data_dict,path):
    """Takes a dict of centralities keyed by column headers and exports 
    data as a CSV file"""
    # Create column header list
    col_headers=["Actor"]
    col_headers.extend(data_dict.keys())
    # Create CSV writer and write column headers
    writer=csv.DictWriter(open(path,"w"),fieldnames=col_headers)
    writer.writerow(dict((h,h) for h in col_headers))
    # Write each row of data
    for j in data_dict[col_headers[1]].keys():
        # Create a new dict for each row
        row=dict.fromkeys(col_headers)
        row["Actor"]=j
        for k in data_dict.keys():
            row[k]=data_dict[k][j]
        writer.writerow(row)
        

def main():
    # 1.0 Loading a local data file
    # Load the Hartford drug users data, a directed binary graph.
    # We will specify that the graph be generated as a directed graph, and
    # that the nodes are integers (rather than strings)
    hartford=nx.read_edgelist("../../data/hartford_drug.txt",create_using=nx.DiGraph(),nodetype=int)
    nx.info(hartford)  # Check the the data has been loaded properly

    # 2.0 Connecting to a database

    # 3.0 Building a network directly from the Internet
    # WARNING: This can take a long time to run!
    seed="imichaeldotorg"   # Set the seed user within livejournal.com
    seed_url="http://"+seed+".livejournal.com"
    # 3.1 Scrape, parse and build seed's ego net
    sg=get_sg(seed_url)
    net,newnodes=create_egonet(sg)
    nx.write_pajek(net,"../../data/"+seed+"_ego.net") # Save data as Pajek
    nx.info(net)
    # 3.2 Perform snowball search, where k=2
    k=2
    for g in range(k):
        net,newnodes=snowball_round(net,newnodes)
        nx.write_pajek(net,"../../data/"+seed+"_step_"+str(g+1)+".net")
    
    # 4.0 Calculate in-degree centrality for Hartford data
    in_cent=nx.in_degree_centrality(hartford)
    
    # 5.0 Calculating multiple measures, and finding
    # most central actors
    hartford_ud=hartford.to_undirected()
    hartford_mc=nx.connected_component_subgraphs(hartford_ud)[0]    # First, extract MC
    # 5.1 Calculate multiple measures on MC
    bet_cen=nx.betweenness_centrality(hartford_mc)
    clo_cen=nx.closeness_centrality(hartford_mc)
    eig_cen=nx.eigenvector_centrality(hartford_mc)
    # 5.2 Find the actors with the highest centrality for each measure,
    print("Actor "+str(highest_centrality(bet_cen))+" has the highest Betweenness centrality")
    print("Actor "+str(highest_centrality(clo_cen))+" has the highest Closeness centrality")
    print("Actor "+str(highest_centrality(eig_cen))+" has the highest Eigenvector centrality")
    
    # 6.0 Calculating degree distribution
    ba_net=nx.barabasi_albert_graph(1000,2)   # Create a Barabasi-Albert network
    # 6.1 NX has a nice built-in function for degree distribution
    dh=nx.degree_histogram(ba_net)
    # 6.2 Plot using same method as http://networkx.lanl.gov/examples/drawing/degree_histogram.html
    pos=nx.spring_layout(ba_net)
    P.figure(figsize=(8,8))
    P.loglog(dh,'b-',marker='o')
    P.title("Degree rank plot (log-log)")
    P.ylabel("Degree")
    P.xlabel("Frequency")
    # 6.4 Draw graph in inset
    P.axes([0.45,0.45,0.45,0.45])
    P.axis('off')
    nx.draw_networkx_nodes(ba_net,pos,node_size=20)
    nx.draw_networkx_edges(ba_net,pos,alpha=0.4)
    P.savefig("../../images/figures/ba_10000.png")
    
    # 6.0 Finding community structure
    clus=nx.clustering(hartford_mc,with_labels=True)
    # 6.1 Get counts of nodes membership for each clustering coefficient
    unique_clus=list(unique(clus.values()))
    clus_counts=zip(map(lambda c: clus.values().count(c),unique_clus),unique_clus)
    clus_counts.sort()
    clus_counts.reverse()
    # 6.2 Create a subgraph from nodes with most frequent clustering coefficient
    mode_clus_sg=nx.subgraph(hartford_mc,[(a) for (a,b) in clus.items() if b==clus_counts[0][1]])
    P.figure(figsize=(6,6))
    nx.draw_spring(mode_clus_sg,with_labels=False,node_size=60,iterations=1000)
    P.savefig('../../images/networks/mode_clus_sg.png')
    
    # 7.0 Plot Eigenvector centrality vs. betweeness in matplotlib
    centrality_scatter(bet_cen,eig_cen,"../../images/figures/drug_scatter.png",ylab="Eigenvector Centrality",xlab="Betweenness Centrality",title="Hartford Drug Network Key Actor Analysis",reg=True)
    
    # 8.0 Outputting network data
    # First, output the data as an adjaceny list
    nx.write_adjlist(hartford_mc,"../../data/hartford_mc_adj.txt")
    # 8.1 Add metric data to the network object
    hartford_mc_met=add_metric(hartford_mc,eig_cen)
    print(hartford_mc_met.nodes(data=True)[1:10])   # Check the the data was stored
    # 8.2 output data using the Pajak format to save the node attribute data
    nx.write_pajek(hartford_mc,"../../data/hartford_mc_metric.net")    # NX will automatically add all attibute data to output
    
    # 9.0 Exporting data to a CSV file
    csv_data={"Betweeness":bet_cen,"Closeness":clo_cen,"Eigenvector":eig_cen}
    # 9.1 After we have all the data in a single dict, we send it to out function
    # to export the data as a CSV
    csv_exporter(csv_data,"../../data/drug_data.csv")
    
    # 10.0 Visualization basics
    # 10.1 Use subplots to draw random and circular layouts
    # of drug net side-by-side
    fig1=P.figure(figsize=(9,4))
    fig1.add_subplot(121)
    nx.draw_random(hartford_mc,with_labels=False,node_size=60)
    fig1.add_subplot(122)
    nx.draw_circular(hartford_mc,with_labels=False,node_size=60)
    P.savefig("../../images/networks/rand_circ.png")
    # 10.2 Draw spring, spectral layouts
    P.figure(figsize=(8,8))
    nx.draw_spring(hartford_mc,with_labels=False,node_size=60,iterations=10000)
    P.savefig("../../images/networks/spring.png")
    P.figure(figsize=(8,8))
    nx.draw_spectral(hartford_mc,with_labels=False,node_size=60,iterations=10)
    P.savefig("../../images/networks/spectral.png")
    # 10.3 Draw shell layout with inner-circle as the 25th percentile 
    # Eigenvector centrality actors
    P.figure(figsize=(8,8))
    # Find actors in 25th percentile
    max_eig=max([(b) for (a,b) in eig_cen.items()])
    s1=[(a) for (a,b) in eig_cen.items() if b>=.25*max_eig]
    s2=hartford_mc.nodes()
    # setdiff1d is a very useful NumPy function!
    s2=list(setdiff1d(s2,s1))       
    shells=[s1,s2]    
    # Calculate psotion and draw          
    shell_pos=nx.shell_layout(hartford_mc,shells)
    nx.draw_networkx(hartford_mc,shell_pos,with_labels=False,node_size=60)
    P.savefig("../../images/networks/shell.png")
    
    # 11.0 Adding analysis to visualization
    P.figure(figsize=(15,15))
    P.subplot(111,axisbg="lightgrey")
    spring_pos=nx.spring_layout(hartford_mc,iterations=1000)
    # 11.1 Use betweeneess centrality for node color intensity
    bet_color=bet_cen.items()
    bet_color.sort()
    bet_color=[(b) for (a,b) in bet_color]
    # 11.2 Use Eigenvector centrality to set node size
    eig_size=eig_cen.items()
    eig_size.sort()
    eig_size=[((b)*2000)+20 for (a,b) in eig_size]
    # 11.3 Use matplotlib's colormap for node intensity 
    nx.draw_networkx(hartford_mc,spring_pos,node_color=bet_color,cmap=P.cm.Greens,node_size=eig_size,with_labels=False)
    P.savefig("../../images/networks/analysis.png")
    
if __name__ == '__main__':
	main()

