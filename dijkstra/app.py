from flask import Flask, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerRangeField, SelectField

from math import inf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aoi01ngoaus82'

# HeapPriorityQueue is a required supporting class for the dijkstra capabilities of the graph

class HeapPriorityQueue():

    def __init__(self, capacity):

        self.__data = [(None, inf)] + [(None, -inf)] * capacity
        self.__end_index = 0

    def is_empty(self):

        return self.__end_index == 0
    
    def top(self):

        if self.is_empty():

            raise Exception("Cannot access top of empty priority queue")
        
        return self.__data[1][0]

    def __enqueue_single(self, item, priority):

        self.__end_index += 1

        if self.__end_index == len(self.__data):

            raise Exception("Cannot enqueue to queue beyond capacity")

        self.__data[self.__end_index] = (item, priority)

        problem_index = self.__end_index

        while self.__data[problem_index][1] > self.__data[problem_index//2][1]:

            temp = self.__data[problem_index]

            self.__data[problem_index] = self.__data[problem_index//2]

            self.__data[problem_index//2] = temp

            problem_index //= 2
    
    def enqueue(self, *items):

        for item in items:

            self.__enqueue_single(item[0], item[1])

    def dequeue(self):

        item = self.top()

        self.__data[1] = self.__data[self.__end_index]
        self.__data[self.__end_index] = (None, -inf)

        problem_index = 1

        max_priority = -inf

        max_index = 1
        
        for index in [problem_index, problem_index * 2, problem_index * 2 + 1]:

            if index < len(self.__data):

                if self.__data[index][1] > max_priority:

                    max_priority = self.__data[index][1]
                    max_index = index

        while max_index != problem_index:

            temp = self.__data[max_index]
            self.__data[max_index] = self.__data[problem_index]
            self.__data[problem_index] = temp

            problem_index = max_index

            max_priority = -inf

            max_index = 1
            
            for index in [problem_index, problem_index * 2, problem_index * 2 + 1]:

                if index < len(self.__data):

                    if self.__data[index][1] > max_priority:

                        max_priority = self.__data[index][1]
                        max_index = index
        
        self.__end_index -= 1
        
        return item

class GraphDB():

    '''
    Modularily designed, with multiple instances and stored databases in mind.
    '''

    def __init__(self, n, edges=None, names=None):

        self.__num_vertices = n
        if names is None:

            names = [None] * n
        self.__vertices = [names[i] if names[i] is not None \
                        else i for i in range(n)]
        self.__name_indeces = {names[i]:i for i in range(n) \
                        if names[i] is not None}
        if edges is None:

            self.__edges = {}
        
        else:

            self.__edges = {(edge[0],edge[1]):edge[2] for edge in edges}
    
    def add_node(self, name=None, connections=None):

        '''
        CAUTION: UNDEFINED BEHAVIOUR MAY OCCUR IF NAME IS NOT A STRING
        '''

        if name is None:
            
            name = self.__num_vertices
        
        else:

            self.__name_indeces[name] = self.__num_vertices
        
        self.__num_vertices += 1

        self.__vertices += [name]

        if connections is not None:

            for other, weight in connections:

                self.add_edge(name, other, weight)
    
    def update_edge(self, a, b, w):

        a_index = self.get_node_index(a)
        b_index = self.get_node_index(b)

        if a_index is None:

            self.add_node(a)
        
        if b_index is None:

            self.add_node(b)
        
        self.__edges[(a,b)] = w
    
    def edge_exists(self, a, b):

        return (a,b) in self.__edges
    
    def get_node_index(self, node):

        if not isinstance(node, int):

            if node in self.__name_indeces:

                return self.__name_indeces[node]
            
            return None
        
        if node < self.__num_vertices:

            return node
        
        return None

    def adj_list(self):

        l = [[] for _ in range(self.__num_vertices)]

        for edge in self.__edges:

            l[edge[0]].append((edge[1], self.__edges[edge]))
        
        for connections in l:

            connections.sort(key = lambda arr: arr[0])
        
        return l

    def dijkstra(self, start=0, end=None):

        print(start, end)

        visit_q = HeapPriorityQueue(len(self.__edges))

        adj_list = self.adj_list()

        print(adj_list)

        distances = [inf] * self.__num_vertices
        distances[start] = 0

        parents = [None] * self.__num_vertices

        final = [False] * self.__num_vertices

        visit_q.enqueue((start, 0))

        while not visit_q.is_empty():

            current = visit_q.dequeue()

            for adj in adj_list[current]:

                print(current, adj)

                if not final[adj[0]]:

                    print(distances[current] + adj[1] , distances[adj[0]])

                    if distances[current] + adj[1] < distances[adj[0]]:

                        distances[adj[0]] = distances[current] + adj[1]

                        visit_q.enqueue((adj[0], -distances[adj[0]]))
                        # Negative ensures the highest priority is the lowest distance
                        
                        parents[adj[0]] = current

            final[current] = True

            print(current, end)

            if current == end:

                distance = distances[current]

                path = [current]

                while path[0] is not None:

                    print(path)

                    path = [parents[current],] + path

                    current = parents[current]
                
                return distance, path[1:]
        
        return distances, parents

class ModifyWeightForm(FlaskForm):

    edge_one_id = IntegerRangeField()
    #edge_one_name = SelectField()
    edge_two_id = IntegerRangeField
    #edge_two_name = SelectField()


@app.route('/')
def home():

    return ''''''


g = GraphDB(4, edges=((0,1,5),(1,2,3),(2,3,10),(3,0,1),(0,2,3),(1,3,8)))

print(g.dijkstra())
print(g.dijkstra(1,0))