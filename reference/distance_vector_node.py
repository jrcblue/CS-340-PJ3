from simulator.node import Node
import copy
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {}
        self.direct_link_cost = {}
        self.neighbors_dv_set = {}
        self.neighbors_dv_seq = {}
        self.seq = 0

    # Return a string
    def __str__(self):
        # return "Rewrite this function to define your node dump printout"
        return str(self.id) + "\n"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link

        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            self.direct_link_cost.pop(str(neighbor))
            self.dv.pop(str(neighbor))
            self.neighbors_dv_set.pop(neighbor)
        else:
            if neighbor not in self.neighbors:
                # add a new neighbor in to self.neighbors
                self.neighbors.append(neighbor)
            # update the direct link cost
            self.direct_link_cost.update({str(neighbor): [latency, neighbor]})
        # use direct link as candidate DV at first
        candidate_dv = copy.deepcopy(self.direct_link_cost)
        for i in self.neighbors:  # find neighbors' DV
            # print(i)
            if i in self.neighbors_dv_set.keys():
                for j in self.neighbors_dv_set[i]:  # neighbor i's DV
                    # neighbor i's DV has a destination that isn't in my DV list and not myself either.
                    if (j not in candidate_dv) and (self.id not in self.neighbors_dv_set[i][j][1:]):
                        # add this destination and cost to my candidate DV
                        candidate_dv.update({j: [0, 0]})
                        candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                        candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]
                    # neighbor i's DV has a destination that is also in my DV list.
                    elif self.id not in self.neighbors_dv_set[i][j][1:]:
                        # compare the cost and update my candidate DV
                        if (self.direct_link_cost[str(i)][0] + self.neighbors_dv_set[i][j][0]) < candidate_dv[j][0]:
                            candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                            candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]
        # if my DV changes, I update it and send it to my neighbors
        if self.dv != candidate_dv:
            self.dv = candidate_dv
            msg = json.dumps([self.id, self.dv, self.seq])
            self.seq += 1
            self.send_to_neighbors(msg)
        print(self.id,':',self.dv)

    # Fill in this function
    def process_incoming_routing_message(self, m):
        new_dv_node, new_dv, seq = json.loads(m)
        if new_dv_node not in self.neighbors_dv_seq:
            self.neighbors_dv_seq.update({new_dv_node: seq})
            self.neighbors_dv_set.update({new_dv_node: new_dv})
        elif seq > self.neighbors_dv_seq[new_dv_node]:
            self.neighbors_dv_seq.update({new_dv_node: seq})
            self.neighbors_dv_set.update({new_dv_node: new_dv})
        else:
            return
        candidate_dv = copy.deepcopy(self.direct_link_cost)
        for i in self.neighbors:
            if i in self.neighbors_dv_set.keys():
                for j in self.neighbors_dv_set[i]:
                    if (j not in candidate_dv) and (self.id not in self.neighbors_dv_set[i][j][1:]):
                        candidate_dv.update({j: [0, 0]})
                        candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                        candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]
                    elif self.id not in self.neighbors_dv_set[i][j][1:]:
                        if (self.direct_link_cost[str(i)][0] + self.neighbors_dv_set[i][j][0]) < candidate_dv[j][0]:
                            candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                            candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]
        if self.dv != candidate_dv:
            self.dv = candidate_dv
            msg = json.dumps([self.id, self.dv, self.seq])
            self.seq += 1
            self.send_to_neighbors(msg)
        print(self.id, ':', self.dv)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return self.dv[str(destination)][1]

