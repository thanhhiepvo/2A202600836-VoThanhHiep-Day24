"""Verify Agent Governance Toolkit policies for MedViet lab."""
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from agent_os.policies import (
    PolicyAction,
    PolicyCondition,
    PolicyDefaults,
    PolicyDocument,
    PolicyEvaluator,
    PolicyOperator,
    PolicyRule,
)


def build_evaluator() -> PolicyEvaluator:
    policy = PolicyDocument(
        name="medviet-data-policy",
        version="1.0",
        defaults=PolicyDefaults(action=PolicyAction.DENY),
        rules=[
            PolicyRule(
                name="allow-anonymized-read",
                condition=PolicyCondition(
                    field="dataset", operator=PolicyOperator.EQ, value="anonymized"
                ),
                action=PolicyAction.ALLOW,
                priority=100,
            ),
            PolicyRule(
                name="allow-aggregated-analyst",
                condition=PolicyCondition(
                    field="dataset", operator=PolicyOperator.EQ, value="aggregated"
                ),
                action=PolicyAction.ALLOW,
                priority=110,
            ),
            PolicyRule(
                name="block-raw-pii",
                condition=PolicyCondition(
                    field="dataset", operator=PolicyOperator.EQ, value="raw_pii"
                ),
                action=PolicyAction.DENY,
                priority=200,
            ),
            PolicyRule(
                name="block-export-outside-vn",
                condition=PolicyCondition(
                    field="destination", operator=PolicyOperator.NE, value="VN"
                ),
                action=PolicyAction.DENY,
                priority=300,
            ),
            PolicyRule(
                name="block-delete-actions",
                condition=PolicyCondition(
                    field="action", operator=PolicyOperator.EQ, value="delete"
                ),
                action=PolicyAction.DENY,
                priority=400,
            ),
        ],
    )
    return PolicyEvaluator(policies=[policy])


def main() -> None:
    evaluator = build_evaluator()
    cases = [
        ({"dataset": "anonymized", "action": "read"}, True),
        ({"dataset": "aggregated", "action": "read", "role": "data_analyst"}, True),
        ({"dataset": "raw_pii", "action": "read"}, False),
        ({"dataset": "anonymized", "action": "export", "destination": "US"}, False),
        ({"dataset": "anonymized", "action": "export", "destination": "VN"}, True),
        ({"dataset": "anonymized", "action": "delete"}, False),
    ]

    for ctx, expected in cases:
        result = evaluator.evaluate(ctx)
        allowed = getattr(result, "allowed", None)
        requires_approval = getattr(result, "requires_approval", False)

        if expected == "approval":
            ok = requires_approval or str(result).lower().find("approval") >= 0
            label = "REQUIRE_APPROVAL" if ok else str(result)
        else:
            ok = bool(allowed) == expected
            label = "ALLOW" if allowed else "DENY"

        status = "✓" if ok else "✗"
        print(f"{status} {ctx} → {label}")

    print("\n✓ AGT policy demo completed")


if __name__ == "__main__":
    main()
