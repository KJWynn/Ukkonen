"""
Name: Khor Jia Wynn
Student ID: 33033919
"""
import sys

def dfs(node, array, strLength, root):
    """
    Depth first lexicographical traversal of tree, returning a list of visited leaves. 
    Lexicographical traversal is possible because the edges of a node are in an array indexed by ASCII range 36 to 126, so when we iterate through
    the array, we are going by lexicographical order.
    """
    if node is None:
        return
    
    # If the current node is a leaf node, add its value to the visited leaves array
    if node.isLeaf and node != root:
        array.append(node.id)
    
    # Recursively traverse each child
    for edge in node.edges:
        if edge is not None:
            dfs(edge.tail, array, strLength, root)

    # once we have accumulated our leaf nodes, we can stop
    if len(array) == strLength:
        return array
    
    return array

def ukkonen(string):
    """
    Constructs the suffix tree using Ukkonen's algorithm. Returns the root of the constructed tree.
    Rule 2 is actually rule 2 case 1 in Ukkonen; Rule 3 is rule 2 case 2 in Ukkonen; Rule 4 is rule 3 in Ukkonen
    """

    n = len(string)

    # init variables, remainder, last_j, globalEnd
    remainder = (0,0)
    lastJ = 0
    globalEnd = [0]
    ruleUsed = None
    first = ord('a') # for naming intermediate nodes

    for i in range(1, n+1):
        globalEnd[0] += 1 # inhereht rule 1 extension
        pointer = globalEnd # pointer for ensuring updates across all leaf nodes

        # base case
        if i == 1:
            root = Node("r", True)
            firstNode = Node(1, True)
            char = string[0]
            root.edges[ord(char)-36] = Edge(root, firstNode, 1,pointer)
            activeNode = root
            lastJ += 1
            root.suffixLink = root
        else:
            # begin phase i+1 and do leaf extension
            j = lastJ+1
            # below three variables are for resolving suffix links
            oldInternalNode = None
            newInternalNode = None
            needToResolve = False 

            while j < i+1: # extensions
                if ruleUsed == 3: # if previous extension created internal node, save a copy of that internal node for resolving suffix link
                    oldInternalNode = newInternalNode 
                newInternalNode = None # reset because we don't know if this extension will create a new one
                ruleUsed = None # reset 

                # skip count, not needed if remainder = (0,0). 
                if remainder != (0,0):
                    remainderLength = remainder[1]-remainder[0]+1 # amount to traverse
                    counter = remainder[0] # used for checking first character of next edge when skipping
                    currEdge = activeNode.edges[ord(string[remainder[0]-1])-36] # first edge to examine
                    currEdgeLength = (currEdge.label[1][0]-currEdge.label[0])+1 # for the edge to be examined
                    cumulativeLength = 0 # total length of edges considered
                    exactAmount = False # this is to check if we traverse exactly the amount needed on current edge
                    while remainderLength >= (cumulativeLength + currEdgeLength):
                        activeNode = currEdge.tail # go to next node
                        counter += currEdgeLength # update next character to check 
                        currEdge = activeNode.edges[ord(string[counter-1])-36] # this is the next edge to be examined (if it exists)
                        if currEdge is not None: # next edge exists
                            cumulativeLength += currEdgeLength # update total traversed/skipped
                            currEdgeLength = (currEdge.label[1][0]-currEdge.label[0])+1 # update the next edge length to be considered
                        else:
                            exactAmount = True # traversed exact amount, so either rule 2 case 1 or rule 3
                            break
                    if exactAmount:
                        traverseAmount = 0
                    else:
                        traverseAmount = remainderLength-cumulativeLength # this is the remaining amount to traverse on the edge where extension occurs

                    # perform extension at extension point
                    if traverseAmount != 0: # we are halway through an edge
                        charPosition = currEdge.label[0] + traverseAmount - 1 # this is how we skip the traversal, by computing the char index to be checked
                        edgeChar = string[charPosition] 
                        if string[(i-1)]==edgeChar:
                            ruleUsed = 4
                        else: # rule 2 case 2
                            ruleUsed = 3
                            oldStart = currEdge.label[0] 
                            oldEndNode = currEdge.tail 
                            # create intermediate node inside old edge
                            intermediateNode = Node(chr(first), False)
                            first += 1 
                            newInternalNode = intermediateNode # used for resolving suffix links
                            # update old edge to end at this intermediate node      
                            newEnd = oldStart + traverseAmount - 1 # 1
                            newEdge = Edge(activeNode, intermediateNode, oldStart, [newEnd])
                            activeNode.edges[ord(string[oldStart-1])-36] = newEdge
                            # create new edge between intermediate node and new leaf node
                            newCharNode = Node(j, True) # create new leaf node for character 
                            newEdge = Edge(intermediateNode, newCharNode, pointer[0], pointer)
                            intermediateNode.edges[ord(string[pointer[0]-1])-36] = newEdge
                            # create new edge between intermediate node and old end node
                            remainderStart = currEdge.label[0]+traverseAmount
                            remainderEnd = currEdge.label[1][0]
                            if currEdge.tail.isLeaf: # if original end node, was leaf, it needs to remain a pointer to global end
                                newEdge = Edge(intermediateNode, oldEndNode, remainderStart, pointer)
                            else:
                                newEdge = Edge(intermediateNode, oldEndNode, remainderStart, [remainderEnd])
                            intermediateNode.edges[ord(string[remainderStart-1])-36] = newEdge
                            lastJ+=1 # for rule 2 extensions
                            remainder = (oldStart,newEnd) # update remainder for rule 2 case 2
                    else: # we are at a node, and traverse amount is 0
                        # update remainder since no more characters to traverse below active node to reach extension point
                        remainder = (0,0)
                        # check rule 3 
                        if activeNode.edges[ord(string[i-1])-36] is not None:
                            ruleUsed = 4
                        else: # rule 2 case 1
                            ruleUsed = 2
                            newNode = Node(j, True)
                            activeNode.edges[ord(string[i-1])-36] = Edge(activeNode, newNode, i, pointer)
                            lastJ+=1 # for rule 2 extensions                                                         
                
                else: # remainder is empty, meaning no skip counting; we directly apply extension rules, either rule 2 case 1 or rule 3
                    if activeNode.edges[ord(string[i-1])-36] is None:
                        ruleUsed = 2
                        newNode = Node(j, True)
                        activeNode.edges[ord(string[i-1])-36] = Edge(activeNode, newNode, i, pointer)
                        lastJ+=1
                    else:
                        ruleUsed = 4 # rule 3

               
                if ruleUsed == 4:
                    j = i+1 # terminate this phase
                    # add character str[i] to remainder 
                    if remainder == (0,0):
                        remainder = (i,i)
                    else:
                        remainder = (remainder[0], remainder[1]+1)
                else:
                    j+=1 # proceed to next extension normally

                # resolve suffix links
                if needToResolve:
                    if newInternalNode is None: # if no internal node created in this extension, suffix link points to active node
                        oldInternalNode.suffixLink = activeNode
                    else:
                        oldInternalNode.suffixLink = newInternalNode # the active node should be the new internal node


                needToResolve = (ruleUsed == 3) # boolean indicating if resolving is needed for next extension, rmb ruleUsed = 3 is rule 2 case 2 in actual Ukkonen

                # if rule 2 case 1/case 2
                if ruleUsed == 2 or ruleUsed == 3:
                    # if active node == root, then activeNode.suffixLink is also root, and this means we manually remove first char from remainder if active node is root
                    if activeNode == root:
                        if remainder[0] == remainder[1]: 
                            remainder = (0,0)
                        else:
                            remainder = (remainder[0]+1, remainder[1])
                    activeNode = activeNode.suffixLink # rule 2 extensions mean we should follow suffix link to the new activeNode for next extension

    return root


def suffix_array(node, strLength, root):
    """
    Uses depth first traveral of suffix tree to obtain its corresponding suffix array.
    """
    array = []
    array = dfs(node, array, strLength, root)
    return array

def rank_array(suffix_array):
    """
    Computes the rank array for suffixes. The ranks are indexed by the suffix ID, allowing O(1) access 
    """
    rank_array = [None for _ in range(len(suffix_array))]
    for i in range(len(suffix_array)):
        rank_array[suffix_array[i]-1] = i+1 # +1 because we use 1-based indexing
    return rank_array


class Node:
    """
    Node class for the suffix tree, contains an array of edges in lexicographical ordering. 
    """
    CHAR_RANGE = 126-36+1 #(94)
    def __init__(self, id, isLeaf):
        self.id = id
        self.isLeaf = isLeaf
        self.suffixLink = None
        self.edges = [None] * self.CHAR_RANGE

class Edge:
    """
    Edge class for the suffix tree. Contains compressed string label(tuple) and references to head and tail node for this edge
    """
    def __init__(self,head,tail, start,end):
        self.head = head
        self.tail = tail
        self.label = (start,end)

    def __str__(self):
        if self.tail is not None:
            arg1 = self.tail.id
        else:
            arg1 = "None"
        if self.head is not None:
            arg2 = self.head.id
        else:
            arg2 = "None"
        return str(arg2) + " " + str(self.label[0]) + " " + str(self.label[1][0]) + " " + str(arg1)
