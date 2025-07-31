import os
import subprocess
from collections import defaultdict
import re
from collections import deque
from .game import PDDLGame
import os
import contextlib
import time

current_directory = os.path.dirname(os.path.abspath(__file__))

class State:
    def __init__(self, propositions, description, edges, acceptance_group):
        self.propositions = propositions
        self.description = description
        self.edges = edges
        self.acceptance_group = acceptance_group
    
    def __repr__(self):
        return f'{self.description}; {self.propositions}; {self.acceptance_group}; {self.edges}'
    
    def __str__(self):
        return self.description
    
    def __hash__(self):
        return hash(self.description)
    
    def __eq__(self, other):
        return self.description == other.description

def _generate_game_graph_edges(game):
    """
    Generates the full game graph for a 3x2 grid flipping game.
    Each state is represented as a 6-character string of 0s and 1s.
    Returns a dictionary mapping each state to a list of states reachable in one move.
    """
    # Generate physical states (2^6 = 64 states)
    # Use BFS to enumerate all reachable physical states from the starting state

    queue = deque()
    game_graph = defaultdict(set)
    queue.append(game)
    start_time = time.time()
    accesses = 0
    while queue:
        game = queue.popleft()
        successors = game.get_successors()
        if not successors:
            game_graph[game].add(game)
        for succ in successors:
            accesses += 1
            game_graph[game].add(succ)
            if succ not in game_graph:
                game_graph[succ] = set()
                queue.append(succ)
                print(f'{len(game_graph)} states explored at {len(game_graph)/(time.time()-start_time):.1f} states/s and {accesses/(time.time()-start_time):.1f} accesses/s\r', end='', flush=True)
    print()
    return game_graph

def _get_state_objects(game):
    adj_list = _generate_game_graph_edges(game)
    start_state = game
    #generate state ordering

    state_ordering = [start_state]
    state_ordering_dict = {start_state: 0}
    for state in adj_list.keys():
        if state != start_state:
            state_ordering_dict[state] = len(state_ordering)
            state_ordering.append(state)
    

    states = []
    atomic_propositions = list(start_state.get_propositions().keys())
    prop_to_idx = {prop:i for i, prop in enumerate(atomic_propositions)}
    for state in state_ordering:
        prop_bools = state.get_propositions()
        props = [f'{prop_to_idx[prop]}' if prop_bools[prop] else f'!{prop_to_idx[prop]}' for prop in prop_bools]
        
        description = repr(state)

        # TODO: acceptence groups
        if state.is_winning_state:
            acceptance_group = ['2']
        else:
            acceptance_group = ['1']

        new_state = State(set(props), description, set(state_ordering_dict[neighbor] for neighbor in adj_list[state]), acceptance_group)
        states.append(new_state)

    return states, atomic_propositions

def format_hoa(game):
    states, atomic_propositions = _get_state_objects(game)

    header=_generate_hoa_header(states, atomic_propositions)
    state_labeled_body, edge_labeled_body=_generate_hoa_body(states)
    return header + state_labeled_body, header + edge_labeled_body



def _generate_hoa_body(states):
    state_labeled_body = '--BODY--\n'
    edge_labeled_body = '--BODY--\n'

    for i, state in enumerate(states):
        edge_labeled_body += f'State: {i} "{state.description}"\n'
        for neighbor in state.edges:
            neighbor_state = states[neighbor]
            props_to_add = neighbor_state.propositions-state.propositions
            # assert len(props_to_add) >0, f'{state.description} {neighbor_state.description}'
            if props_to_add:
                edge_labeled_body+=f'\t[{" & ".join(props_to_add)}] {neighbor} {{{" ".join(neighbor_state.acceptance_group)}}}\n'
            else:
                edge_labeled_body+=f'\t[t] {neighbor} {{{" ".join(neighbor_state.acceptance_group)}}}\n'
        
        state_labeled_body += f'State: [{" & ".join(state.propositions)}] {i} "{state.description}" {{{" ".join(state.acceptance_group)}}}\n'
        state_labeled_body += f'\t{" ".join([str(edge) for edge in state.edges])}\n'

    edge_labeled_body += '--END--'
    state_labeled_body += '--END--'
    return state_labeled_body, edge_labeled_body


def _generate_hoa_header(states, atomic_propositions):
    header = f"HOA: v1\n"
    header += f'States: {len(states)}\n'
    header += f'Start: 0\n'
    header += f'AP: {len(atomic_propositions)} ' + " ".join([f'"{prop}"' for prop in atomic_propositions]) + "\n"
    header += f'acc-name: parity max even 3\n'
    header += f'Acceptance: 3 Inf(2) | (Fin(1) & Inf(0))\n'
    # header += f'properties: trans-labels explicit-labels trans-acc deterministic\n'
    header += f'spot-state-player: {" ".join(["1" if "6" in state.propositions else "1" for state in states])}\n'

    return header



def _get_strategy_string_from_cosmo(edge_labeled_hoa):
    """
    Runs the 'cosmo' tool with the given edge-labeled HOA file as input,
    and returns the resulting strategy string (stdout as a string).
    """
    try:
        # Run cosmo, passing the file as stdin
        result = subprocess.run(
            ['cosmo'],
            # stdin=edge_labeled_hoa,
            input=edge_labeled_hoa,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        raise RuntimeError("The 'cosmo' executable was not found in your PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"cosmo failed: {e.stdout}")

def _parse_strategy_string(strategy_string):
    """
    Parses the strategy string and returns a dictionary of state to action.
    """
    # Remove everything before and including "-- Strategy Template (for System) --"
    strat_marker = "-- Strategy Template (for System) --"
    idx = strategy_string.find(strat_marker)
    if idx != -1:
        strategy_string = strategy_string[idx + len(strat_marker):]
    
    live_marker = 'Conditional live groups: '
    live_idx = strategy_string.find(live_marker)

    unsafe_marker = 'Unsafe edges:'
    unsafe_idx = strategy_string.find(unsafe_marker)
    pair_re=re.compile(r'(\d+)\s*->\s*(\d+)')

    unsafe_strategy=defaultdict(list)

    if unsafe_idx != -1:
        unsafe_str=strategy_string[unsafe_idx + len(unsafe_marker): live_idx]
        unsafe_pairs = pair_re.findall(unsafe_str)
        unsafe_pairs = [(int(a), int(b)) for a, b in unsafe_pairs]
    
        for a, b in unsafe_pairs:
            unsafe_strategy[a].append(b)
    
    live_strategy=defaultdict(list)
    live_str = strategy_string[live_idx + len(live_marker):]
    live_pairs = pair_re.findall(live_str)
    live_pairs = [(int(a), int(b)) for a, b in live_pairs]
    for a, b in live_pairs:
        live_strategy[a].append(b)
    
    strategy={'unsafe':dict(unsafe_strategy), 'live':dict(live_strategy)}

    
    return strategy

def generate_strategy_template(edge_labeled_hoa):
    strategy_string = _get_strategy_string_from_cosmo(edge_labeled_hoa)
    strategy = _parse_strategy_string(strategy_string)
    return strategy


def convert_pddl_to_hoa(domain_path, problem_path, state_labeled=False, edge_labeled=True, strategy_template=False, verbose=False):
    # Check if problem_path is a folder or not
    if os.path.isdir(problem_path):
        problem_folder=problem_path
        problem_idx=-1
    else:
        problem_folder=os.path.dirname(problem_path)
        problem_files=sorted(list(filter(lambda x: x.endswith('.pddl'), os.listdir(problem_folder))))
        problem_idx = problem_files.index(os.path.basename(problem_path))

    game = PDDLGame(domain_path, problem_folder, problem_idx)
    ret=[]
    # INSERT_YOUR_CODE


    if not verbose:
        with open(os.devnull, 'w') as devnull, contextlib.redirect_stdout(devnull):
            state_labeled_hoa, edge_labeled_hoa = format_hoa(game)
    else:
        state_labeled_hoa, edge_labeled_hoa = format_hoa(game)
    if state_labeled:
        ret.append(state_labeled_hoa)
    if edge_labeled:
        ret.append(edge_labeled_hoa)
    if strategy_template:
        ret.append(generate_strategy_template(edge_labeled_hoa))
    return tuple(ret)



__all__ = ["convert_pddl_to_hoa"]