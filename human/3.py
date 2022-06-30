from data3 import data2 as data #i cant believe you've done this
from collections import deque


#bfs on implicit graph (set of nodes, grid)
def bfs_implicit(grid, start, end):
    queue=deque([n for n in start])
    visited={n for n in start}#when there are more than one start node
    prev={n:None for n in start}
    found_end=None
    while queue:
        node=queue.popleft()
        if node in end:
            found_end=node
            break
        for n in neighbors(node, grid):
            if n not in visited:
                queue.append(n)
                visited.add(n)
                prev[n]=node
    out=[]
    while found_end:
        out.append(found_end)
        if found_end in prev:
            found_end=prev[found_end]
        else:
            break
    out.reverse()
    return out

def neighbors(node, grid):
    x,y=node
    for pos in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
        if pos in grid:
            yield pos

class multiend:#for passing into end
    def __init__(self, endlist):
        self.endlist=endlist
    def __contains__(self, item):
        return item in self.endlist

#data is a list containing paths of the kind:
#[(startx,starty),["U","D","L","R","?"]]
#where "?" is an optional end character:
#"X" = wall
#"F" = finish (there can be multiple finishes)
#"S" = starting point (there can be multiple starts)
#any cell that a path passes through is considered to be a valid empty cell.
#it is possible to traverse from an empty cell to an empty cell if they are adjacent.
#find a path from any starting point to any finishing point.

#convert data to grid (set)
grid=set()
finish=set()
walls=set()
starts=set()
for path in data:
    curr=path[0]
    grid.add(curr)
    for move in path[1]:
        if move=="U":
            curr=(curr[0],curr[1]-1)
        elif move=="D":
            curr=(curr[0],curr[1]+1)
        elif move=="L":
            curr=(curr[0]-1,curr[1])
        elif move=="R":
            curr=(curr[0]+1,curr[1])
        else:
            if move=="X":
                grid.remove(curr)
            elif move=="F":
                finish.add(curr)
            elif move=="S":
                starts.add(curr)
            continue #reached end
        grid.add(curr)


#debug
# grid.add((53,13))
# walls.add((53,13))

# print(grid)
#dimensions
xmax=max(x for x,y in grid)
xmin=min(x for x,y in grid)
ymax=max(y for x,y in grid)
ymin=min(y for x,y in grid)
for x in range(xmin,xmax+1):
    for y in range(ymin,ymax+1):
        if (x,y) in grid:
            if (x,y) in walls:
                print("X",end="")
            elif (x,y) in finish:
                print("F",end="")
            elif (x,y) in starts:
                print("S",end="")
            else:
                print("#",end="")
        else:
            print(".",end="")
    print()
# print("({0},{1}) to ({2},{3})".format(xmin,ymin,xmax,ymax))

#debug
# print((105,13)in multiend(finish))
print(starts)

def nodes_to_path(nodes):
    out=[]
    curr=nodes[0]
    for n in nodes[1:]:
        if n[0]==curr[0]:
            if n[1]>curr[1]:
                out.append("D")
            else:
                out.append("U")
        elif n[1]==curr[1]:
            if n[0]>curr[0]:
                out.append("R")
            else:
                out.append("L")
        else:
            raise Exception("nodes not adjacent")
        curr=n
    return "".join(out)

print(nodes_to_path(bfs_implicit(grid, starts, multiend(finish))))