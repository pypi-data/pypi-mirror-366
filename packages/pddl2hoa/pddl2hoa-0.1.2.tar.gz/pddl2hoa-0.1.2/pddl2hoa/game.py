from abc import ABC, abstractmethod
from copy import copy
import os
from pddlgym.core import PDDLEnv


current_dir = os.path.dirname(os.path.abspath(__file__))
pddl_dir = os.path.join(current_dir, "../pddl/")

class TurnBasedGame(ABC):
    
    def get_player(self):
        if not hasattr(self, 'player'):
            self.player = 0
        return self.player

    def make_move(self, *args, **kwargs):
        self._make_move_impl(*args, **kwargs)
        if not hasattr(self, 'player'):
            self.player = 0
        self.player = 1-self.player

        
    
    @abstractmethod
    def _make_move_impl(self, *args, **kwargs):
        pass
    
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def is_valid_state(self):
        pass
    
    @property
    @abstractmethod
    def is_winning_state(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return self.name + ' ' + self.physical_state + f"; player: {self.get_player()}"
    
    @property
    @abstractmethod
    def physical_state(self):
        pass

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()
    
    def __hash__(self):
        return hash(self.__repr__())
    
    def get_successors(self):
        successors = []
        for action in self.get_valid_actions():
            successor = copy(self)
            successor.make_move(action)
            successors.append(successor)
        return successors

    @abstractmethod
    def get_propositions(self):
        pass

    @abstractmethod
    def get_valid_actions(self):
        pass


class PDDLGame(TurnBasedGame):
    env=None
    domain_file=None
    problem_folder=None
    all_propositions=None
    
    def __init__(self, domain_path, problem_path, problem_idx=-1, reset_env=False, state=None):
        if self.__class__.env is None or reset_env:
            self.__class__.env = PDDLEnv(domain_path, problem_path, operators_as_actions=True, dynamic_action_space=True)
            if problem_idx >=0:
                self.__class__.env.fix_problem_index(problem_idx)
            self.__class__.domain_file = domain_path
            self.__class__.problem_folder = problem_path
            self.__class__.env.reset()
            self.__class__.all_propositions = self.__class__.env.observation_space.all_ground_literals(self.__class__.env.get_state())
            
        if state is None:
            state, _ = self.__class__.env.reset()
        self.state = state
        
    def _make_move_impl(self, *args, **kwargs):
        self.__class__.env._state = self.state
        self.state, _, _, _, _ = self.__class__.env.step(*args, **kwargs)

    @property
    def name(self):
        return self.domain_file.split('/')[-1].split('.')[0]
    
    @property
    def is_valid_state(self):
        return True
    
    @property
    def is_winning_state(self):
        return self.__class__.env._is_goal_reached(self.state)
    
    @property
    def physical_state(self):
        state_obj = self.state
        literals = [str(lit) for lit in state_obj.literals]
        literals.sort()

        objects = [str(obj) for obj in state_obj.objects]
        objects.sort()

        return 'objects: ' + ' '.join(objects) + '; literals: ' + ' '.join(literals)
    
    def __str__(self):
        return self.physical_state
    
    
    def get_valid_actions(self):
        return self.__class__.env.action_space.all_ground_literals(self.state)
    
    def get_propositions(self):
        propositions = {str(prop):prop in self.state.literals for prop in self.__class__.all_propositions}
        return propositions