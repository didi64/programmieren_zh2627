import math
import random
from observable import Observable


def make_stream(f):
    next_symb = f if callable(f) else lambda xs=iter(f): next(xs, None)
    return next_symb


class DEA(Observable):
    def __init__(self, delta, state=0, accepting_states=()):
        '''delta: dict of the form
           {(state, symbol): new_state, ...} or
           {(state, symbol): (new_state, outupt_symbol), ...}
        '''
        self.initial_state = state
        self.state = self.initial_state
        self.delta = {k: (v, None) if type(v) is int else v for k, v in delta.items()}
        self.accepting_states = set(accepting_states)

    def process_symb(self, s_read):
        if s_read is None:
            return False
        xstate_in = (self.state, s_read)
        if not (xstate_out := self.delta.get(xstate_in)):
            msg = 'No transition for ({}, {}) in automatons transition table!'
            raise ValueError(msg.format(*xstate_in))
        self.state, symb = xstate_out
        data = (xstate_in,  (self.state, symb, self.is_accepting()))
        self._notify('state_change', data)
        return True

    def read(self, word):
        for c in word:
            self.process_symb(c)

    def reset(self):
        old_state = self.state
        self.state = self.initial_state
        self._notify('reset', (old_state, self.state))

    def is_accepting(self):
        return self.state in self.accepting_states

    def _step(self, next_symb):
        return self.process_symb(next_symb())

    def _run(self, word, max_steps=math.inf):
        next_symb = make_stream(word)
        steps = 0
        success = True
        while success and steps < max_steps:
            success = self._step(next_symb)
            steps += success

    def __call__(self, word):
        self.reset()
        self._run(word)
        return self.is_accepting()


class NEA(Observable):
    '''None is the Error state'''
    EPSILON = ()  # empyt word
    policies = {'first': lambda states: next(iter(states)),
                'random': lambda states: random.choice(tuple(states)),
                }

    def __init__(self, delta, state=0, accepting_states=(), policy='random'):
        assert policy is None or policy in self.policies or callable(policy), \
               'policy must be "first" or "random" or callable'
        self.initial_state = state
        self.state = self.initial_state
        self.delta = {k: {(s, None) if type(s) is int else s for s in v} for k, v in delta.items()}
        self.accepting_states = set(accepting_states)
        self.policy = policy
        self.state_selector = self.policies.get(policy, policy)

    def select(self, xstates):
        if not xstates:
            return None
        return self.state_selector(xstates)

    def process_symb(self, s_read):
        if s_read is None:
            return False
        xstate_in = (self.state, s_read)
        if xstate_in not in self.delta:
            self._notify('KeyError', xstate_in)
            return False
        self.state, s_out = self.select(self.delta[xstate_in])
        xstate_out = (self.state, s_out, self.is_accepting())
        self._notify('state_change', (xstate_in, xstate_out))
        return True

    def _step(self, get_symb):
        return self.process_symb(get_symb())

    def _run(self, word, max_steps=math.inf):
        get_symb = make_stream(word)
        steps = 0
        success = True
        while success and steps < max_steps:
            success = self._step(get_symb)
            steps += success

    def is_accepting(self):
        return self.state in self.accepting_states

    def reset(self):
        s = self.state
        self.state = self.initial_state
        self._notify('reset', (s, self.state))

    def _eclosure(self, state):
        '''returns the epsilon closure of a state'''
        states = {state}
        count = 0
        while count < (c := len(states)):
            count = c
            new_states = set()
            for state in states:
                xstates = self.delta.get((state, self.EPSILON), set())
                new_states |= {s for s, _ in xstates}
            states |= new_states
        return states

    def eclosure(self, states):
        '''returns the epsilon closure of the set states'''
        closure = set()
        for state in states:
            closure |= self._eclosure(state)
        return closure

    def ra_states(self, word, with_path=False):
        if with_path:
            state_path = self._reachable_states_with_path(word)
            return {k: v for k, v in state_path.items() if k in self.accepting_states}
        else:
            states = self._reachable_states(word)
            return states & self.accepting_states

    def _reachable_states(self, word):
        states = self.eclosure({self.initial_state})
        for s in word:
            new_states = set()
            for state in states:
                xstates = self.delta.get((state, s), set())
                states = {s for s, _ in xstates}
                new_states |= self.eclosure(states)
            states = new_states
        return states

    def _extend_statepath(self, state_path, symb):
        new_state_path = {}
        for state in state_path:
            xstates = self.delta.get((state, symb), set())
            states = {s for s, _ in xstates}
            new_states = states - set(new_state_path)
            new_states = self.eclosure(new_states)
            for s in new_states:
                new_state_path[s] = state_path[state] + ((state, symb, s),)
        return new_state_path

    def _reachable_states_with_path(self, word):
        initials = self.eclosure({self.initial_state})
        state_path = {s: () for s in initials}
        for symb in word:
            state_path = self._extend_statepath(state_path, symb)
        return state_path

    def __call__(self, word, with_path=False):
        self.reset()
        return self.ra_states(word, with_path=with_path)


class Environment(Observable):
    def __init__(self, automaton):
        self.automaton = automaton
        self.automaton.register_callback(self.action_handler)

    def reset(self):
        self.automaton.reset()

    def update(self):
        raise NotImplementedError

    def get_symbol(self):
        raise NotImplementedError

    def action_handler(self, event, data=None):
        raise NotImplementedError

    def step(self, symb=None):
        symb = symb or self.get_symbol()
        if not symb:
            return
        self.automaton.process_symb(symb)
        self.update(self.automaton.state)
        return True

    def run(self, max_steps=10):
        steps = 0
        success = True
        while success and steps < max_steps:
            success = self.step()
            steps += success