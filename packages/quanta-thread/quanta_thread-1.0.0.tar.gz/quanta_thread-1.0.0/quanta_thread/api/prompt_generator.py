"""
Prompt Generator: Specialized prompt generation for quantum and ML tasks.

This module provides intelligent prompt generation for various quantum computing
and machine learning tasks, optimizing for different AI backends.
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging


class PromptType(Enum):
    """Types of prompts that can be generated."""
    QUANTUM_ALGORITHM = "quantum_algorithm"
    ML_OPTIMIZATION = "ml_optimization"
    PARALLEL_IMPLEMENTATION = "parallel_implementation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    QUANTUM_INSPIRED = "quantum_inspired"
    CODE_REVIEW = "code_review"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    ARCHITECTURE_SEARCH = "architecture_search"


class AIBackend(Enum):
    """Supported AI backends."""
    GROK = "grok"
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"


@dataclass
class PromptTemplate:
    """Template for generating prompts."""
    prompt_type: PromptType
    backend: AIBackend
    template: str
    variables: List[str]
    description: str


class PromptGenerator:
    """
    Intelligent prompt generator for quantum and ML tasks.
    
    This class provides:
    - Specialized prompts for different AI backends
    - Context-aware prompt generation
    - Performance optimization through prompt engineering
    - Multi-step prompt generation for complex tasks
    """
    
    def __init__(self):
        """Initialize the prompt generator."""
        self.templates: Dict[str, PromptTemplate] = {}
        self.prompt_history: List[Dict[str, Any]] = []
        
        # Initialize templates
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize prompt templates for different tasks and backends."""
        templates = [
            # Quantum Algorithm Templates
            PromptTemplate(
                prompt_type=PromptType.QUANTUM_ALGORITHM,
                backend=AIBackend.GROK,
                template="""
You are an expert quantum computing researcher and software engineer. Generate a Python implementation of the {algorithm_name} quantum algorithm.

Problem: {problem_description}

{f"Target Complexity: {target_complexity}" if target_complexity else ""}

Requirements:
1. Implement the algorithm using classical bit-pair qubit emulation
2. Include proper superposition and entanglement simulation
3. Add measurement and state collapse functionality
4. Include performance optimizations and threading support
5. Add comprehensive documentation and comments
6. Include error handling and validation

Please provide:
1. Complete Python implementation
2. Usage examples
3. Performance analysis
4. Optimization suggestions

Focus on creating a practical, efficient implementation that can run on classical hardware while emulating quantum behavior.
""",
                variables=["algorithm_name", "problem_description", "target_complexity"],
                description="Generate quantum algorithm implementations"
            ),
            
            PromptTemplate(
                prompt_type=PromptType.QUANTUM_ALGORITHM,
                backend=AIBackend.GEMINI,
                template="""
As a quantum computing expert, create a Python implementation of {algorithm_name} using classical emulation techniques.

Problem: {problem_description}

{f"Target Complexity: {target_complexity}" if target_complexity else ""}

Key Requirements:
- Use bit-pair qubit simulation
- Implement superposition and entanglement
- Add threading for parallel execution
- Include comprehensive error handling
- Provide detailed documentation

Deliverables:
1. Complete implementation with comments
2. Usage examples and benchmarks
3. Performance analysis
4. Optimization recommendations

Ensure the implementation is practical and efficient for classical hardware.
""",
                variables=["algorithm_name", "problem_description", "target_complexity"],
                description="Generate quantum algorithm implementations (Gemini optimized)"
            ),
            
            # ML Optimization Templates
            PromptTemplate(
                prompt_type=PromptType.ML_OPTIMIZATION,
                backend=AIBackend.GROK,
                template="""
You are an expert machine learning engineer specializing in performance optimization. Optimize the following ML workflow for {optimization_target}.

Workflow Description:
{workflow_description}

Current Performance Metrics:
{performance_metrics}

Optimization Target: {optimization_target}

Requirements:
1. Maintain or improve accuracy while optimizing for {optimization_target}
2. Use quantum-inspired optimization techniques where applicable
3. Implement parallel processing and threading
4. Add memory optimization if targeting memory usage
5. Include performance monitoring and profiling
6. Provide before/after performance comparisons

Please provide:
1. Optimized workflow implementation
2. Performance improvement strategies
3. Code examples with threading and parallelization
4. Monitoring and profiling code
5. Expected performance gains
""",
                variables=["workflow_description", "performance_metrics", "optimization_target"],
                description="Optimize ML workflows for performance"
            ),
            
            # Parallel Implementation Templates
            PromptTemplate(
                prompt_type=PromptType.PARALLEL_IMPLEMENTATION,
                backend=AIBackend.GEMINI,
                template="""
Create a parallel implementation of the following algorithm in {target_language} using {num_threads} threads.

Algorithm Description:
{algorithm_description}

Requirements:
1. Use {num_threads} threads for parallel execution
2. Implement proper thread synchronization and data sharing
3. Handle race conditions and deadlocks
4. Include performance monitoring and load balancing
5. Add error handling for thread failures
6. Optimize for the target language's threading model

Please provide:
1. Complete parallel implementation
2. Thread management and synchronization code
3. Performance monitoring utilities
4. Usage examples and benchmarks
5. Scalability analysis
""",
                variables=["algorithm_description", "target_language", "num_threads"],
                description="Generate parallel implementations"
            ),
            
            # Performance Analysis Templates
            PromptTemplate(
                prompt_type=PromptType.PERFORMANCE_ANALYSIS,
                backend=AIBackend.GROK,
                template="""
You are a performance optimization expert. Analyze the following code and performance data to identify bottlenecks and suggest improvements.

Code:
{code_snippet}

Performance Data:
{performance_data}

Please provide:
1. Bottleneck identification and analysis
2. Specific optimization recommendations
3. Code improvements with explanations
4. Performance profiling suggestions
5. Expected performance gains
6. Alternative algorithms or approaches if applicable

Focus on practical, implementable optimizations that can provide significant performance improvements.
""",
                variables=["code_snippet", "performance_data"],
                description="Analyze performance bottlenecks"
            ),
            
            # Quantum-Inspired Templates
            PromptTemplate(
                prompt_type=PromptType.QUANTUM_INSPIRED,
                backend=AIBackend.GEMINI,
                template="""
Create a classical implementation that mimics the behavior of the following quantum algorithm, optimized for {target_platform}.

Quantum Algorithm:
{quantum_algorithm}

Requirements:
1. Emulate quantum superposition using classical techniques
2. Implement quantum-inspired parallelism and interference
3. Use bit-pair qubit simulation where applicable
4. Optimize for {target_platform} capabilities
5. Maintain quantum algorithm's theoretical advantages where possible
6. Include performance comparisons with classical alternatives

Please provide:
1. Complete classical implementation
2. Quantum-inspired optimization techniques used
3. Performance analysis and benchmarks
4. Scalability considerations
5. Usage examples and documentation
""",
                variables=["quantum_algorithm", "target_platform"],
                description="Generate quantum-inspired classical implementations"
            ),
            
            # Hyperparameter Tuning Templates
            PromptTemplate(
                prompt_type=PromptType.HYPERPARAMETER_TUNING,
                backend=AIBackend.GROK,
                template="""
Optimize hyperparameters for the following ML model using quantum-inspired techniques.

Model Description:
{model_description}

Current Hyperparameters:
{current_hyperparameters}

Performance Metrics:
{performance_metrics}

Optimization Goals:
{optimization_goals}

Requirements:
1. Use quantum-inspired optimization algorithms
2. Implement parallel hyperparameter search
3. Consider the trade-off between exploration and exploitation
4. Provide confidence intervals for recommendations
5. Include early stopping strategies
6. Suggest adaptive learning rate schedules

Please provide:
1. Optimized hyperparameter values
2. Search strategy and algorithm details
3. Expected performance improvements
4. Implementation code for the optimization
5. Validation and testing recommendations
""",
                variables=["model_description", "current_hyperparameters", "performance_metrics", "optimization_goals"],
                description="Optimize hyperparameters using quantum-inspired techniques"
            ),
            
            # Architecture Search Templates
            PromptTemplate(
                prompt_type=PromptType.ARCHITECTURE_SEARCH,
                backend=AIBackend.GEMINI,
                template="""
Design an optimal neural network architecture for the following problem using quantum-inspired search techniques.

Problem Description:
{problem_description}

Data Characteristics:
{data_characteristics}

Performance Requirements:
{performance_requirements}

Constraints:
{constraints}

Requirements:
1. Use quantum-inspired architecture search
2. Consider multiple architecture families (CNNs, RNNs, Transformers, etc.)
3. Implement efficient search strategies
4. Balance model complexity with performance
5. Include regularization and optimization techniques
6. Provide scalability considerations

Please provide:
1. Recommended architecture design
2. Search strategy and methodology
3. Expected performance characteristics
4. Implementation guidelines
5. Training and optimization recommendations
""",
                variables=["problem_description", "data_characteristics", "performance_requirements", "constraints"],
                description="Design optimal neural network architectures"
            )
        ]
        
        for template in templates:
            key = f"{template.prompt_type.value}_{template.backend.value}"
            self.templates[key] = template
    
    def generate_prompt(self,
                       prompt_type: PromptType,
                       backend: AIBackend,
                       **kwargs) -> str:
        """
        Generate a prompt for the specified type and backend.
        
        Args:
            prompt_type: Type of prompt to generate
            backend: AI backend to target
            **kwargs: Variables to substitute in the template
            
        Returns:
            Generated prompt string
        """
        template_key = f"{prompt_type.value}_{backend.value}"
        
        if template_key not in self.templates:
            raise ValueError(f"No template found for {prompt_type} and {backend}")
        
        template = self.templates[template_key]
        
        # Validate required variables
        missing_vars = [var for var in template.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        # Generate prompt
        prompt = template.template.format(**kwargs)
        
        # Record prompt generation
        self.prompt_history.append({
            'prompt_type': prompt_type.value,
            'backend': backend.value,
            'variables': kwargs,
            'prompt_length': len(prompt),
            'timestamp': self._get_timestamp()
        })
        
        return prompt
    
    def generate_multi_step_prompt(self,
                                 steps: List[Dict[str, Any]]) -> List[str]:
        """
        Generate a sequence of prompts for multi-step tasks.
        
        Args:
            steps: List of step configurations
            
        Returns:
            List of generated prompts
        """
        prompts = []
        
        for i, step in enumerate(steps):
            prompt_type = PromptType(step['prompt_type'])
            backend = AIBackend(step['backend'])
            variables = step.get('variables', {})
            
            prompt = self.generate_prompt(prompt_type, backend, **variables)
            prompts.append(prompt)
            
            # Add context from previous steps if available
            if i > 0 and step.get('include_context', False):
                context = f"\n\nContext from previous step:\n{step.get('context', '')}"
                prompts[-1] += context
        
        return prompts
    
    def generate_adaptive_prompt(self,
                               base_prompt_type: PromptType,
                               backend: AIBackend,
                               context: Dict[str, Any],
                               adaptation_rules: Dict[str, Any]) -> str:
        """
        Generate an adaptive prompt based on context and rules.
        
        Args:
            base_prompt_type: Base type of prompt
            backend: AI backend to target
            context: Context information
            adaptation_rules: Rules for adapting the prompt
            
        Returns:
            Adapted prompt string
        """
        # Generate base prompt
        base_prompt = self.generate_prompt(base_prompt_type, backend, **context)
        
        # Apply adaptation rules
        adapted_prompt = base_prompt
        
        # Add complexity based on context
        if context.get('complexity_level') == 'advanced':
            adapted_prompt += "\n\nAdditional Requirements for Advanced Implementation:"
            adapted_prompt += "\n- Include advanced optimization techniques"
            adapted_prompt += "\n- Consider edge cases and error handling"
            adapted_prompt += "\n- Provide detailed performance analysis"
        
        # Add specific backend optimizations
        if backend == AIBackend.GROK:
            adapted_prompt += "\n\nOptimize for Grok's strengths in reasoning and code generation."
        elif backend == AIBackend.GEMINI:
            adapted_prompt += "\n\nLeverage Gemini's capabilities in mathematical and scientific tasks."
        
        # Add performance requirements
        if context.get('performance_critical'):
            adapted_prompt += "\n\nPerformance is critical - prioritize optimization over readability."
        
        return adapted_prompt
    
    def generate_quantum_ml_prompt(self,
                                 task_type: str,
                                 model_type: str,
                                 data_characteristics: Dict[str, Any],
                                 optimization_target: str) -> str:
        """
        Generate a specialized prompt for quantum-inspired ML tasks.
        
        Args:
            task_type: Type of ML task
            model_type: Type of model
            data_characteristics: Characteristics of the data
            optimization_target: Target for optimization
            
        Returns:
            Generated prompt string
        """
        prompt = f"""
You are an expert in quantum-inspired machine learning. Create an optimized solution for the following task.

Task Type: {task_type}
Model Type: {model_type}
Optimization Target: {optimization_target}

Data Characteristics:
{json.dumps(data_characteristics, indent=2)}

Requirements:
1. Use quantum-inspired optimization techniques
2. Implement parallel processing where beneficial
3. Consider superposition-like data representations
4. Apply quantum-inspired search algorithms
5. Optimize for {optimization_target}
6. Include performance monitoring and analysis

Please provide:
1. Complete implementation with quantum-inspired techniques
2. Performance optimization strategies
3. Parallel processing implementation
4. Expected performance improvements
5. Usage examples and documentation
"""
        
        return prompt
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about prompt generation.
        
        Returns:
            Dictionary containing prompt statistics
        """
        if not self.prompt_history:
            return {'total_prompts': 0}
        
        stats = {
            'total_prompts': len(self.prompt_history),
            'prompt_types': {},
            'backends': {},
            'avg_prompt_length': 0,
            'total_prompt_length': 0
        }
        
        total_length = 0
        for entry in self.prompt_history:
            # Count prompt types
            prompt_type = entry['prompt_type']
            stats['prompt_types'][prompt_type] = stats['prompt_types'].get(prompt_type, 0) + 1
            
            # Count backends
            backend = entry['backend']
            stats['backends'][backend] = stats['backends'].get(backend, 0) + 1
            
            # Calculate lengths
            total_length += entry['prompt_length']
        
        stats['total_prompt_length'] = total_length
        stats['avg_prompt_length'] = total_length / len(self.prompt_history)
        
        return stats
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def clear_history(self):
        """Clear the prompt generation history."""
        self.prompt_history.clear()
    
    def export_templates(self) -> Dict[str, Any]:
        """
        Export all templates for external use.
        
        Returns:
            Dictionary containing all templates
        """
        export_data = {}
        
        for key, template in self.templates.items():
            export_data[key] = {
                'prompt_type': template.prompt_type.value,
                'backend': template.backend.value,
                'template': template.template,
                'variables': template.variables,
                'description': template.description
            }
        
        return export_data
    
    def import_templates(self, templates_data: Dict[str, Any]):
        """
        Import templates from external source.
        
        Args:
            templates_data: Dictionary containing template data
        """
        for key, data in templates_data.items():
            template = PromptTemplate(
                prompt_type=PromptType(data['prompt_type']),
                backend=AIBackend(data['backend']),
                template=data['template'],
                variables=data['variables'],
                description=data['description']
            )
            self.templates[key] = template 