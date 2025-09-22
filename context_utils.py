import re
from typing import Any, Dict


def _normalize_key(key: str) -> str:
    """Convert keys to ``snake_case`` for consistent access."""
    key = key.replace('-', '_').replace(' ', '_')
    key = re.sub(r"(?<!^)(?=[A-Z])", "_", key)
    return key.lower()


def _add_model_attrs(ctx: Dict[str, Any], obj: Any, prefix: str = "") -> None:
    """Add SQLAlchemy model column attributes to ``ctx``.

    Only simple column values are copied; relationships and private attributes
    are ignored.  ``prefix`` can be supplied to namespace the keys.
    """
    if not obj:
        return
    table = getattr(obj, "__table__", None)
    columns = getattr(table, "columns", [])
    for column in columns:
        name = column.key
        value = getattr(obj, name, None)
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            continue
        key = f"{prefix}_{name}" if prefix else name
        ctx[_normalize_key(key)] = value


def build_context(loan_summary: Any) -> Dict[str, Any]:
    """Build a flat dictionary of context data for a loan summary.

    The function gathers attributes from ``LoanSummary`` and selected related
    models such as ``ReportFields``, ``Application`` and ``User``.  Keys are
    normalised to ``snake_case``.  The ``loan_notes`` relationship is skipped.
    """
    context: Dict[str, Any] = {}

    # Core loan summary fields
    _add_model_attrs(context, loan_summary)

    # Include formatted string snapshot for mapping (loan_data table)
    _add_model_attrs(context, getattr(loan_summary, 'loan_data', None), prefix='loan_data')

    # Related report fields
    rf = getattr(loan_summary, "report_fields", None)
    if rf:
        try:
            data = rf.to_dict()
        except Exception:  # pragma: no cover - fallback for unexpected issues
            data = {}
            _add_model_attrs(data, rf)
        for key, value in data.items():
            if value is None or isinstance(value, (dict, list)):
                continue
            context[_normalize_key(key)] = value

    # Related application details if available
    application = getattr(loan_summary, "application", None)
    if application:
        _add_model_attrs(context, application, prefix="application")

    # User information
    user = getattr(loan_summary, "user", None)
    if user:
        for field in ["first_name", "last_name", "email", "phone", "company"]:
            value = getattr(user, field, None)
            if value is not None:
                context[_normalize_key(f"user_{field}")] = value
        full_name = getattr(user, "full_name", None)
        if full_name:
            context["user_full_name"] = full_name
        # Provide a sensible default for client_name if not set elsewhere
        context.setdefault("client_name", getattr(rf, "client_name", None) or full_name)

    # Ensure we don't include loan notes or other relationship data
    context.pop("loan_notes", None)

    return context

