from pddl2hoa import convert_pddl_to_hoa

# state_labeled, edge_labeled, strategy = convert_pddl_to_hoa('pddl/hanoi.pddl', 'pddl/hanoi/problem4.pddl')
state_labeled, edge_labeled = convert_pddl_to_hoa('pddl/hanoi.pddl', 'pddl/hanoi/problem4.pddl', strategy_template=False, verbose=True)

# print(state_labeled)
# print(edge_labeled)
# print(strategy)
with open('hanoi_hoa.hoa', 'w') as f:
    f.write(edge_labeled)
