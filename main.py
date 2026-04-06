# from renderer import Renderer
from parser import Parser
from dijkstra import Dijkstra

def main() -> None:
    # renderer: Renderer = Renderer()
    # renderer.setup()
    # renderer.run()
    parser: Parser = Parser("maze_nigh.txt") 
    graph = parser.parse()
    if graph:
        graph.log_graph()
    
    dij: Dijkstra = Dijkstra()
    path =  dij.path(graph)
    print()
    print()
    print("####################PATH#######################")
    for node in path:
        print("Node: ", node)

if __name__ == '__main__':
    main()
