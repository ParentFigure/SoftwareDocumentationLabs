from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ViolationRecord:
    summons_number: str
    plate: str
    state: str
    license_type: str
    issue_date: str
    violation_time: str
    violation: str
    fine_amount: str
    penalty_amount: str
    payment_amount: str
    amount_due: str
    county: str
    issuing_agency: str
    violation_status: str

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> "ViolationRecord":
        return cls(
            summons_number=row.get("summons_number", ""),
            plate=row.get("plate", ""),
            state=row.get("state", ""),
            license_type=row.get("license_type", ""),
            issue_date=row.get("issue_date", ""),
            violation_time=row.get("violation_time", ""),
            violation=row.get("violation", ""),
            fine_amount=row.get("fine_amount", ""),
            penalty_amount=row.get("penalty_amount", ""),
            payment_amount=row.get("payment_amount", ""),
            amount_due=row.get("amount_due", ""),
            county=row.get("county", ""),
            issuing_agency=row.get("issuing_agency", ""),
            violation_status=row.get("violation_status", ""),
        )

    def to_line(self) -> str:
        return (
            f"summons_number={self.summons_number}; plate={self.plate}; state={self.state}; "
            f"license_type={self.license_type}; issue_date={self.issue_date}; "
            f"violation_time={self.violation_time}; violation={self.violation}; "
            f"fine_amount={self.fine_amount}; penalty_amount={self.penalty_amount}; "
            f"payment_amount={self.payment_amount}; amount_due={self.amount_due}; "
            f"county={self.county}; issuing_agency={self.issuing_agency}; "
            f"violation_status={self.violation_status}"
        )
