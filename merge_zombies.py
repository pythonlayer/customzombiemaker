# Read files
with open("new_zombies.txt", "r", encoding="utf-8") as f:
    master_lines = f.readlines()

with open("master_list.txt", "r", encoding="utf-8") as f:
    codenames_raw = f.read().strip()

# Split database codenames (pipe-separated)
codenames_db = codenames_raw.split("|")

# Build a reference order from masterlist
# Only take the first codename if multiple are given with slashes
reference_order = []
for line in master_lines:
    line = line.strip()
    if " - " in line:
        _, code = line.split(" - ", 1)
        # Take only first part if slashed
        code = code.split("/")[0]
        # Only include if it exists in the database
        if code in codenames_db:
            reference_order.append(code)

# Final sorted list (strictly from database & masterlist)
sorted_codenames = reference_order

# Join back with pipe
result = "|".join(sorted_codenames)

# Print or save to file
print(result)
# Optionally save:
# with open("codenames_sorted.txt", "w", encoding="utf-8") as f:
#     f.write(result)
