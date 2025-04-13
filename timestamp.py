import re
from datetime import timedelta

def seconds_to_hhmmssms(seconds):
    td = timedelta(seconds=float(seconds))
    total_seconds = int(td.total_seconds())
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}:{milliseconds:03}"

def convert_timestamps(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    converted_lines = []
    timestamp_pattern = re.compile(r"START:\s*([\d.]+)\s*\|\s*END\s*([\d.]+)")

    for line in lines:
        match = timestamp_pattern.search(line)
        if match:
            start = seconds_to_hhmmssms(match.group(1))
            end = seconds_to_hhmmssms(match.group(2))
            # replace only the matched part in the line
            new_line = timestamp_pattern.sub(f"START: {start} | END {end}", line)
            converted_lines.append(new_line)
        else:
            converted_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(converted_lines)

# Example usage:
convert_timestamps("input.txt", "output.txt")