"""
Molecular Dynamics Module

This module provides quantum-inspired molecular dynamics simulations,
including classical MD, quantum dynamics, and enhanced sampling methods.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.integrate import odeint
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


class IntegrationMethod(Enum):
    """Molecular dynamics integration methods."""
    VERLET = "verlet"
    RUNGE_KUTTA = "runge_kutta"
    QUANTUM_INSPIRED = "quantum_inspired"
    LEAPFROG = "leapfrog"


@dataclass
class MDTrajectory:
    """Molecular dynamics trajectory data."""
    
    positions: np.ndarray  # (n_steps, n_atoms, 3)
    velocities: np.ndarray  # (n_steps, n_atoms, 3)
    forces: np.ndarray  # (n_steps, n_atoms, 3)
    energies: np.ndarray  # (n_steps,)
    temperatures: np.ndarray  # (n_steps,)
    time_steps: np.ndarray  # (n_steps,)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "positions": self.positions.tolist(),
            "velocities": self.velocities.tolist(),
            "forces": self.forces.tolist(),
            "energies": self.energies.tolist(),
            "temperatures": self.temperatures.tolist(),
            "time_steps": self.time_steps.tolist()
        }


@dataclass
class MDResult:
    """Molecular dynamics simulation result."""
    
    trajectory: MDTrajectory
    final_energy: float
    final_temperature: float
    average_energy: float
    average_temperature: float
    energy_conservation: float
    integration_method: IntegrationMethod
    simulation_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trajectory": self.trajectory.to_dict(),
            "final_energy": self.final_energy,
            "final_temperature": self.final_temperature,
            "average_energy": self.average_energy,
            "average_temperature": self.average_temperature,
            "energy_conservation": self.energy_conservation,
            "integration_method": self.integration_method.value,
            "simulation_time": self.simulation_time
        }


class MolecularDynamics:
    """Quantum-inspired molecular dynamics simulator."""
    
    def __init__(self, 
                 integration_method: IntegrationMethod = IntegrationMethod.QUANTUM_INSPIRED,
                 time_step: float = 0.001,
                 temperature: float = 300.0,
                 friction: float = 0.1):
        """
        Initialize molecular dynamics simulator.
        
        Args:
            integration_method: Integration method
            time_step: Time step in ps
            temperature: Temperature in K
            friction: Friction coefficient for Langevin dynamics
        """
        self.integration_method = integration_method
        self.time_step = time_step
        self.temperature = temperature
        self.friction = friction
        self.nuclei = None
        self.masses = None
        self.quantum_parameters = None
        
    def set_system(self, nuclei: List[Tuple[str, np.ndarray]], masses: Optional[List[float]] = None):
        """
        Set molecular system for simulation.
        
        Args:
            nuclei: List of (element, position) tuples
            masses: List of atomic masses (amu)
        """
        self.nuclei = nuclei
        self.masses = masses or self._get_default_masses(nuclei)
        
        # Initialize quantum parameters
        n_atoms = len(nuclei)
        self.quantum_parameters = np.random.uniform(0, 2*np.pi, n_atoms * 6)
        
    def run_simulation(self, n_steps: int, potential_function: Optional[Callable] = None) -> MDResult:
        """
        Run molecular dynamics simulation.
        
        Args:
            n_steps: Number of simulation steps
            potential_function: Custom potential function
            
        Returns:
            MD simulation result
        """
        if self.nuclei is None:
            raise ValueError("Must call set_system() before run_simulation()")
        
        # Initialize trajectory arrays
        n_atoms = len(self.nuclei)
        positions = np.zeros((n_steps, n_atoms, 3))
        velocities = np.zeros((n_steps, n_atoms, 3))
        forces = np.zeros((n_steps, n_atoms, 3))
        energies = np.zeros(n_steps)
        temperatures = np.zeros(n_steps)
        time_steps = np.zeros(n_steps)
        
        # Initial conditions
        positions[0] = np.array([pos for _, pos in self.nuclei])
        velocities[0] = self._initialize_velocities()
        
        # Use default potential if none provided
        if potential_function is None:
            potential_function = self._lennard_jones_potential
        
        import time
        start_time = time.time()
        
        # Run simulation
        for step in range(1, n_steps):
            if self.integration_method == IntegrationMethod.QUANTUM_INSPIRED:
                positions[step], velocities[step] = self._quantum_integration_step(
                    positions[step-1], velocities[step-1], potential_function
                )
            elif self.integration_method == IntegrationMethod.VERLET:
                positions[step], velocities[step] = self._verlet_integration_step(
                    positions[step-1], velocities[step-1], potential_function
                )
            else:
                positions[step], velocities[step] = self._runge_kutta_integration_step(
                    positions[step-1], velocities[step-1], potential_function
                )
            
            # Calculate forces and energy
            forces[step] = self._calculate_forces(positions[step], potential_function)
            energies[step] = self._calculate_energy(positions[step], velocities[step], potential_function)
            temperatures[step] = self._calculate_temperature(velocities[step])
            time_steps[step] = step * self.time_step
        
        simulation_time = time.time() - start_time
        
        # Create trajectory
        trajectory = MDTrajectory(
            positions=positions,
            velocities=velocities,
            forces=forces,
            energies=energies,
            temperatures=temperatures,
            time_steps=time_steps
        )
        
        # Calculate final results
        final_energy = energies[-1]
        final_temperature = temperatures[-1]
        average_energy = np.mean(energies)
        average_temperature = np.mean(temperatures)
        energy_conservation = np.std(energies) / np.mean(energies)
        
        return MDResult(
            trajectory=trajectory,
            final_energy=final_energy,
            final_temperature=final_temperature,
            average_energy=average_energy,
            average_temperature=average_temperature,
            energy_conservation=energy_conservation,
            integration_method=self.integration_method,
            simulation_time=simulation_time
        )
    
    def _quantum_integration_step(self, positions: np.ndarray, velocities: np.ndarray, 
                                 potential_function: Callable) -> Tuple[np.ndarray, np.ndarray]:
        """Quantum-inspired integration step."""
        n_atoms = len(positions)
        
        # Apply quantum transformation to positions and velocities
        quantum_positions = self._apply_quantum_transformation(positions)
        quantum_velocities = self._apply_quantum_transformation(velocities)
        
        # Calculate forces
        forces = self._calculate_forces(quantum_positions, potential_function)
        
        # Quantum-inspired velocity update
        for i in range(n_atoms):
            # Apply quantum rotation to forces
            if i < len(self.quantum_parameters) // 6:
                rotation = self.quantum_parameters[i * 6:(i + 1) * 6]
                forces[i] = forces[i] * np.cos(rotation[:3]) + np.sin(rotation[3:])
        
        # Update positions and velocities
        new_positions = quantum_positions + quantum_velocities * self.time_step + 0.5 * forces * self.time_step**2
        new_velocities = quantum_velocities + forces * self.time_step
        
        # Apply quantum measurement (collapse to classical state)
        new_positions = np.real(new_positions)
        new_velocities = np.real(new_velocities)
        
        return new_positions, new_velocities
    
    def _verlet_integration_step(self, positions: np.ndarray, velocities: np.ndarray,
                                potential_function: Callable) -> Tuple[np.ndarray, np.ndarray]:
        """Verlet integration step."""
        n_atoms = len(positions)
        
        # Calculate forces
        forces = self._calculate_forces(positions, potential_function)
        
        # Update positions
        new_positions = positions + velocities * self.time_step + 0.5 * forces * self.time_step**2
        
        # Calculate new forces
        new_forces = self._calculate_forces(new_positions, potential_function)
        
        # Update velocities
        new_velocities = velocities + 0.5 * (forces + new_forces) * self.time_step
        
        return new_positions, new_velocities
    
    def _runge_kutta_integration_step(self, positions: np.ndarray, velocities: np.ndarray,
                                     potential_function: Callable) -> Tuple[np.ndarray, np.ndarray]:
        """Runge-Kutta integration step."""
        # Define state vector
        state = np.concatenate([positions.flatten(), velocities.flatten()])
        
        # Define derivative function
        def derivative(state, t):
            n_atoms = len(positions)
            pos = state[:3*n_atoms].reshape(n_atoms, 3)
            vel = state[3*n_atoms:].reshape(n_atoms, 3)
            
            forces = self._calculate_forces(pos, potential_function)
            
            dpos = vel
            dvel = forces
            
            return np.concatenate([dpos.flatten(), dvel.flatten()])
        
        # Integrate one step
        new_state = odeint(derivative, state, [0, self.time_step])[1]
        
        # Extract positions and velocities
        n_atoms = len(positions)
        new_positions = new_state[:3*n_atoms].reshape(n_atoms, 3)
        new_velocities = new_state[3*n_atoms:].reshape(n_atoms, 3)
        
        return new_positions, new_velocities
    
    def _calculate_forces(self, positions: np.ndarray, potential_function: Callable) -> np.ndarray:
        """Calculate forces using finite difference."""
        n_atoms = len(positions)
        forces = np.zeros((n_atoms, 3))
        
        # Finite difference for force calculation
        delta = 1e-6
        for i in range(n_atoms):
            for j in range(3):
                # Forward step
                pos_forward = positions.copy()
                pos_forward[i, j] += delta
                energy_forward = potential_function(pos_forward)
                
                # Backward step
                pos_backward = positions.copy()
                pos_backward[i, j] -= delta
                energy_backward = potential_function(pos_backward)
                
                # Force is negative gradient
                forces[i, j] = -(energy_forward - energy_backward) / (2 * delta)
        
        return forces
    
    def _calculate_energy(self, positions: np.ndarray, velocities: np.ndarray, 
                         potential_function: Callable) -> float:
        """Calculate total energy."""
        # Kinetic energy
        kinetic_energy = 0.5 * np.sum(self.masses[:, np.newaxis] * velocities**2)
        
        # Potential energy
        potential_energy = potential_function(positions)
        
        return kinetic_energy + potential_energy
    
    def _calculate_temperature(self, velocities: np.ndarray) -> float:
        """Calculate instantaneous temperature."""
        # T = (2/3) * KE / (N * kB)
        kinetic_energy = 0.5 * np.sum(self.masses[:, np.newaxis] * velocities**2)
        n_atoms = len(velocities)
        temperature = (2/3) * kinetic_energy / (n_atoms * 8.314e-3)  # Convert to K
        return temperature
    
    def _initialize_velocities(self) -> np.ndarray:
        """Initialize velocities with Maxwell-Boltzmann distribution."""
        n_atoms = len(self.nuclei)
        velocities = np.random.normal(0, 1, (n_atoms, 3))
        
        # Scale to target temperature
        target_ke = 1.5 * n_atoms * 8.314e-3 * self.temperature  # J/mol
        current_ke = 0.5 * np.sum(self.masses[:, np.newaxis] * velocities**2)
        scale_factor = np.sqrt(target_ke / current_ke)
        velocities *= scale_factor
        
        # Remove center-of-mass motion
        total_momentum = np.sum(self.masses[:, np.newaxis] * velocities, axis=0)
        total_mass = np.sum(self.masses)
        velocities -= total_momentum / total_mass
        
        return velocities
    
    def _get_default_masses(self, nuclei: List[Tuple[str, np.ndarray]]) -> np.ndarray:
        """Get default atomic masses."""
        # Simplified mass table (amu)
        mass_table = {
            'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
            'B': 10.811, 'C': 12.011, 'N': 14.007, 'O': 15.999,
            'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
            'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.065,
            'Cl': 35.453, 'Ar': 39.948, 'K': 39.098, 'Ca': 40.078
        }
        
        masses = []
        for element, _ in nuclei:
            masses.append(mass_table.get(element, 12.0))  # Default to C mass
        
        return np.array(masses)
    
    def _lennard_jones_potential(self, positions: np.ndarray) -> float:
        """Lennard-Jones potential energy."""
        n_atoms = len(positions)
        energy = 0.0
        
        # LJ parameters (simplified)
        epsilon = 0.1  # kJ/mol
        sigma = 3.0    # Angstrom
        
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                distance = np.linalg.norm(positions[i] - positions[j])
                if distance > 0:
                    r6 = (sigma / distance) ** 6
                    r12 = r6 ** 2
                    energy += 4 * epsilon * (r12 - r6)
        
        return energy
    
    def _apply_quantum_transformation(self, array: np.ndarray) -> np.ndarray:
        """Apply quantum-inspired transformation to array."""
        n_atoms = len(array)
        transformed_array = array.copy()
        
        # Apply quantum rotation
        for i in range(n_atoms):
            if i < len(self.quantum_parameters) // 6:
                rotation = self.quantum_parameters[i * 6:(i + 1) * 6]
                for j in range(3):
                    if j < len(rotation):
                        transformed_array[i, j] *= np.cos(rotation[j])
        
        return transformed_array


class QuantumDynamics:
    """Quantum dynamics simulator."""
    
    def __init__(self, n_states: int = 2, time_step: float = 0.001):
        """
        Initialize quantum dynamics simulator.
        
        Args:
            n_states: Number of quantum states
            time_step: Time step
        """
        self.n_states = n_states
        self.time_step = time_step
        self.hamiltonian = None
        self.quantum_state = None
        
    def set_hamiltonian(self, hamiltonian: np.ndarray):
        """Set system Hamiltonian."""
        self.hamiltonian = hamiltonian
        
    def set_initial_state(self, initial_state: np.ndarray):
        """Set initial quantum state."""
        self.quantum_state = initial_state / np.linalg.norm(initial_state)
        
    def evolve(self, n_steps: int) -> np.ndarray:
        """Evolve quantum state."""
        if self.hamiltonian is None or self.quantum_state is None:
            raise ValueError("Must set Hamiltonian and initial state")
        
        # Time evolution operator
        evolution_operator = np.exp(-1j * self.hamiltonian * self.time_step)
        
        # Evolve state
        trajectory = np.zeros((n_steps, self.n_states), dtype=complex)
        current_state = self.quantum_state.copy()
        
        for step in range(n_steps):
            trajectory[step] = current_state
            current_state = evolution_operator @ current_state
            current_state = current_state / np.linalg.norm(current_state)
        
        return trajectory


def create_molecular_dynamics(method: IntegrationMethod = IntegrationMethod.QUANTUM_INSPIRED) -> MolecularDynamics:
    """Factory function to create molecular dynamics simulator."""
    return MolecularDynamics(integration_method=method)


def create_quantum_dynamics(n_states: int = 2) -> QuantumDynamics:
    """Factory function to create quantum dynamics simulator."""
    return QuantumDynamics(n_states=n_states) 