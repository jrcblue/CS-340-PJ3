from simulator.node import Node
import json
import sys
import copy


# also implement Dijkstra’s Algorithm
class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.all_edges = {}  # (A,B):latency
        self.edges_seq = {}  # (A,B):seq

    # Return a string
    def __str__(self):
        return str(self.id) + "\n"
        # return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # store the link in graph
        # if neighbor == 9 and self.id ==11:
            # print('l',latency)
        if latency == -1 and neighbor in self.neighbors:
            # remove neighbor node
            self.neighbors.remove(neighbor)

            self.all_edges.pop((self.id, neighbor))
            self.all_edges.pop((neighbor, self.id))

            msg = json.dumps([self.id, neighbor, latency, self.get_time(), self.id])

            # self.seq += 1
            self.send_to_neighbors(msg)


        else:
            old_latency = self.all_edges.get((self.id, neighbor))
            self.all_edges.update({(self.id, neighbor): latency})
            self.all_edges.update({(neighbor, self.id): latency})
            self.edges_seq.update({(self.id, neighbor): self.get_time()})
            self.edges_seq.update({(neighbor, self.id): self.get_time()})

            self.edges_seq.update({(neighbor, self.id):self.get_time()})
            self.edges_seq.update({(self.id, neighbor): self.get_time()})

            if neighbor not in self.neighbors:
                self.neighbors.append(neighbor)
                # self.seq += 1

                msg = json.dumps([self.id, neighbor, latency, self.get_time(),self.id])
                self.send_to_neighbors(msg)

                # share link to neighbors
                for M,N in self.all_edges.keys():
                    ltc = self.all_edges.get((M,N))

                    seq = self.edges_seq.get((M,N))
                    msg = json.dumps([M, N, ltc, seq,self.id])
                    # previous record CANNONT use newest seq
                    self.send_to_neighbor(neighbor,msg)


            else:
                if old_latency != latency:
                    # update edges version
                    self.edges_seq.update({(self.id,neighbor): self.get_time()})
                    self.edges_seq.update({(neighbor,self.id): self.get_time()})

                    # share link to neighbors
                    msg = json.dumps([self.id, neighbor, latency, self.get_time(),self.id])
                    # self.seq += 1
                    self.send_to_neighbors(msg)


    # Fill in this function
    def process_incoming_routing_message(self, m):
        # reconstruct msg, add source
        # 1. send to neighbors except source
        # 2. if get old version, give back new one


        new_node1, new_node2, ltc, seq, src = json.loads(m)

        # update current edge latency
        if self.edges_seq.get((new_node1,new_node2)) is None:
            # print("nodeID=",self.id," receive NEW NODE:", new_node1,new_node2,ltc)
            self.edges_seq.update({(new_node1,new_node2): seq})
            self.edges_seq.update({(new_node2,new_node1): seq})

            self.all_edges.update({(new_node2, new_node1): ltc})
            self.all_edges.update({(new_node1, new_node2): ltc})

            if ltc == -1:
                self.all_edges.pop((new_node2, new_node1))
                self.all_edges.pop((new_node1, new_node2))

            # self.send_to_neighbors(m)???
            for nei in self.neighbors:
                if nei != src:
                    msg = json.dumps([new_node1, new_node2, ltc, seq, self.id])
                    self.send_to_neighbor(nei,msg)

        elif seq > self.edges_seq.get((new_node2, new_node1)):
            # print("nodeID=", self.id, " receive NEW UPDATE:", new_node1, new_node2, ltc)
            self.edges_seq.update({(new_node1, new_node2): seq})
            self.edges_seq.update({(new_node2, new_node1): seq})
            # if new_node1==9 and new_node2 == 1:pass
                # print('ltc',ltc,'seq',seq)
            self.all_edges.update({(new_node2, new_node1): ltc})
            self.all_edges.update({(new_node1, new_node2): ltc})

            if ltc == -1:
                self.all_edges.pop((new_node2, new_node1))
                self.all_edges.pop((new_node1, new_node2))

            # self.send_to_neighbors(m)???
            for nei in self.neighbors:
                if nei != src:
                    msg = json.dumps([new_node1, new_node2, ltc, seq, self.id])
                    self.send_to_neighbor(nei,msg)


        else:
            # send back newest msg to who gives old one
            if seq < self.edges_seq.get((new_node2,new_node1)):
                seq = self.edges_seq.get((new_node1,new_node2))
                ltc = self.all_edges.get((new_node1,new_node2))
                msg = json.dumps([new_node1, new_node2, ltc, seq, self.id])
                self.send_to_neighbor(src, msg)
            return

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # initialize the unvisited Q
        dist = {}
        prev = {}
        graph_nodes = self.get_graph_nodes()
        for v in graph_nodes:
            dist[v] = sys.maxsize
            prev[v] = None
        dist[destination] = 0
        for vt in self.get_neighbors(destination):
            dist[vt] = self.all_edges.get((vt, destination))
            prev[vt] = destination
        Q = graph_nodes[:]
        Q.remove(destination)

        while Q:
            if destination == 2 and self.id == 11:
                print(self.all_edges.get((1,9)))
            # print(prev.get(9))
            # print(prev.get(1))
            # find the minimum values in Q
            min_dist = sys.maxsize
            min_node = Q[0]

            for ver in Q:
                if dist.get(ver) < min_dist:
                    min_dist = dist.get(ver)
                    min_node = ver
            Q.remove(min_node)
            nb_of_mincode = self.get_neighbors(min_node)

            for nei in nb_of_mincode:
                if nei in Q:
                    alt = dist[min_node] + self.all_edges.get((min_node, nei))
                    if alt < dist[nei]:
                        dist[nei] = alt
                        prev[nei] = min_node

        return prev.get(self.id)

    def get_neighbors(self, node):
        ls = []
        # print("all edges keys:", self.all_edges.keys())
        for M, N in self.all_edges.keys():
            if M == node and N not in ls:
                ls.append(N)
            if N == node and M not in ls:
                ls.append(M)

        return ls

    def get_graph_nodes(self):
        q = []
        for M, N in self.all_edges.keys():
            if M not in q:
                q.append(M)
            if N not in q:
                q.append(N)

        return q
