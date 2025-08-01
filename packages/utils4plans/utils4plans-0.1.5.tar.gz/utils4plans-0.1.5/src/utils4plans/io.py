from pathlib import Path
import json
import pickle

import networkx as nx
from utils4plans.printing import StyledConsole

THROWAWAY_FOLDER = Path("/Users/julietnwagwuume-ezeoke/_UILCode/gqe-phd/fpopt/utils4plans/throwaway")

class NotImplementedError(Exception):
    pass

def make_json_name(name:str): return f"{name}.json"
def make_pickle_name(name:str): return f"{name}.pickle"


def check_folder_exists_and_return(p: Path):
    assert p.exists(), StyledConsole.print(f"Error: {p} does not exist", style="error")
    return p
    # TODO -> handle different behavior if doesnt exist.. 

def get_or_make_folder_path(root_path: Path, folder_name: str):
    # TODO try using pathlib's walk function instead.. 
    assert root_path.exists()
    path_to_outputs = root_path / folder_name
    if not path_to_outputs.exists():
        path_to_outputs.mkdir()
    return path_to_outputs

def error_if_file_exists(path: Path):
    if path.exists():  # TODO handle overwriting in a unified way..
        raise Exception(f"File already exists at {path} - try another name")
    return path

def append_if_file_exists(p: Path):
    pass


def deconstruct_path(path: Path):
    return (path.parent, path.name)

def write_graph(G: nx.Graph, folder_path:Path, name: str):
    G_json = nx.node_link_data(G, edges="edges")  # pyright: ignore[reportCallIssue]
    with open(folder_path / f"{name}.json", "w+") as file:
        json.dump(G_json, default=str, fp=file)


def read_graph(folder_path: Path, name: str):
    with open(folder_path / f"{name}.json", "r") as file:
        d = json.load(file)
    G: nx.Graph = nx.node_link_graph(d, edges="edges")  # pyright: ignore[reportCallIssue]
    return G


def write_pickle(item, folder_path: Path, file_name: str):
    path = error_if_file_exists(folder_path / make_pickle_name(file_name))
    with open(path, "wb") as handle:
        pickle.dump(item, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Wrote pickle to {path.parent} / {path.name}")


def read_pickle(folder_path: Path, file_name: str):
    with open(folder_path / f"{file_name}.pickle", "rb") as handle:
        result = pickle.load(handle)
    return result


def write_json(item, folder_path: Path, file_name: str):
    path = error_if_file_exists(folder_path / make_json_name(file_name))
    with open(path, "w+") as handle:
        json.dump(item, handle)
    print(f"Wrote to {path}")


def read_json(path_to_inputs: Path, file_name):
    path = check_folder_exists_and_return(path_to_inputs / make_json_name(file_name))
    assert path.suffix == ".json"

    with open(path) as f:
        res = json.load(f)
    return res




if __name__ == "__main__":
    obj = {"hi": 10, "bye":[1,2,3,4], "see": {"hi": "bye", 10: None}}
    write_json(obj, THROWAWAY_FOLDER, "test1")
    r = read_json(THROWAWAY_FOLDER, "test1")
    print(r)




