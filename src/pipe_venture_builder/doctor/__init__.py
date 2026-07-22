"""Read-only portable readiness diagnostics."""

from .checks import DoctorCheck, DoctorReport, run_doctor

__all__ = ["DoctorCheck", "DoctorReport", "run_doctor"]
