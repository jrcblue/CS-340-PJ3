from simulator.node import Node
import copy
import json
import numpy as np
class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.local_dv = {}
        self.neighbors_dv_table = {}
        self.neighbors_seq = {}
        self.seq_num = 0
        self.neighbors_cost = {}
    # Return a string
    def __str__(self):
        return str(self.id)

    def dv_update(self, new_dv):
        for i in self.neighbors:  # every neighbor
            # except the new added neighbor
            i = str(i)
            if i in self.neighbors_dv_table.keys():
                # every dv in every neighbor
                for j in self.neighbors_dv_table[i].keys():
                    # no cycle
                    if self.id not in self.neighbors_dv_table[i][j][1]:
                        # new destination
                        if j not in new_dv:
                            # update cost and as_path
                            new_dv[j] = [self.neighbors_dv_table[i][j][0] + new_dv[i][0], new_dv[i][1] + self.neighbors_dv_table[i][j][1]]
                        else:
                            # update existing cost and path
                            if (new_dv[i][0] + self.neighbors_dv_table[i][j][0]) < new_dv[j][0]:
                                new_dv[j] = [self.neighbors_dv_table[i][j][0] + new_dv[i][0],new_dv[i][1] + self.neighbors_dv_table[i][j][1]]
        return new_dv
    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):

        #    new_dv[str(key)] = [self.local_dv[str(key)][0], self.local_dv[str(key)][1]]
        if neighbor not in self.neighbors:
            #new node
            self.neighbors.append(neighbor)
            self.neighbors_cost[str(neighbor)] = [latency, [neighbor]]
            new_dv = copy.deepcopy(self.neighbors_cost)
        elif latency == -1:
            #delete node
            self.neighbors.remove(neighbor)
            self.local_dv.pop(str(neighbor))
            self.neighbors_dv_table.pop(str(neighbor))
            self.neighbors_cost.pop(str(neighbor))
            new_dv = copy.deepcopy(self.neighbors_cost)
        else:
            self.neighbors_cost[str(neighbor)] = [latency, [neighbor]]
            new_dv = copy.deepcopy(self.neighbors_cost)
            new_dv = self.dv_update(new_dv)

        # only when new DV changes, update and send it to neighbors
        if self.local_dv != new_dv:
            self.local_dv = new_dv
            msg = json.dumps([self.id, self.seq_num, self.local_dv])
            self.seq_num += 1
            self.send_to_neighbors(msg)


    # Fill in this function
    def process_incoming_routing_message(self, m):
        id, seq_num, dv = json.loads(m)
        # if new node
        if id not in self.neighbors_seq.keys():
            #print('new message from new node')
            self.neighbors_seq[id] = seq_num
            self.neighbors_dv_table[str(id)] = dv
        # existing node but new message
        elif seq_num > self.neighbors_seq[id]:
            #print('update')
            self.neighbors_seq[id] = seq_num
            self.neighbors_dv_table[str(id)] = dv
        #old seq
        else:
            #print('pass')
            return
        new_dv = copy.deepcopy(self.neighbors_cost)
        new_dv = self.dv_update(new_dv)
        if self.local_dv != new_dv:
            self.local_dv = new_dv
            msg = json.dumps([self.id,  self.seq_num,self.local_dv])
            self.seq_num += 1
            self.send_to_neighbors(msg)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        if str(destination) in self.local_dv.keys():
            return self.local_dv[str(destination)][1][0]
        else:
            return -1