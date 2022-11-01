"""
Drew's super amazing top tier FSM systems!!!!!!!!!!!!!!!!!!!!!!!!

This module contains the State class, the FSM class, and the Dynamic FSM Class
"""
import logging
from typing import Callable, Dict, Optional, Tuple


class TransitionException(Exception):
    pass


class DynamicFSM:
    """
    A Dynamic FSM, instead of manually defining states, they are automatically
    assigned by naming their enter and (optionally) exit functions
    enterStateName and exitStateName.

    The main con of this system compared to the StaticFSM is we cannot explicitly specify what states a state is allowed
    to transition to - they will all always be able to transition to any state
    """

    def __init__(self):
        self.activeState: Optional[str] = None

        # Don't allow a state change to be called if we're currently transitioning
        self.transitioning: bool = False

    def setState(self, toState: str):
        if self.transitioning:
            raise TransitionException("Cannot transition while already transitioning!")
        if self.activeState == toState:
            return

        # Lock the FSM to prevent transitioning until this transition is finished
        self.transitioning = True
        if self.activeState:
            exitFunc: Optional[Callable] = self.getStateExit(self.activeState)
            if exitFunc:
                exitFunc()

        logging.info(f"SETTING STATE: {toState}")
        self.getStateEntry(toState)()
        self.activeState = toState

        # Unlock the transition
        self.transitioning = False

    def getStateEntry(self, stateName: str) -> Callable:
        enterFunc: Optional[Callable] = getattr(self, f'enter{stateName}', None)
        if not enterFunc:
            raise TransitionException(f'State "{stateName}" does not have an entry function ("enter{stateName}")')
        return enterFunc

    def getStateExit(self, stateName: str) -> Optional[Callable]:
        exitFunc: Optional[Callable] = getattr(self, f'exit{stateName}', None)
        return exitFunc


class State:
    """
    The individual states for the FSM. This is what we use to manually define each state.
    """

    def __init__(self, name: str, enterFunc: Callable, exitFunc: Optional[Callable] = None,
                 transitions: Optional[Tuple[str, ...]] = None):
        self.name: str = name
        self.enterFunc: Callable = enterFunc
        self.exitFunc: Optional[Callable] = exitFunc
        self.transitions: Optional[Tuple[str, ...]] = transitions


class FSM:
    """
    A Simple Finite State Machine. We manually define states in the constructor
    """

    def __init__(self, *states: State):
        self.activeState: Optional[State] = None

        # Don't allow a state change to be called if we're currently transitioning
        self.transitioning: bool = False
        self.states: Dict[str, State] = {}
        for state in states:
            self.states[state.name] = state

    def setState(self, state: str):
        if self.transitioning:
            raise TransitionException("Cannot transition while already transitioning!")

        toState = self.getState(state)

        if self.activeState == toState:
            return
        if not self.isValidTransition(self.activeState, toState):
            raise TransitionException(f"{self.activeState} cannot transition to {toState.name}")

        # Lock the FSM to prevent transitioning until this transition is finished
        self.transitioning = True
        logging.info(f"SETTING STATE: {state}")
        if self.activeState and self.activeState.exitFunc:
            self.activeState.exitFunc()
        self.activeState = toState
        self.activeState.enterFunc()

        # Unlock the transition
        self.transitioning = False

    def getState(self, state: str) -> State:
        return self.states.get(state, None)

    def isValidTransition(self, fromState: Optional[State], toState: State) -> bool:
        if self.activeState is None or fromState.transitions is None:
            return True
        return toState.name in fromState.transitions
