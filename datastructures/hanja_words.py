from dataclasses import dataclass, field

@dataclass
class HanjaWords:
  beginner: list[tuple[tuple[str, str], int]] = field(default_factory=list) # All words with dictionary entries also in 5800 list
  novice: list[tuple[tuple[str, str], int]] = field(default_factory=list)
  advanced: list[tuple[tuple[str, str], int]] = field(default_factory=list)
  avg_freq_beginner: float = field(default_factory=float) # Average frequency of words in 5800 list
  avg_freq_novice: float = field(default_factory=float)
  avg_freq_advanced: float = field(default_factory=float)
