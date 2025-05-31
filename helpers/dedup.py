## This function helps to deduplicate translations/definitions taken from the dictionary, etc.
def dedup(seq: list[str]) -> list[str]:
  seen = set()
  return [x for x in seq if not (x in seen or seen.add(x))]