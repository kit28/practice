from datetime import timedelta
import re

def seconds_to_hhmmssms(seconds):
    td = timedelta(seconds=float(seconds))
    total_seconds = int(td.total_seconds())
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}:{milliseconds:03}"

def convert_timestamps(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    def replace_match(match):
        start = seconds_to_hhmmssms(match.group(1))
        end = seconds_to_hhmmssms(match.group(2))
        return f"START: {start} | END {end}"

    # Regex pattern to match lines like START: 6.0 | END 9.0
    pattern = r"START:\s*([\d.]+)\s*\|\s*END\s*([\d.]+)"
    updated_content = re.sub(pattern, replace_match, content)

    with open(output_file, 'w') as f:
        f.write(updated_content)

# Example usage:
convert_timestamps("input.txt", "output.txt")