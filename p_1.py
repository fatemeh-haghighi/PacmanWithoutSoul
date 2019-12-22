import copy
from operator import attrgetter
import heapq
import time 
import matplotlib.pyplot as plt
# function to find place of a character
def find_place(character, lines):
    location = []
    for counter in range(len(lines)):
        for i in range(len(lines[counter])):
            if lines[counter][i] == character:
                location.append((counter, i))
                lines[counter][i] = ' '
    return location


# reading map file
file_path = '/home/fatemeh/Documents/semester_7/AI/p_1/test_cases/test2'
# file_path = 'in.txt'
file = open(file_path,'r')

# spliting data of file
data = file.read().split('\n')
for i in range(len(data)):
    data[i] = list(data[i])

# initializing list based on locations
fruit_p = find_place('1', data)
fruit_q = find_place('2', data)
shared_fruit = find_place('3', data)
q_location = find_place('Q', data)[0]
p_location = find_place('P', data)[0]
visited_nodes = []


def calculate_manhatan_distance(location1, location2):
    return abs((location1[0] - location2[0]) + (location1[1] - location2[1]))



class State:
    def __init__(self, q_location, p_location, fruit_p, fruit_q, shared_fruit, path_cost, huristic):
        self.q_location = q_location
        self.p_location = p_location
        self.fruit_p = copy.deepcopy(fruit_p)
        self.fruit_q = copy.deepcopy(fruit_q)
        self.shared_fruit = copy.deepcopy(shared_fruit)
        self.path_cost = path_cost
        self.evaluation = huristic + path_cost

    def __eq__(self , other):
        return hash(self) == hash(other)
   

    def __lt__(self, other):
        return self.evaluation < other.evaluation


    def calculate_huristic(self, agnt):
        distance = 0
        if agnt == 'P':
            for i in range(len(fruit_p)):
                j = i + 1
                if j < len(fruit_p):
                    distance = max(calculate_manhatan_distance(fruit_p[i], fruit_p[j]) , distance)
        if agnt == 'Q':
            for i in range(len(fruit_q)):
                j = i + 1
                if j < len(fruit_q):
                    distance = max(calculate_manhatan_distance(fruit_q[i], fruit_q[j]) , distance)
        for i in range(len(shared_fruit)):
            j = i + 1
            if j < len(shared_fruit):
                distance = max(calculate_manhatan_distance(shared_fruit[i], shared_fruit[j]) , distance)
        return distance
    
    def get_huristic(self):
        return min(self.calculate_huristic('P'), self.calculate_huristic('Q'))        # return 0
                


    

    def update(self, new_obj, location, agnt):
        if (location[0], location[1]) in self.fruit_p:
            index = new_obj.fruit_p.index((location[0], location[1]))
            del new_obj.fruit_p[index]
        elif (location[0], location[1]) in self.fruit_q:
            index = new_obj.fruit_q.index((location[0], location[1]))
            del new_obj.fruit_q[index]
        elif (location[0], location[1]) in self.shared_fruit:
            index = new_obj.shared_fruit.index((location[0], location[1]))
            del new_obj.shared_fruit[index]
        if agnt == 'P':
            new_obj.p_location = location
        elif agnt == 'Q':
            new_obj.q_location = location
        new_obj.path_cost = self.path_cost + 1
        new_obj.evaluation = new_obj.path_cost + new_obj.get_huristic()
        return new_obj


    def is_child_valid(self, location0, location1, poison):
        if ((location0, location1) in poison) or (data[location0][location1] ==  '%'):
            return "no"
        else:
            return "yes"
    
    def valid_childs(self , obj, poison, agnt):
        childs = []
        for i in range(4):
            # 0 : down, 1: up , 2: right, 3: left
            if i == 0: 
                if self.is_child_valid(obj[0] + 1, obj[1], poison) == "yes":
                    child_obj = copy.deepcopy(self)
                    childs.append(self.update(child_obj, (obj[0] + 1, obj[1]), agnt))

            elif i == 1:
                if self.is_child_valid(obj[0] - 1, obj[1], poison) == "yes":
                    child_obj = copy.deepcopy(self)
                    childs.append(self.update(child_obj, (obj[0] - 1, obj[1]), agnt))

            elif i == 2:
                if self.is_child_valid(obj[0] , obj[1] + 1, poison) == "yes":
                    child_obj = copy.deepcopy(self)
                    childs.append(self.update(child_obj, (obj[0], obj[1] + 1), agnt))

            else:
                if self.is_child_valid(obj[0] , obj[1] - 1, poison) == "yes":
                    child_obj = copy.deepcopy(self)
                    childs.append(self.update(child_obj, (obj[0], obj[1] - 1), agnt))

        return childs
        
            


    def expand(self):
        child1 = self.valid_childs(self.p_location, self.fruit_q, 'P')
        child2 = self.valid_childs(self.q_location, self.fruit_p, 'Q')
        return child1 + child2
    
    def is_goal_state(self):
        if len(self.fruit_p) == 0 and len(self.fruit_q) == 0 and len(self.shared_fruit) == 0:
            return "yes"
        else:
            return "no"

    def __hash__(self):
        a = ()
        a += self.p_location
        a += self.q_location
        for element in (self.shared_fruit + self.fruit_p + self.fruit_q) : 
            a += element
        return hash(a)


def checkKey(dict, key):
    if key in dict:
        return 'present'
    else:
        return 'not present'

def breadth_first_search(initial_node):
    counter = 0
    seperate_state = 0
    frontier = []
    explored = {}
    if initial_node.is_goal_state() == "yes":
        return initial_node, len(explored), seperate_state
    else:
        frontier.append(initial_node)
        explored.update({initial_node:counter})
        while(True):
            if len(frontier) == 0:
                return "failure", len(explored), seperate_state
            else:
                childs = frontier[0].expand()
                del frontier[0]
                seperate_state += 1
                for node in childs:
                    if checkKey(explored, node) == "not present":
                        if node.is_goal_state() == "yes":
                            return node, len(explored), seperate_state
                        else:
                            counter += 1
                            explored.update({node : counter})
                            frontier.append(node)
                            print("current explore length is : ", len(explored))



def depth_first_search(initial_node , depth):
    separate_state = 0
    counter = 0
    frontier = []
    explored = {}
    frontier.append(initial_node)
    explored.update({initial_node:counter})
    if initial_node.is_goal_state() == "yes":
        return initial_node, len(explored), separate_state
    while (True):
        if len(frontier) == 0:
            return "failure", len(explored), separate_state
        else:
            if frontier[-1].is_goal_state() == "yes" : 
                return frontier[-1] , len(explored), separate_state
            if frontier[-1].path_cost == depth :
                del frontier[-1]
                separate_state += 1
                continue
            childs = frontier[-1].expand()
            del frontier[-1]
            separate_state += 1
            for child in childs : 
                if checkKey(explored, child) == "not present":
                    frontier.append(child)
                    explored.update({child:counter})
                    counter += 1
                    print("current explore length is : ", len(explored))



def iterative_deepening_search(initial_state):
    for i in range(9999):
        node , explored_length, separate_state = depth_first_search(initial_state , i)
        if node != "failure" : 
            return node , explored_length, separate_state
    print("failure")


def find_min_evaluation(li):
    vi = 0
    for i in range(1, len(li)):
        if li[i].evaluation < li[vi].evaluation:
            vi = i
    return vi

def a_star(initial_node):
    separate_state = 0
    frontier = []
    explored = {}
    if initial_node.is_goal_state() == "yes":
        return initial_node, len(explored), separate_state
    frontier.append(initial_node)
    while(len(frontier)):
        min_index = find_min_evaluation(frontier)
        if frontier[min_index].is_goal_state() == "yes":
            return frontier[min_index], len(explored), separate_state
        else:
            print("explored number: ", len(explored))
            childs =  frontier[min_index].expand()
            explored.update({frontier[min_index]:0})
            frontier.pop(min_index)
            separate_state += 1
            for child in childs:
                if checkKey(explored, child) == "not present":
                    if not child in frontier:
                        frontier.append(child)
                    else:
                        if child < frontier[frontier.index(child)] :
                            frontier.pop(frontier.index(child))
                            separate_state += 1
                            frontier.append(child)
    return "failure", len(explored), separate_state
    


e = State(q_location, p_location, fruit_p, fruit_q, shared_fruit, 0, 0)


def call_in_time(function, initial_node):
    time_summation = 0
    for i in range(3):
        start_time = time.time()
        out, num, separate_state = function(initial_node)
        end_time = time.time()
        time_summation += (end_time - start_time)
    time_summation = time_summation /3
    return time_summation , num, out.path_cost, separate_state


# test
time , number, cost, separate_state = call_in_time(a_star,e)
print("number of visited is : ", number)
print("time of execution is : ", time)
print("cost of solution is: ", cost)
print("separate state number is : ", separate_state)
