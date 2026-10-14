from dataclasses import dataclass, asdict

ERROR, WARNING, INFO = "error", "warning", "info"


@dataclass
class Finding:
    file: str
    severity: str
    rule: str
    clause: str      # clause of the specification the rule rests on ("" when none governs it)
    path: str        # JSON pointer into the file
    message: str

    def as_dict(self):
        return asdict(self)

    def line(self):
        where = self.path or "/"
        cl = f" [{self.clause}]" if self.clause else ""
        return f"{self.file}: {self.severity} {self.rule}{cl} at {where}: {self.message}"
