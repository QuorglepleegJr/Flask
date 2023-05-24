from flask import Flask, request, session, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, validators, ValidationError

from math import inf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aoi01ngoaus82'

'''Backend'''

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

    def get_num_vertices(self):

        return self.__num_vertices
    
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

    def node_exists(self, node):

        return self.get_node_index(node) is not None
    
    def get_node_index(self, node):

        if not isinstance(node, int):

            if node in self.__name_indeces:

                return self.__name_indeces[node]
            
            return None
        
        if node < self.__num_vertices and node >= 0:

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

'''Front end'''

# Form Requirements

class ModifyWeightForm(FlaskForm):

    edge_one_id = IntegerField(label="Edge start ID:",validators=[validators.InputRequired()])
    edge_two_id = IntegerField(label="Edge end ID:",validators=[validators.InputRequired()])
    weight = IntegerField(label="Weight:",validators=[validators.NumberRange(min=0), validators.InputRequired()])
    submit = SubmitField(label="Modify")

# Routes

@app.route('/')
def home():

    return render_template("home.html")

@app.route('/success')
def success():

    if 'last_action' in session:

        print(app.graph.adj_list())

        return render_template("success.html", action=session['last_action'])
    
    return redirect(url_for("home"))

@app.route('/mod', methods=['GET','POST'])
def modify():

    modify_weight_form = ModifyWeightForm()

    if modify_weight_form.is_submitted():

        a = modify_weight_form.edge_one_id.data
        b = modify_weight_form.edge_two_id.data

        for node_input in (a,b):

            if not app.graph.node_exists(node_input):

                return render_template("mod.html", form=modify_weight_form, \
                    error=f"One or more endpoint of the edge is not a valid node ID, \
                        must be between 0 and {app.graph.get_num_vertices()}")

        w = modify_weight_form.weight.data

        if not isinstance(w, int) or w < 0:

            return render_template("mod.html", form=modify_weight_form, \
                    error=f"The weight must be a non-negative integer.")

        app.graph.update_edge(a, b, w)

        session['last_action'] = f"Edge between {a} and {b} set to weight {w}"

        return redirect(url_for("success"))

    return render_template("mod.html", form=modify_weight_form, error="")


if __name__ == "__main__":

    app.graph = GraphDB(4, edges=((0,1,5),(1,2,3),(2,3,10),(3,0,1),(0,2,3),(1,3,8)))
    app.run()
