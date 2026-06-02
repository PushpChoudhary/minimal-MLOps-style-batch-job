# Save this as clean_data.py and run it once to fix your mock data
with open('data.csv', 'r') as file:
    lines = file.readlines()

with open('data_cleaned.csv', 'w') as file:
    for line in lines:
        # Strip leading/trailing whitespaces and quotation marks
        clean_line = line.strip().strip('"') + '\n'
        file.write(clean_line)

print("Data cleaned successfully!")