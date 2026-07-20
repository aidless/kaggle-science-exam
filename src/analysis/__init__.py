"""Analysis modules for stage analysis tooling."""

from .stage_streak import build_streak
from .stage_leaderboard import build_leaderboard
from .stage_grep import build_grep
from .stage_coverage import build_coverage
from .stage_timeline import build_timeline
from .stage_cadence import build_cadence
from .stage_suggestion import collect_suggestions
from .stage_summary import build_summary
from .stage_trend import build_trend
from .stage_fanout import build_fanout
from .stage_clusters import build_clusters
from .stage_backlog import build_backlog
from .stage_coupling import build_coupling
from .stage_maturity import build_maturity
from .stage_velocity import collect_velocity
from .stage_density_curve import collect_curves
from .stage_distribution import build_distribution
from .stage_calendar import collect_calendar

__all__ = [
    "build_streak",
    "build_leaderboard",
    "build_grep",
    "build_coverage",
    "build_timeline",
    "build_cadence",
    "collect_suggestions",
    "build_summary",
    "build_trend",
    "build_fanout",
    "build_clusters",
    "build_backlog",
    "build_coupling",
    "build_maturity",
    "collect_velocity",
    "collect_curves",
    "build_distribution",
    "collect_calendar",
]
