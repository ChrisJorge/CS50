import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    # directory = sys.argv[1] if len(sys.argv) == 2 else "large"
    directory = 'small'

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    Frontier = QueueFrontier() # Initialize the Frontier which will be used in the problem.
    VisitedFrontier = set() # Initialize a set of all seen movie person pairs
    GoalFound = False
    Element = 1
    # print(neighbors_for_person(source))

    AllPaths = neighbors_for_person(source) # Get all possible paths from the source ID
    for path in AllPaths: # Loop through all given paths
        NextNode = Node(path,None,None) # Create a Node
        Frontier.add(NextNode) # Add the Node to the Frontier

    while Frontier.empty() == False: # Stay inside the loop while the frontier is not empty
        if Element != 1:
            PastElement = Element # Save the past element
            Element = Frontier.remove() # Remove the first element from the queue
            PastElement.action(Element) # Set the previous elements action as the new element
        else:
            Element = Frontier.remove() # Remove the first element from the queue

        VisitedFrontier.add((Element.state)) # Add the state to the Visited Frontier
       
        AllPaths = neighbors_for_person(Element.state[1]) # Get all possible paths from the current node
        for path in AllPaths: # Loop through all given paths
            NextNode = Node(path,Element,None) # Create a Node
            if NextNode.state[1] == target: # Check if the Person ID of the nodes state is equal to the target Person ID
                GoalFound = True
                break # Break out of the loop
            if NextNode.state in VisitedFrontier == False:
                Frontier.add(NextNode) # Add the Node to the Frontier
            
        if GoalFound:
            ans = [] # Initialize an empty list
            while NextNode.parent: # Loop through while the nodes have a parent 
                print(NextNode.state)
                print(NextNode.parent)
                ans.append(NextNode.state)
                NextNode = NextNode.parent
            # ans.append(NextNode.state)
            ans.reverse()
            return ans
    
    raise Exception('No Link Found')


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
