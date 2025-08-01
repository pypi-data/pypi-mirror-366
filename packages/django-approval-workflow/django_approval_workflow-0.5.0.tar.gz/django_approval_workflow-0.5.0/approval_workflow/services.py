"""Approval flow orchestration services."""

import logging
from typing import Any, Dict, List, Optional, Type
from django.db.models import Q
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from .choices import ApprovalStatus, RoleSelectionStrategy
from .handlers import get_handler_for_instance
from .models import ApprovalFlow, ApprovalInstance

logger = logging.getLogger(__name__)
User = get_user_model()


def advance_flow(
    instance: ApprovalInstance,
    action: str,
    user: User,
    comment: Optional[str] = None,
    form_data: Optional[Dict[str, Any]] = None,
    resubmission_steps: Optional[List[Dict[str, Any]]] = None,
    delegate_to: Optional[User] = None,
) -> Optional[ApprovalInstance]:
    """Advance the approval flow by delegating to the appropriate handler.

    Args:
        instance: The approval instance to act upon
        action: Action to take ('approved', 'rejected', 'resubmission', 'delegated', 'escalated')
        user: User performing the action
        comment: Optional comment for the action
        form_data: Optional form data for the step
        resubmission_steps: Optional list of new steps for resubmission
        delegate_to: Optional user to delegate the step to (required for 'delegated' action)

    Returns:
        Next approval instance if workflow continues, None if complete

    Raises:
        ValueError: If action is invalid or instance status is not pending
        PermissionError: If user is not authorized to act on this step
    """
    logger.info(
        "Advancing approval flow - Flow ID: %s, Step: %s, Action: %s, User: %s",
        instance.flow.id,
        instance.step_number,
        action,
        user.username,
    )

    if instance.status not in [ApprovalStatus.PENDING, ApprovalStatus.CURRENT]:
        logger.warning(
            "Cannot advance flow - Step already processed - Flow ID: %s, Step: %s, Status: %s",
            instance.flow.id,
            instance.step_number,
            instance.status,
        )
        raise ValueError(
            f"Cannot act on step {instance.step_number} as it's already {instance.status}"
        )

    if instance.assigned_to and instance.assigned_to != user:
        logger.warning(
            "User not authorized for step - Flow ID: %s, Step: %s, User: %s, Assigned to: %s",
            instance.flow.id,
            instance.step_number,
            user.username,
            instance.assigned_to.username if instance.assigned_to else None,
        )
        raise PermissionError("You are not authorized to act on this step.")

    action_map = {
        "approved": _handle_approve,
        "rejected": _handle_reject,
        "resubmission": _handle_resubmission,
        "delegated": _handle_delegate,
        "escalated": _handle_escalate,
    }

    if action not in action_map:
        logger.error(
            "Invalid action provided - Action: %s, Valid actions: %s",
            action,
            list(action_map.keys()),
        )
        raise ValueError(f"Unsupported action: {action}")

    logger.debug(
        "Delegating to action handler - Flow ID: %s, Step: %s, Action: %s",
        instance.flow.id,
        instance.step_number,
        action,
    )

    result = action_map[action](
        instance=instance,
        user=user,
        comment=comment,
        form_data=form_data,
        resubmission_steps=resubmission_steps,
        delegate_to=delegate_to,
    )

    logger.info(
        "Flow advancement completed - Flow ID: %s, Step: %s, Action: %s, Next step: %s",
        instance.flow.id,
        instance.step_number,
        action,
        result.step_number if result else "None (workflow complete)",
    )

    return result


def _handle_approve(
    instance: ApprovalInstance,
    user: User,
    comment: Optional[str] = None,
    form_data: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Optional[ApprovalInstance]:
    """Approve the current step, optionally validate form data.

    Args:
        instance: The approval instance to approve
        user: User performing the approval
        comment: Optional comment for the approval
        form_data: Optional form data for validation
        **kwargs: Additional keyword arguments (unused)

    Returns:
        Next approval instance if workflow continues, None if complete

    Raises:
        ValueError: If form data is required but not provided
    """
    logger.debug(
        "Processing approval - Flow ID: %s, Step: %s, User: %s, Has form: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
        bool(instance.form),
    )

    if instance.form and instance.form.schema:
        if not form_data:
            logger.error(
                "Form data required but not provided - Flow ID: %s, Step: %s",
                instance.flow.id,
                instance.step_number,
            )
            raise ValueError("This step requires form_data.")
        logger.debug(
            "Form data validation passed - Flow ID: %s, Step: %s",
            instance.flow.id,
            instance.step_number,
        )

    # CURRENT status optimization: Mark current step as approved
    instance.status = ApprovalStatus.APPROVED
    instance.action_user = user
    instance.comment = comment or ""
    instance.form_data = form_data or {}
    instance.save()

    logger.info(
        "Step approved and saved - Flow ID: %s, Step: %s, User: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
    )

    handler = get_handler_for_instance(instance)
    logger.debug(
        "Executing approval handler - Flow ID: %s, Step: %s, Handler: %s",
        instance.flow.id,
        instance.step_number,
        handler.__class__.__name__,
    )
    handler.on_approve(instance)

    # Handle role-based approval logic
    if instance.assigned_role and instance.role_selection_strategy:
        return _handle_role_based_approval_completion(instance)
    else:
        # Standard user-based approval flow
        return _advance_to_next_step(instance)


def _handle_reject(
    instance: ApprovalInstance,
    user: User,
    comment: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Reject the current step and clean up the rest of the flow.

    Args:
        instance: The approval instance to reject
        user: User performing the rejection
        comment: Optional comment for the rejection
        **kwargs: Additional keyword arguments (unused)
    """
    logger.info(
        "Processing rejection - Flow ID: %s, Step: %s, User: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
    )

    instance.status = ApprovalStatus.REJECTED
    instance.action_user = user
    instance.comment = comment or ""
    instance.save()

    logger.info(
        "Step rejected and saved - Flow ID: %s, Step: %s, User: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
    )

    remaining_steps = ApprovalInstance.objects.filter(
        flow=instance.flow,
        status__in=[ApprovalStatus.PENDING, ApprovalStatus.CURRENT],
    ).filter(
        Q(step_number__gt=instance.step_number) |  # Future steps
        (Q(step_number=instance.step_number) & ~Q(pk=instance.pk))  # Same step, different instance
    )

    remaining_count = remaining_steps.count()
    remaining_steps.delete()

    logger.info(
        "Cleaned up remaining steps - Flow ID: %s, Deleted steps: %s",
        instance.flow.id,
        remaining_count,
    )

    handler = get_handler_for_instance(instance)
    logger.debug(
        "Executing rejection handler - Flow ID: %s, Step: %s, Handler: %s",
        instance.flow.id,
        instance.step_number,
        handler.__class__.__name__,
    )
    handler.on_reject(instance)

    return None


def _handle_resubmission(
    instance: ApprovalInstance,
    user: User,
    comment: Optional[str] = None,
    resubmission_steps: Optional[List[Dict[str, Any]]] = None,
    **kwargs: Any,
) -> ApprovalInstance:
    """Request resubmission: cancel current flow & append a new set of steps.

    Resubmission is used when the current approval step determines that additional
    review or corrections are needed before the workflow can continue. This function:

    1. Marks the current instance as NEEDS_RESUBMISSION
    2. Deletes any remaining pending steps in the workflow
    3. Creates new approval steps as specified in resubmission_steps
    4. Calls the on_resubmission handler for custom business logic
    5. Returns the first new step for the requester to continue processing

    The resubmission mechanism allows for dynamic workflow modification based on
    runtime decisions by reviewers. Common use cases include:
    - Adding additional reviewers (legal, security, compliance)
    - Requesting document revisions before continuing
    - Escalating to higher authorities
    - Parallel review processes

    Args:
        instance: The approval instance requesting resubmission. This instance
                 will be marked with NEEDS_RESUBMISSION status.
        user: User performing the resubmission request. Must have permission
              to act on the current step.
        comment: Optional comment explaining why resubmission is needed.
                This is stored with the instance and passed to handlers.
        resubmission_steps: List of new steps to add to the workflow. Each step
                           should contain 'step', 'assigned_to', and optionally 'form'.
                           Step numbers will be auto-calculated starting from the
                           next available number in the flow.
        **kwargs: Additional keyword arguments (unused, reserved for future use)

    Returns:
        First new approval instance created for resubmission. This allows the
        caller to immediately continue processing or redirect to the new step.

    Raises:
        ValueError: If resubmission_steps is not provided or empty.
                   At least one new step must be specified for resubmission.

    Example:
        # Manager requests legal review before final approval
        legal_step = _handle_resubmission(
            instance=current_step,
            user=manager,
            comment="Legal review required for compliance",
            resubmission_steps=[
                {"step": 1, "assigned_to": legal_reviewer},
                {"step": 2, "assigned_to": director}  # Final approval
            ]
        )

        # The current_step is now NEEDS_RESUBMISSION
        # legal_step is the new first step to be processed
    """
    logger.info(
        "Processing resubmission - Flow ID: %s, Step: %s, User: %s, New steps: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
        len(resubmission_steps) if resubmission_steps else 0,
    )

    if not resubmission_steps:
        logger.error(
            "Resubmission steps not provided - Flow ID: %s, Step: %s",
            instance.flow.id,
            instance.step_number,
        )
        raise ValueError("resubmission_steps must be provided.")

    instance.status = ApprovalStatus.NEEDS_RESUBMISSION
    instance.action_user = user
    instance.comment = comment or ""
    instance.save()

    logger.info(
        "Resubmission status saved - Flow ID: %s, Step: %s, User: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
    )

    # Delete remaining steps in this flow (including CURRENT status)
    remaining_steps = ApprovalInstance.objects.filter(
        flow=instance.flow,
        step_number__gt=instance.step_number,
        status__in=[ApprovalStatus.PENDING, ApprovalStatus.CURRENT],
    )

    remaining_count = remaining_steps.count()
    remaining_steps.delete()

    logger.info(
        "Cleaned up remaining steps for resubmission - Flow ID: %s, Deleted steps: %s",
        instance.flow.id,
        remaining_count,
    )

    # Create a new set of steps with step_number continuing from last
    last_step = (
        ApprovalInstance.objects.filter(flow=instance.flow)
        .order_by("-step_number")
        .first()
    )
    next_step_number = last_step.step_number + 1 if last_step else 1

    logger.debug(
        "Creating new resubmission steps - Flow ID: %s, Starting step: %s, Count: %s",
        instance.flow.id,
        next_step_number,
        len(resubmission_steps),
    )

    created_steps = []
    for i, step in enumerate(resubmission_steps):
        # CURRENT status optimization: First new step is CURRENT, rest are PENDING
        status = ApprovalStatus.CURRENT if i == 0 else ApprovalStatus.PENDING
        new_step = ApprovalInstance.objects.create(
            flow=instance.flow,
            step_number=next_step_number + i,
            assigned_to=step["assigned_to"],
            status=status,
            form=step.get("form"),
            sla_duration=step.get("sla_duration"),
            allow_higher_level=step.get("allow_higher_level", False),
            extra_fields=step.get("extra_fields"),
        )
        created_steps.append(new_step)

    logger.info(
        "Created resubmission steps - Flow ID: %s, Steps: %s",
        instance.flow.id,
        [step.step_number for step in created_steps],
    )

    handler = get_handler_for_instance(instance)
    logger.debug(
        "Executing resubmission handler - Flow ID: %s, Step: %s, Handler: %s",
        instance.flow.id,
        instance.step_number,
        handler.__class__.__name__,
    )
    handler.on_resubmission(instance)

    first_new_step = ApprovalInstance.objects.get(
        flow=instance.flow, step_number=next_step_number
    )

    logger.info(
        "Resubmission completed - Flow ID: %s, First new step: %s",
        instance.flow.id,
        first_new_step.step_number,
    )

    return first_new_step


def _handle_delegate(
    instance: ApprovalInstance,
    user: User,
    comment: Optional[str] = None,
    delegate_to: Optional[User] = None,
    **kwargs: Any,
) -> ApprovalInstance:
    """Delegate the current step to another user by creating a new step record."""
    logger.info(
        "Processing delegation - Flow ID: %s, Step: %s, User: %s, Delegate to: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
        delegate_to.username if delegate_to else None,
    )

    if not delegate_to:
        raise ValueError("delegate_to user must be provided.")

    instance.status = ApprovalStatus.DELEGATED
    instance.action_user = user
    instance.comment = comment or ""
    instance.save()

    delegated_step = ApprovalInstance.objects.create(
        flow=instance.flow,
        step_number=instance.step_number,
        assigned_to=delegate_to,
        status=ApprovalStatus.CURRENT,
        form=instance.form,
        sla_duration=instance.sla_duration,
        allow_higher_level=instance.allow_higher_level,
        extra_fields=instance.extra_fields,
    )

    handler = get_handler_for_instance(instance)
    handler.on_delegate(instance)

    return delegated_step


def _handle_escalate(
    instance: ApprovalInstance,
    user: User,
    comment: Optional[str] = None,
    **kwargs: Any,
) -> ApprovalInstance:
    """Escalate the current step to a head manager by creating a new step record."""
    logger.info(
        "Processing escalation - Flow ID: %s, Step: %s, User: %s",
        instance.flow.id,
        instance.step_number,
        user.username,
    )

    head_manager_field = getattr(settings, "APPROVAL_HEAD_MANAGER_FIELD", None)
    escalation_user = None

    # Try to get head manager from direct field first
    if head_manager_field:
        escalation_user = getattr(user, head_manager_field, None)

    # Fallback to role hierarchy if no direct head manager found
    if not escalation_user:
        role_field = getattr(settings, "APPROVAL_ROLE_FIELD", "role")
        current_role = getattr(user, role_field, None)
        
        if current_role:
            parent_role = current_role.parent if hasattr(current_role, 'parent') else None
            if parent_role:
                escalation_user = User.objects.filter(**{role_field: parent_role}).first()

    if not escalation_user:
        raise ValueError("No head manager or higher role user found for escalation.")

    instance.status = ApprovalStatus.ESCALATED
    instance.action_user = user
    instance.comment = comment or ""
    instance.save()

    escalated_step = ApprovalInstance.objects.create(
        flow=instance.flow,
        step_number=instance.step_number,
        assigned_to=escalation_user,
        status=ApprovalStatus.CURRENT,
        form=instance.form,
        sla_duration=instance.sla_duration,
        allow_higher_level=instance.allow_higher_level,
        extra_fields=instance.extra_fields,
    )

    handler = get_handler_for_instance(instance)
    handler.on_escalate(instance)

    return escalated_step


def get_dynamic_form_model() -> Optional[Type[Any]]:
    """Resolve the optional DynamicForm model from settings.

    Returns:
        Model class if configured in settings, None otherwise

    Raises:
        LookupError: If configured model path is invalid
        ValueError: If configured model path format is invalid
    """
    model_path = getattr(settings, "APPROVAL_DYNAMIC_FORM_MODEL", None)
    logger.debug("Resolving dynamic form model - Path: %s", model_path)

    if not model_path:
        logger.debug("No dynamic form model configured")
        return None

    try:
        model = apps.get_model(model_path)
        logger.debug("Dynamic form model resolved - Model: %s", model.__name__)
        return model
    except (LookupError, ValueError) as e:
        logger.warning(
            "Failed to resolve dynamic form model - Path: %s, Error: %s",
            model_path,
            str(e),
        )
        return None


def start_flow(obj: Model, steps: List[Dict[str, Any]]) -> ApprovalFlow:
    """Start a new ApprovalFlow for a given object.

    Args:
        obj: The Django model instance this flow is for
        steps: List of step dictionaries with keys:
               - 'step': Step number (positive integer)
               - 'assigned_to': User instance or None
               - 'form': Optional form instance or ID
               - 'sla_duration': Optional duration for SLA tracking (e.g., timedelta(days=2))
               - 'allow_higher_level': Optional boolean to allow higher role users to approve (default: False)
               - 'extra_fields': Optional dictionary of additional custom fields

    Returns:
        ApprovalFlow instance with created approval steps

    Raises:
        ValueError: If input validation fails
        TypeError: If step data types are incorrect
    """
    logger.info(
        "Starting new approval flow - Object: %s (%s), Steps count: %s",
        obj.__class__.__name__,
        obj.pk,
        len(steps),
    )

    if not isinstance(steps, list):
        logger.error(
            "Invalid steps parameter - Expected list, got: %s", type(steps).__name__
        )
        raise ValueError("steps must be a list of step dictionaries")

    dynamic_form_model = get_dynamic_form_model()

    logger.debug(
        "Validating flow steps - Count: %s, Has form model: %s",
        len(steps),
        bool(dynamic_form_model),
    )

    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            logger.error(
                "Invalid step at index %s - Expected dict, got: %s",
                i,
                type(step).__name__,
            )
            raise ValueError(
                f"Step at index {i} must be a dict, got {type(step).__name__}"
            )
        if "step" not in step:
            logger.error("Missing 'step' key in step at index %s", i)
            raise ValueError(f"Missing 'step' key in step at index {i}")
        if "assigned_to" not in step:
            logger.error("Missing 'assigned_to' key in step at index %s", i)
            raise ValueError(f"Missing 'assigned_to' key in step at index {i}")
        if not isinstance(step["step"], int) or step["step"] <= 0:
            logger.error("Invalid step number at index %s - Value: %s", i, step["step"])
            raise ValueError(f"'step' must be a positive integer at index {i}")
        if step["assigned_to"] is not None and not isinstance(
            step["assigned_to"], User
        ):
            logger.error(
                "Invalid assigned_to at index %s - Expected User, got: %s",
                i,
                type(step["assigned_to"]).__name__,
            )
            raise ValueError(f"'assigned_to' must be a User or None at index {i}")

        # Validate form if used
        if "form" in step:
            if not dynamic_form_model:
                logger.error(
                    "Form provided but no dynamic form model configured - Step index: %s",
                    i,
                )
                raise ValueError(
                    f"'form' provided in step {i}, but no APPROVAL_DYNAMIC_FORM_MODEL is configured."
                )
            form_obj = step["form"]
            if isinstance(form_obj, int):
                # Resolve by ID
                if hasattr(dynamic_form_model, "objects"):
                    logger.debug(
                        "Resolving form by ID - Step: %s, Form ID: %s", i, form_obj
                    )
                    step["form"] = dynamic_form_model.objects.get(pk=form_obj)
                else:
                    logger.error(
                        "Dynamic form model has no objects manager - Step: %s", i
                    )
                    raise ValueError(
                        f"Dynamic form model at step {i} has no objects manager"
                    )
            elif not isinstance(form_obj, dynamic_form_model):
                logger.error(
                    "Invalid form object at step %s - Expected: %s, Got: %s",
                    i,
                    dynamic_form_model.__name__,
                    type(form_obj).__name__,
                )
                raise ValueError(
                    f"'form' in step {i} must be a {dynamic_form_model.__name__} instance or ID."
                )

        logger.debug(
            "Step validated - Index: %s, Step number: %s, Assigned to: %s, Has form: %s",
            i,
            step["step"],
            step["assigned_to"].username if step["assigned_to"] else None,
            "form" in step,
        )

    content_type = ContentType.objects.get_for_model(obj.__class__)
    flow = ApprovalFlow.objects.create(content_type=content_type, object_id=str(obj.pk))

    logger.info(
        "Created approval flow - Flow ID: %s, Object: %s (%s)",
        flow.id,
        obj.__class__.__name__,
        obj.pk,
    )

    # CURRENT status optimization: Sort steps and set first as CURRENT
    sorted_steps = sorted(steps, key=lambda x: x["step"])
    created_instances = []

    for i, step_data in enumerate(sorted_steps):
        # First step (lowest step number) is CURRENT, rest are PENDING
        status = ApprovalStatus.CURRENT if i == 0 else ApprovalStatus.PENDING
        instance = ApprovalInstance.objects.create(
            flow=flow,
            step_number=step_data["step"],
            status=status,
            assigned_to=step_data["assigned_to"],
            form=step_data.get("form"),
            sla_duration=step_data.get("sla_duration"),
            allow_higher_level=step_data.get("allow_higher_level", False),
            extra_fields=step_data.get("extra_fields"),
        )
        created_instances.append(instance)

    logger.info(
        "Created approval instances - Flow ID: %s, Instances: %s",
        flow.id,
        [f"Step {inst.step_number}" for inst in created_instances],
    )

    return flow


def _handle_role_based_approval_completion(instance: ApprovalInstance) -> Optional[ApprovalInstance]:
    """Handle completion logic for role-based approvals based on strategy.
    
    Args:
        instance: The just-approved role-based approval instance
        
    Returns:
        Next approval instance if workflow continues, None if complete
    """
    logger.debug(
        "Processing role-based approval completion - Flow ID: %s, Step: %s, Strategy: %s",
        instance.flow.id,
        instance.step_number,
        instance.role_selection_strategy,
    )
    
    if instance.role_selection_strategy == RoleSelectionStrategy.ANYONE:
        # For "anyone" strategy, first approval completes the step
        # Delete all other CURRENT instances for this step
        other_current_instances = ApprovalInstance.objects.filter(
            flow=instance.flow,
            step_number=instance.step_number,
            status=ApprovalStatus.CURRENT,
            assigned_role_content_type=instance.assigned_role_content_type,
            assigned_role_object_id=instance.assigned_role_object_id,
        ).exclude(pk=instance.pk)
        
        cancelled_count = other_current_instances.count()
        other_current_instances.delete()
        
        logger.info(
            "ANYONE strategy: Deleted %s other current instances - Flow ID: %s, Step: %s",
            cancelled_count,
            instance.flow.id,
            instance.step_number,
        )
        
        return _advance_to_next_step(instance)
        
    elif instance.role_selection_strategy == RoleSelectionStrategy.CONSENSUS:
        # For "consensus" strategy, check if all instances for this step are approved
        remaining_current_instances = ApprovalInstance.objects.filter(
            flow=instance.flow,
            step_number=instance.step_number,
            status=ApprovalStatus.CURRENT,
            assigned_role_content_type=instance.assigned_role_content_type,
            assigned_role_object_id=instance.assigned_role_object_id,
        ).exists()
        
        if remaining_current_instances:
            logger.info(
                "CONSENSUS strategy: Waiting for more approvals - Flow ID: %s, Step: %s",
                instance.flow.id,
                instance.step_number,
            )
            return None  # Stay on current step, wait for more approvals
        else:
            logger.info(
                "CONSENSUS strategy: All approvals received - Flow ID: %s, Step: %s",
                instance.flow.id,
                instance.step_number,
            )
            return _advance_to_next_step(instance)
            
    elif instance.role_selection_strategy == RoleSelectionStrategy.ROUND_ROBIN:
        # For "round_robin" strategy, single approval completes the step
        return _advance_to_next_step(instance)
    
    else:
        logger.error(
            "Unknown role selection strategy - Flow ID: %s, Step: %s, Strategy: %s",
            instance.flow.id,
            instance.step_number,
            instance.role_selection_strategy,
        )
        raise ValueError(f"Unknown role selection strategy: {instance.role_selection_strategy}")


def _advance_to_next_step(instance: ApprovalInstance) -> Optional[ApprovalInstance]:
    """Advance to the next step in the workflow.
    
    Args:
        instance: The current completed approval instance
        
    Returns:
        Next approval instance if workflow continues, None if complete
    """
    # Find next step by ordering step numbers (safer than assuming step+1)
    next_step = ApprovalInstance.objects.filter(
        flow=instance.flow,
        step_number__gt=instance.step_number,
        status=ApprovalStatus.PENDING,
    ).order_by('step_number').first()

    if next_step:
        # For role-based approvals, we might need to create multiple instances
        if next_step.assigned_role and next_step.role_selection_strategy:
            return _activate_role_based_step(next_step)
        else:
            # Standard user-based approval
            next_step.status = ApprovalStatus.CURRENT
            next_step.save()

            logger.info(
                "Next step found and set as CURRENT - Flow ID: %s, Current step: %s, Next step: %s",
                instance.flow.id,
                instance.step_number,
                next_step.step_number,
            )
            return next_step

    logger.info(
        "Final approval reached - Flow ID: %s, Step: %s, Executing final approval handler",
        instance.flow.id,
        instance.step_number,
    )
    handler = get_handler_for_instance(instance)
    handler.on_final_approve(instance)
    return None


def _activate_role_based_step(step_template: ApprovalInstance) -> ApprovalInstance:
    """Activate a role-based step by creating instances for all required users.
    
    Args:
        step_template: The template step with role assignment
        
    Returns:
        First created approval instance (for consistency with API)
    """
    from .utils import get_users_for_role, get_user_with_least_assignments
    
    logger.info(
        "Activating role-based step - Flow ID: %s, Step: %s, Strategy: %s",
        step_template.flow.id,
        step_template.step_number,
        step_template.role_selection_strategy,
    )
    
    # Get users for the assigned role
    role_users = get_users_for_role(step_template.assigned_role)
    
    if not role_users:
        logger.error(
            "No users found for role - Flow ID: %s, Step: %s, Role: %s",
            step_template.flow.id,
            step_template.step_number,
            step_template.assigned_role,
        )
        raise ValueError(f"No users found for role: {step_template.assigned_role}")
    
    created_instances = []
    
    if step_template.role_selection_strategy == RoleSelectionStrategy.ANYONE:
        # Create approval instances for all users with this role, all CURRENT
        for user in role_users:
            instance = ApprovalInstance.objects.create(
                flow=step_template.flow,
                step_number=step_template.step_number,
                assigned_to=user,
                assigned_role_content_type=step_template.assigned_role_content_type,
                assigned_role_object_id=step_template.assigned_role_object_id,
                role_selection_strategy=step_template.role_selection_strategy,
                status=ApprovalStatus.CURRENT,
                form=step_template.form,
                sla_duration=step_template.sla_duration,
                allow_higher_level=step_template.allow_higher_level,
                extra_fields=step_template.extra_fields,
            )
            created_instances.append(instance)
            
    elif step_template.role_selection_strategy == RoleSelectionStrategy.CONSENSUS:
        # Create approval instances for all users with this role, all CURRENT
        for user in role_users:
            instance = ApprovalInstance.objects.create(
                flow=step_template.flow,
                step_number=step_template.step_number,
                assigned_to=user,
                assigned_role_content_type=step_template.assigned_role_content_type,
                assigned_role_object_id=step_template.assigned_role_object_id,
                role_selection_strategy=step_template.role_selection_strategy,
                status=ApprovalStatus.CURRENT,
                form=step_template.form,
                sla_duration=step_template.sla_duration,
                allow_higher_level=step_template.allow_higher_level,
                extra_fields=step_template.extra_fields,
            )
            created_instances.append(instance)
            
    elif step_template.role_selection_strategy == RoleSelectionStrategy.ROUND_ROBIN:
        # Find user with least current assignments
        selected_user = get_user_with_least_assignments(role_users)
        
        instance = ApprovalInstance.objects.create(
            flow=step_template.flow,
            step_number=step_template.step_number,
            assigned_to=selected_user,
            assigned_role_content_type=step_template.assigned_role_content_type,
            assigned_role_object_id=step_template.assigned_role_object_id,
            role_selection_strategy=step_template.role_selection_strategy,
            status=ApprovalStatus.CURRENT,
            form=step_template.form,
            sla_duration=step_template.sla_duration,
            allow_higher_level=step_template.allow_higher_level,
            extra_fields=step_template.extra_fields,
        )
        created_instances.append(instance)
    
    # Delete the template step
    step_template.delete()
    
    logger.info(
        "Created %s approval instances for role-based step - Flow ID: %s, Step: %s",
        len(created_instances),
        step_template.flow.id,
        step_template.step_number,
    )
    
    return created_instances[0] if created_instances else None
