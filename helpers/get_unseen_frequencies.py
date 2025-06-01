def get_unseen_frequencies(freq_dict, seen_frequencies):
  # Get all frequencies
  all_freqs = set(range(len(freq_dict)))
  print(all_freqs)
  # Take the difference of the sets
  unseen_freqs_set = all_freqs - seen_frequencies
  print(unseen_freqs_set)
  # Convert back to sorted list
  unseen_freqs = sorted(unseen_freqs_set)
  print(unseen_freqs)

  return unseen_freqs