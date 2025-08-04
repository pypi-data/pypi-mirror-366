"""
Action node implementation.

This module provides the ActionNode class which is a leaf node representing
an executable action with argument extraction and validation.
"""

from typing import Any, Callable, Dict, Optional, Set, Type, List, Union
from ..base_node import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext
from intent_kit.context.dependencies import declare_dependencies
from .remediation import (
    get_remediation_strategy,
    RemediationStrategy,
)


class ActionNode(TreeNode):
    """Leaf node representing an executable action with argument extraction and validation."""

    def __init__(
        self,
        name: Optional[str],
        param_schema: Dict[str, Type],
        action: Callable[..., Any],
        arg_extractor: Callable[
            [str, Optional[Dict[str, Any]]], Union[Dict[str, Any], ExecutionResult]
        ],
        context_inputs: Optional[Set[str]] = None,
        context_outputs: Optional[Set[str]] = None,
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = "",
        parent: Optional["TreeNode"] = None,
        children: Optional[List["TreeNode"]] = None,
        remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
    ):
        super().__init__(
            name=name, description=description, children=children or [], parent=parent
        )
        self.param_schema = param_schema
        self.action = action
        self.arg_extractor = arg_extractor
        self.context_inputs = context_inputs or set()
        self.context_outputs = context_outputs or set()
        self.input_validator = input_validator
        self.output_validator = output_validator
        self.context_dependencies = declare_dependencies(
            inputs=self.context_inputs,
            outputs=self.context_outputs,
            description=f"Context dependencies for intent '{self.name}'",
        )

        # Store remediation strategies
        self.remediation_strategies = remediation_strategies or []

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.ACTION

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        # Track token usage across the entire execution
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        total_duration = 0.0

        try:
            context_dict: Optional[Dict[str, Any]] = None
            if context:
                context_dict = {
                    key: context.get(key)
                    for key in self.context_inputs
                    if context.has(key)
                }

            # Extract parameters - this might involve LLM calls
            extracted_params = self.arg_extractor(user_input, context_dict or {})
            self.logger.debug(f"ActionNode extracted_params: {extracted_params}")

            # If the arg_extractor returned an ExecutionResult (LLM-based), extract token info
            if isinstance(extracted_params, ExecutionResult):
                total_input_tokens += getattr(extracted_params, "input_tokens", 0) or 0
                total_output_tokens += (
                    getattr(extracted_params, "output_tokens", 0) or 0
                )
                total_cost += getattr(extracted_params, "cost", 0.0) or 0.0
                total_duration += getattr(extracted_params, "duration", 0.0) or 0.0

                # Extract the actual parameters from the result
                if extracted_params.params:
                    extracted_params = extracted_params.params
                elif extracted_params.output:
                    extracted_params = extracted_params.output
                else:
                    extracted_params = {}
            elif not isinstance(extracted_params, dict):
                # If it's not a dict or ExecutionResult, convert to dict
                extracted_params = {}

        except Exception as e:
            self.logger.error(
                f"Argument extraction failed for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
            )
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path(),
                ),
                params=None,
                children_results=[],
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                cost=total_cost,
                duration=total_duration,
            )
        if self.input_validator:
            try:
                if not self.input_validator(extracted_params):
                    self.logger.error(
                        f"Input validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})"
                    )
                    return ExecutionResult(
                        success=False,
                        node_name=self.name,
                        node_path=self.get_path(),
                        node_type=NodeType.ACTION,
                        input=user_input,
                        output=None,
                        error=ExecutionError(
                            error_type="InputValidationError",
                            message="Input validation failed",
                            node_name=self.name,
                            node_path=self.get_path(),
                        ),
                        params=extracted_params,
                        children_results=[],
                        input_tokens=total_input_tokens,
                        output_tokens=total_output_tokens,
                        cost=total_cost,
                        duration=total_duration,
                    )
            except Exception as e:
                self.logger.error(
                    f"Input validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
                )
                return ExecutionResult(
                    success=False,
                    node_name=self.name,
                    node_path=self.get_path(),
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=None,
                    error=ExecutionError(
                        error_type=type(e).__name__,
                        message=str(e),
                        node_name=self.name,
                        node_path=self.get_path(),
                    ),
                    params=extracted_params,
                    children_results=[],
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                    cost=total_cost,
                    duration=total_duration,
                )
        try:
            self.logger.debug(
                f"Validating types for intent '{self.name}' (Path: {'.'.join(self.get_path())})"
            )
            validated_params = self._validate_types(extracted_params)
        except Exception as e:
            self.logger.error(
                f"Type validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
            )
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path(),
                ),
                params=extracted_params,
                children_results=[],
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                cost=total_cost,
                duration=total_duration,
            )
        self.logger.debug(f"ActionNode validated_params: {validated_params}")
        try:
            if context is not None:
                output = self.action(**validated_params, context=context)
            else:
                output = self.action(**validated_params)
        except Exception as e:
            self.logger.error(
                f"Action execution error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
            )

            # Try remediation strategies
            error = ExecutionError(
                error_type=type(e).__name__,
                message=str(e),
                node_name=self.name,
                node_path=self.get_path(),
            )

            remediation_result = self._execute_remediation_strategies(
                user_input=user_input,
                context=context,
                original_error=error,
                validated_params=validated_params,
            )

            if remediation_result:
                # Aggregate tokens from remediation if it succeeded
                if isinstance(remediation_result, ExecutionResult):
                    total_input_tokens += (
                        getattr(remediation_result, "input_tokens", 0) or 0
                    )
                    total_output_tokens += (
                        getattr(remediation_result, "output_tokens", 0) or 0
                    )
                    total_cost += getattr(remediation_result, "cost", 0.0) or 0.0
                    total_duration += (
                        getattr(remediation_result, "duration", 0.0) or 0.0
                    )

                    # Update the remediation result with aggregated tokens
                    remediation_result.input_tokens = total_input_tokens
                    remediation_result.output_tokens = total_output_tokens
                    remediation_result.cost = total_cost
                    remediation_result.duration = total_duration

                    return remediation_result

            self.logger.debug(f"ActionNode remediation_result: {remediation_result}")
            # If no remediation succeeded, return the original error
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=error,
                params=validated_params,
                children_results=[],
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                cost=total_cost,
                duration=total_duration,
            )
        self.logger.debug(f"ActionNode output: {output}")
        if self.output_validator:
            try:
                if not self.output_validator(output):
                    self.logger.error(
                        f"Output validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})"
                    )
                    return ExecutionResult(
                        success=False,
                        node_name=self.name,
                        node_path=self.get_path(),
                        node_type=NodeType.ACTION,
                        input=user_input,
                        output=None,
                        error=ExecutionError(
                            error_type="OutputValidationError",
                            message="Output validation failed",
                            node_name=self.name,
                            node_path=self.get_path(),
                        ),
                        params=validated_params,
                        children_results=[],
                        input_tokens=total_input_tokens,
                        output_tokens=total_output_tokens,
                        cost=total_cost,
                        duration=total_duration,
                    )
            except Exception as e:
                self.logger.error(
                    f"Output validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
                )
                return ExecutionResult(
                    success=False,
                    node_name=self.name,
                    node_path=self.get_path(),
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=None,
                    error=ExecutionError(
                        error_type=type(e).__name__,
                        message=str(e),
                        node_name=self.name,
                        node_path=self.get_path(),
                    ),
                    params=validated_params,
                    children_results=[],
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                    cost=total_cost,
                    duration=total_duration,
                )

        # Update context with outputs
        if context is not None:
            for key in self.context_outputs:
                if hasattr(output, key):
                    context.set(key, getattr(output, key), self.name)
                elif isinstance(output, dict) and key in output:
                    context.set(key, output[key], self.name)

        self.logger.debug(f"Final ActionNode returning ExecutionResult: {output}")
        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=NodeType.ACTION,
            input=user_input,
            output=output,
            error=None,
            params=validated_params,
            children_results=[],
            # NOTE: Setting the sum total for now for this execution call, but should delineate the cost of any LLM calls associated with this node
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            cost=total_cost,
            duration=total_duration,
        )

    def _execute_remediation_strategies(
        self,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        validated_params: Optional[Dict[str, Any]] = None,
    ) -> Optional[ExecutionResult]:
        """Execute remediation strategies in order until one succeeds."""
        for strategy in self.remediation_strategies:
            try:
                if isinstance(strategy, str):
                    strategy_instance = get_remediation_strategy(strategy)
                else:
                    strategy_instance = strategy

                if strategy_instance:
                    remediation_result = strategy_instance.execute(
                        node_name=self.name or "unknown",
                        user_input=user_input,
                        context=context,
                        original_error=original_error,
                        handler_func=self.action,
                        validated_params=validated_params,
                    )
                    if remediation_result and remediation_result.success:
                        self.logger.info(
                            f"Remediation strategy '{strategy_instance.__class__.__name__}' succeeded for intent '{self.name}'"
                        )
                        return remediation_result
            except Exception as e:
                self.logger.error(
                    f"Remediation strategy execution failed for intent '{self.name}': {type(e).__name__}: {str(e)}"
                )

        return None

    def _validate_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert parameter types according to the schema."""
        validated_params: Dict[str, Any] = {}
        for param_name, param_type in self.param_schema.items():
            if param_name not in params:
                raise ValueError(f"Missing required parameter: {param_name}")

            param_value = params[param_name]
            try:
                if param_type is str:
                    validated_params[param_name] = str(param_value)
                elif param_type is int:
                    validated_params[param_name] = int(param_value)
                elif param_type is float:
                    validated_params[param_name] = float(param_value)
                elif param_type is bool:
                    if isinstance(param_value, str):
                        validated_params[param_name] = param_value.lower() in (
                            "true",
                            "1",
                            "yes",
                            "on",
                        )
                    else:
                        validated_params[param_name] = bool(param_value)
                else:
                    validated_params[param_name] = param_value
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid type for parameter '{param_name}': expected {param_type.__name__}, got {type(param_value).__name__}"
                ) from e

        return validated_params
