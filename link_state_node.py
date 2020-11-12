from simulator.node import Node
import json
import sys

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.edge_latencies = {}
        self.edge_m_timestamps = {}

    # Return a string
    def __str__(self):
        # return "Rewrite this function to define your node dump printout"
        return "Node " + str(self.id) + "\n"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # pass
        time_stamp = self.get_time()
        self.edge_m_timestamps.update({(self.id, neighbor): time_stamp})
        self.edge_m_timestamps.update({(neighbor, self.id): time_stamp})

        if latency == -1:
            self.edge_latencies.pop((self.id, neighbor))
            self.edge_latencies.pop((neighbor, self.id))
            if(neighbor in self.neighbors):
                self.neighbors.remove(neighbor)
        else:
            former_latency = self.edge_latencies.get((self.id, neighbor))
            self.edge_latencies.update({(self.id, neighbor): latency})
            self.edge_latencies.update({(neighbor, self.id): latency})
            if(neighbor not in self.neighbors):
                self.neighbors.append(neighbor)
                for node_1, node_2 in self.edge_latencies.keys(): #share dv to the new neighbor
                    self.send_to_neighbor(neighbor, json.dumps([node_1, node_2, self.edge_latencies.get((node_1, node_2)), self.edge_m_timestamps.get((node_1, node_2)), self.id]))

        self.send_to_neighbors(json.dumps([self.id, neighbor, latency, time_stamp, self.id]))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # pass
        src_node, dst_node, latency, time_stamp, msg_src = json.loads(m)

        if self.edge_m_timestamps.get((src_node,dst_node)) is None or time_stamp > self.edge_m_timestamps.get((src_node, dst_node)):

            self.edge_m_timestamps.update({(src_node,dst_node): time_stamp})
            self.edge_m_timestamps.update({(dst_node,src_node): time_stamp})

            if latency == -1:
                self.edge_latencies.pop((dst_node, src_node))
                self.edge_latencies.pop((src_node, dst_node))
            else:
                self.edge_latencies.update({(dst_node, src_node): latency})
                self.edge_latencies.update({(src_node, dst_node): latency})

            for neighbor in self.neighbors:
                if neighbor != msg_src:
                    self.send_to_neighbor(neighbor, json.dumps([src_node, dst_node, latency, time_stamp, self.id]))
        else:
            # send the newest msg to node which sends the old one
            if time_stamp < self.edge_m_timestamps.get((dst_node,src_node)):
                self.send_to_neighbor(msg_src, json.dumps([src_node, dst_node, self.edge_latencies.get((src_node,dst_node)), self.edge_m_timestamps.get((src_node,dst_node)), self.id]))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # return -1
        #Initialization
        dist = {}
        prev = {}
        Q = self.get_all_nodes() # The list of the “unvisited”vertices.
        for v in Q:
            dist[v] = sys.maxsize # Unknown distance from source to v.
            prev[v] = None # Previous node in optimal path from source.
        dist[destination] = 0 # Distance from source to itself is zero.

        # “visit” the closest unvisited vertex, u
        while Q:
            minimum_dist = sys.maxsize
            u = Q[0] # u := vertex in Q with minimum dist[u]
            for v in Q:
                if dist.get(v) < minimum_dist:
                    minimum_dist = dist.get(v)
                    u = v
            Q.remove(u)
            # try using u to make shorter paths
            for v in self.get_neighbors(u):
                alt = dist[u] + self.edge_latencies.get((u, v))
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u

        return prev.get(self.id)

    def get_neighbors(self, node):
        ret = []
        for node_1, node_2 in self.edge_latencies.keys():
            if node_1 == node and node_2 not in ret:
                ret.append(node_2)
            if node_2 == node and node_1 not in ret:
                ret.append(node_1)

        return ret

    def get_all_nodes(self):
        ret = []
        for node_1, node_2 in self.edge_latencies.keys():
            if node_1 not in ret:
                ret.append(node_1)
            if node_2 not in ret:
                ret.append(node_2)

        return ret
