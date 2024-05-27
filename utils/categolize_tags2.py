import csv
import os
import json
import sys
import random

from yaml import safe_load, full_load, unsafe_load, safe_dump

import cohere
import cohere.core.api_error

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pickle_memory import load_memory, save_memory
from dotenv import load_dotenv
load_dotenv()



class YamlUtils:
    @staticmethod
    def normal_parse(text:str) -> dict:
        try:
            return safe_load(text)
        except Exception:
            pass

        try:
            return full_load(text)
        except Exception:
            pass

        try:
            return unsafe_load(text)
        except Exception:
            pass

        raise ValueError("Failed to parse YAML format")
    
    @staticmethod
    def trim_yaml(text:str) -> str:
        if not text.startswith("-") and not text.startswith(" ") and not text.startswith("#"):
            if '```yaml' in text:
                text = text.split('```yaml')[1].split('```')[0]
                return text
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
                return text
        return None
    
    @staticmethod
    def yaml_format(text:str) -> dict:
        # try nomal parse
        try:
            return YamlUtils.normal_parse(text)
        except Exception:
            pass

        replace_text = text.replace("\\'s", "_e_a_s").replace("'s", "_a_s").replace("'", "\"").replace("_e_a_s", "'s").replace("_a_s", "'s")
        lines = replace_text.split("\n")
        for i, line in enumerate(lines):
            line = line.strip("\n")
            if line.endswith(":\""):
                lines[i] = line.replace("\"", "")
        replace_text = "\n".join(lines) 

        try:
            return YamlUtils.normal_parse(replace_text)
        except Exception:
            pass

        # try trim and parse
        trim_text = ""
        try:
            trim_text = YamlUtils.trim_yaml(text)
            if trim_text:
                return YamlUtils.yaml_format(trim_text)
        except Exception:
            pass

        if trim_text:
            lines = trim_text.split("\n")
            for i, line in enumerate(lines):
                line = line.strip("\n")
                if not (line.startswith(" ") or line.startswith("- ")):
                    lines[i] = f"- {line}"
            trim_text = "\n".join(lines)
            try:
                return YamlUtils.normal_parse(trim_text)
            except Exception:
                pass

        # raise error
        print (f"Failed to parse YAML format: {text}")
        raise ValueError("Failed to parse YAML format")


co = cohere.Client(os.getenv("COHERE_API_KEY"))

with open('tag_category2.json', 'r', encoding='utf-8') as file:
    data = json.loads(file.read())

nocate = []
cated = []

logtags = []

for tag, categories in data.items():
    print (tag, categories)
    if not categories or len(categories) <= 1:
        nocate.append(tag)
    else:
        cated.append(tag)
        if len(categories) > 4:
            logtags.append(tag)

long_tags = random.sample(logtags, 10)
random_tags = random.sample(cated, 20)

nocate_data = {}
for tag in nocate:
    nocate_data[tag] = data[tag]
    if nocate_data[tag] is None:
        nocate_data[tag] = []


print(f"Tags with no categories: {len(nocate)}")
print(f"Tags with categories: {len(cated)}")


samples = list(set(long_tags + random_tags))
tag_samples = {}
for tag in samples:
    tag_samples[tag] = data[tag]

print(safe_dump(tag_samples))


def get_text(system, text):
    key = f"get_text: system={system} , text={text}"
    cached = load_memory(key)
    if cached is not None:
        return cached
    
    key2 = f"get_text response: {system} {text}"
    response = load_memory(key2)
    if not response:
        response = co.chat(
            preamble=str(system),
            message=str(text),
            model="command-r-plus"
        ).text
        save_memory(key2, response)
    
    save_memory(key, response)
    return response

def split_dict(data, chunk_size):
    items = list(data.items())
    chunks = [dict(items[i:i + chunk_size]) for i in range(0, len(items), chunk_size)]
    return chunks

result = split_dict(nocate_data, 50)

system_prompt = f"""
## Task
Adds category information to tags expressed as English words.
Output in YAML format.

## Output sample (YAML)
```yaml
{safe_dump(tag_samples)}
```
""".strip()


for i, chunk in enumerate(result):
    print(f"Chunk {i+1}")

    result = get_text(system_prompt, safe_dump(chunk))
    result_data = YamlUtils.yaml_format(result)
    print(result_data)

    data.update(result_data)
    json.dump(data, open('tag_category2.json', 'w', encoding='utf-8'))

sys.exit()

headers = []
samples = []
data = []


# Open the CSV file
with open('wd-v1-4-moat-tagger-v2_.csv', 'r') as file:
    # Create a CSV reader object
    reader = csv.reader(file)

    # Iterate over each row in the CSV file
    for row in reader:
        if not headers:
            headers = row
            continue
        if row[4]:
            samples.append({"tag":row[1], "categories":[row[4], row[5], row[6], row[7]]})
        else:
            data.append({"tag":row[1], "categories":[row[4], row[5], row[6], row[7]]})



def work(input_data):
    system = """
## Task & Context
You can classify what English words represent as tags.

## Style Guide
You will output data in JSON format with absolutely no errors. Please do not respond with your own thoughts or opinions.
"""

    sample_format = ",\n".join([json.dumps(sample) for sample in samples])
    input_format = ",\n".join([json.dumps(sample) for sample in input_data])

    message = f"""
The JSON data below is tag information used for image analysis. A tag requires information on multiple categories to which the tag belongs.

Please follow the sample and set up to 4 category information for the tag.

## Sample data
```json
[
{sample_format}
]
```

## Tag data that requires category addition
```json
[
{input_format}
]
```
"""

    #print(system)
    #print(message)
    result = get_text(system, message)
    #print(result)

    return json_format(result)

def json_format(text:str) -> dict:
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError:
        pass
    
    try:
        return eval(text)
    except (Exception, SyntaxError):
        pass

    try:
        if not text.startswith("[") and not text.startswith("{") and not text.startswith("\""):
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
                return json_format(text)
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
                return json_format(text)
    except Exception:
        pass

    try:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if not line.startswith("\"") and line.endswith("\""):
                lines[i] = f"\"{line}"
            elif not line.startswith("\"") and line.endswith("\","):
                lines[i] = f"\"{line}"
            if line.startswith("\"") and not (line.endswith("\"") or line.endswith("\",")):
                line_temp = line.strip().strip("\"")
                if '\"' not in line_temp:
                    lines[i] = f"\"{line_temp}\","
            if line.startswith("「") and line.endswith("」,"):
                lines[i] = line.replace("「", "\"").replace("」", "\"").replace("：", ":")
            
        return json_format("\n".join(lines))
    except Exception:
        pass

    print (f"Failed to parse JSON format: {text}")
    raise ValueError("Failed to parse JSON format")

# Split the data into chunks of 100
chunks = [data[i:i+50] for i in range(0, len(data), 50)]

tag_category = []

error_chunks = load_memory("error_chunks", [])

error_data_list = []

# Process each chunk
for chunk in chunks:
    try:
        if str(chunk) in error_chunks:
            raise cohere.core.api_error.ApiError()

        result_data = work(chunk)
        tag_category.extend(result_data)
    except cohere.core.api_error.ApiError:
        if str(chunk) not in error_chunks:
            error_chunks.append(str(chunk))

        print("Failed to process chunk")
        chunks2 = [chunk[i:i+5] for i in range(0, len(chunk), 5)]
        for chunk2 in chunks2:
            try:
                if str(chunk2) in error_chunks:
                    raise cohere.core.api_error.ApiError()
                result_data = work(chunk2)
                tag_category.extend(result_data)
            except cohere.core.api_error.ApiError:
                if str(chunk2) not in error_chunks:
                    error_chunks.append(str(chunk2))
                print("Failed to process chunk")
                
                for chunk3 in chunk2:
                    try:
                        if str(chunk3) in error_chunks:
                            raise cohere.core.api_error.ApiError()
                        result_data = work([chunk3])
                        tag_category.extend(result_data)
                    except cohere.core.api_error.ApiError:
                        print("Failed to process chunk")
                        error_chunks.append(str(chunk3))
                        error_data_list.append(chunk3)

save_memory("error_chunks", error_chunks)

print(tag_category)

print(error_data_list)


final_format = {}
for item in samples:
    final_format[item["tag"]] = [category.replace(" ","_") for category in item["categories"] if category]

for item in tag_category:
    final_format[item["tag"]] = [category.replace(" ","_") for category in item["categories"] if category]

for item in error_data_list:
    final_format[item["tag"]] = []

print(final_format)

with open('tag_category.json', 'w') as file:
    json.dump(final_format, file)
