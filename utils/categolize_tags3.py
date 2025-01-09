import os
import sys
import asyncio
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# pip install -U litellm
# pip install -U git+https://github.com/sugarkwork/chat_assistant.git
from pmem.async_pmem import PersistentMemory
from chat_assistant import ChatAssistant, ModelManager

from json_repair import loads

from dotenv import load_dotenv
load_dotenv()
#.env file:
#DEEPSEEK_API_KEY="...api_key..."
#COHERE_API_KEY="...api_key..."


cache = PersistentMemory(".tmp.db")

# Global semaphore for concurrent processing
concurrency_semaphore = asyncio.Semaphore(4)


async def read_csv(csv_file):
    if not os.path.exists(csv_file):
        csv_file = os.path.join(os.path.dirname(__file__), csv_file)

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


async def categorize_tags(ai:ChatAssistant, tags:list, samples:list) -> list:
    try:
        tag_text = "```text\n"
        for tag in tags:
            tag_text += tag + "\n"
        tag_text += "```\n"
        
        sample_text = "```jsonl\n"
        for sample in samples:
            sample_text += str(sample) + "\n"
        sample_text += "```\n"

        system_prompt = f"""
# Order
Please think of a tag category.
Please do not output your impressions or comments, only the final jsonl result.

# Sample (jsonl)
{sample_text}
"""
    
        message_prompt = f"""# Tags
{tag_text}
"""
        result = await ai.chat(system=system_prompt, message=message_prompt)
        
        if '```jsonl' in result:
            result = result.split('```jsonl')[1].strip()
        
        if '```' in result:
            result = result.split('```')[0].strip()
        
        result = result.split('\n')
        result = [loads(row) for row in result if row]
        
        return result
    finally:
        pass


def clean_data(data):
    clean_data = []
    for row in data:
        new_row = {}
        new_row['name'] = row['name']
        for n in range(1, 8):
            if f'category{n}' in row and row[f'category{n}']:
                new_row[f'category{n}'] = row[f'category{n}']
        clean_data.append(new_row)
    
    return clean_data


async def process_batch(num, ai, batch, sample_data) -> list:
    async with concurrency_semaphore:
        print(f"Processing {len(batch)} tags in batch {num}")
        return await categorize_tags(ai, batch, sample_data)

async def main():
    models=[
        'deepseek/deepseek-chat', 
        #'cohere/command-r-plus-08-2024', 
        #'cohere/command-r-plus',
        #'cohere/command-r-08-2024'
        ]
    
    ai = ChatAssistant(
        model_manager=ModelManager(models=models),
        memory=cache
        )

    result = await ai.chat(message='Hello, what your name?')
    print(result)

    csv_file = 'wd-eva02-large-tagger-v3.csv'
    data = await read_csv(csv_file)
    names = set([row['name'] for row in data])

    sample_csv_file = 'samples.csv'
    sample_data = clean_data(await read_csv(sample_csv_file))
    sample_names = set([row['name'] for row in sample_data])

    cached_tag_names = await cache.load('cached_tags', [])
    print("cached_tag_names: ", cached_tag_names)
    data = names - sample_names
    data = data - set(cached_tag_names)
    data = list(data)
    sorted(data)

    # Split data into chunks of 50
    batch_size = 30
    batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]

    total_batches = len(batches)
    batch_tasks = []

    result_data = {}
    for cached_tag in cached_tag_names:
        result_data[cached_tag] = await cache.load(cached_tag)

    for i, batch in enumerate(batches):
        print(f"Preparing batch {i+1}/{total_batches} ({len(batch)} tags)")
        key = f"tag_categorize : {batch}"
        
        async def process_and_save_batch(num, batch, key, sample_data, result_data):
            result = await cache.load(key)
            if not result:
                result = await process_batch(num, ai, batch, sample_data)
                await cache.save(key, result)
            
            for row in result:
                result_data[row['name']] = []
                for n in range(1, 8):
                    if f'category{n}' in row:
                        result_data[row['name']].append(row[f'category{n}'])
                rkey = row['name']
                await cache.save(rkey, result_data[row['name']])

                cached_tags = await cache.load('cached_tags', [])
                cached_tags.append(rkey)
                await cache.save('cached_tags', cached_tags)
            
            return result

        batch_task = asyncio.create_task(process_and_save_batch(i, batch, key, sample_data, result_data))
        batch_tasks.append(batch_task)

    # Wait for all batch tasks to complete
    results = await asyncio.gather(*batch_tasks)

    import json

    # add sample data to result
    for row in sample_data:
        result_data[row['name']] = []
        for n in range(1, 8):
            if f'category{n}' in row:
                result_data[row['name']].append(row[f'category{n}'])

    # Load old tag data
    with open('tag_category.json', 'r') as f:
        old_tag_data = loads(f.read())
        for key, val in old_tag_data.items():
            if key not in result_data:
                result_data[key] = val
                continue
            
            if not result_data[key]:
                result_data[key] = val
                continue

            for v in val:
                if v not in result_data[key]:
                    result_data[key].append(v)
    
    # Clean up the data
    for key in result_data.keys():
        new_items = []
        for item in result_data[key]:
            item = item.strip().lower().replace(' ', '_')
            if item not in new_items:
                new_items.append(item)
        
        result_data[key] = new_items

    # Save the result
    with open(os.path.join(os.path.dirname(__file__), 'result.json'), 'w', encoding='utf8') as f:
        firstline = True
        f.write('{\n')
        for key,val in result_data.items():
            if firstline:
                firstline = False
            else:
                f.write(',\n')
            f.write(f'"{key}": {json.dumps(val)}')
        f.write('\n}')
        

    print("Done")

    await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
