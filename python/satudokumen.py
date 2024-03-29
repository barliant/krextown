'''
Membaca isi berkas dari korpus Tempo di folder yang diberikan.
Anung Ariwibowo
Versioning
20120118 Membaca korpus Tempo, memasukkannya ke nltk.Text.
20120116 v1.0
'''

import networkx as nx
import os
import nltk
import pprint
import matplotlib.pyplot as plt

def traverse(graph, start, node):
    graph.depth[node.name] = node.shortest_path_distance(start)
    for child in node.hyponyms():
        graph.add_edge(node.name, child.name)
        traverse(graph, start, child)
        
def hyponym_graph(start):
    G = nx.Graph()
    G.depth = {}
    traverse(G, start, start)
    return G
    
def graph_draw(graph):
    nx.draw_graphviz(graph, node_size = [16 * graph.degree(n) for n in graph],
            node_color = [graph.depth[n] for n in graph],
            with_labels = False)
    plt.show()
    
def grab_files(directory):
    for name in os.listdir(directory):
        full_path = os.path.join(directory, name)
        if os.path.isdir(full_path):
            for entry in grab_files(full_path):
                yield entry
        elif os.path.isfile(full_path):
            yield full_path
        else:
            print('Unidentified name %s. It could be a symbolic link' % full_path)

def main():
    G = nx.Graph()

    folderKorpus = os.path.abspath('.') + '\\tempo-txt'
    #folderKorpus = 'tempo-txt'
    '''
    for root, files, dirs in os.walk(folderKorpus):
        for name in files:
            print(os.path.join(root, name))
    '''

    ctrBerkas = 0
    sentTokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    daftarBerkas = grab_files(folderKorpus)
    termList = []
    for berkas in daftarBerkas:
        data = open(berkas)
        ctrBerkas += 1
        ctrBaris = 0
        for baris in data:
            ctrBaris += 1
            sents = sentTokenizer.tokenize(baris)
            for sent in sents:
                kalimat = sent.replace('\n', ' ').strip()
                if len(kalimat) > 0:
                    kalimat = kalimat.lower()
                    tokens = nltk.word_tokenize(kalimat)
                    #print ctrBaris, len(tokens), tokens
                    akhirKalimat = tokens[len(tokens)-1]
                    '''
                    if akhirKalimat != '.':
                        print(berkas)
                        print(ctrBaris)
                        #print(kalimat)
                        print(akhirKalimat)
                    '''
                    if tokens[0] not in termList:
                        termList.append(tokens[0])
                        #print(tokens[0])
                        #print(ctrBerkas, len(termList))
                    for idx in range(1,len(tokens)-1):
                        G.add_edge(tokens[idx-1], tokens[idx])
                        if tokens[idx] not in termList:
                            termList.append(tokens[idx])
                            #print(tokens[idx])
                            #print(ctrBerkas, len(termList))
                    #text = nltk.Text(tokens)
        data.close()
    pprint.pprint(tokens)
    '''
    nx.draw(G)
    plt.show()
    '''
    print("%d berkas diolah" % ctrBerkas)
    print("%d term diolah" % len(termList))

    ce = nx.eigenvector_centrality(G)
    print(sorted(['%0.2f %s'%(ce[node], node) for node in ce]))


if __name__ == '__main__':
    main()
else:
    print "Modul Analisis Graf Bahasa."
    print __doc__

