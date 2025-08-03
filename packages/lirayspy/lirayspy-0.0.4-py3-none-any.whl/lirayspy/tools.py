from enum import Enum


class ExecStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanStatus(Enum):
    NOT_ASSIGNED = "not_assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class LayerClass(Enum):
    # Primary Layers
    PLAN_AREA = "plan_area"
    PARCELS = "parcels"
    CABINET = "cabinet"

    # Network Logical Points
    MST = "mst"
    SPLICE = "splice"
    SPLICE_MST = "splice_mst"
    RESIDENTIAL = "residential"

    # Hand-Holes
    VAULT_24X36 = "vault_24x36"
    VAULT_17X30 = "vault_17x30"
    VAULT_10X15 = "vault_10x15"
    VAULT_OTHERS = "vault_others"

    # Fiber
    FIBER_24 = "fiber_24"
    FIBER_48 = "fiber_48"
    FIBER_72 = "fiber_72"
    FIBER_144 = "fiber_144"
    FIBER_288 = "fiber_288"
    FIBER_TAIL = "fiber_tail"
    FIBER_DROP = "fiber_drop"

    # Conduits
    CONDUIT_075 = "conduit_075"
    CONDUIT_125 = "conduit_125"

    # Tunnels
    TUNNEL = "tunnel"

    # Downloaded Layers
    HIGHWAYS_LINES = "highways_lines"
    BUILDINGS = "buildings"

    # Manually Created Layers
    MST_CLUSTER_AREA = "mst_cluster_area"
    MST_SERVICE_AREA = "mst_service_area"
    CORNER_POINTS = "corner_points"
    FIBER_BRANCH_AREA = "fiber_branch_area"

    # Calculated Layers
    HIGHWAYS_AREA = "highways_area"
    ESCAPE_POINTS = "escape_points"


class GeomType(Enum):
    POINT = "point"
    LINESTRING = "linestring"
    POLYGON = "polygon"


def join_urls(base: str, *args: str) -> str:
    steps = []

    for step in ([base] + [arg for arg in args if isinstance(arg, str)]):
        if step.startswith("/"):
            step = step[1:]
        if step.endswith("/"):
            step = step[:-1]
        steps.append(step)

    return "/".join(steps)
