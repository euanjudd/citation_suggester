import requests
from django.shortcuts import render
from django.http import JsonResponse
import replicate
import json
from dotenv import load_dotenv

load_dotenv()  # This loads the environment variables from .env

def home(request):
    return render(request, 'index.html')

def fetch_sorted_data(query, rows=100, max_tries=10):
    entries = []
    offset = 0
    tries = 0

    while len(entries) < rows and tries < max_tries:
        params = {
            'query': query,
            'filter': 'type:journal-article',
            'filter': 'has-title:true',
            'filter': 'has-abstract:true',
            'rows': 20,
            'offset': offset
        }
        response = requests.get("https://api.crossref.org/works", params=params)
        if response.status_code == 200:
            data = response.json()
            entries.extend(data['message']['items'])
            offset += 20  # Increase offset to fetch the next batch of results
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break  # Exit loop if there's an HTTP error
        
        tries += 1

    return entries[:rows]  # Return only the first 10 entries

def format_entry(entry):
    """Format entry for display."""
    return {
        'title': " ".join(entry.get('title', ['No title available'])),
        'DOI': entry.get('DOI', 'No DOI available'),
        'abstract': entry.get('abstract', 'No abstract available'),
        'date': "-".join(map(str, entry['issued']['date-parts'][0])) if 'issued' in entry else 'No date available',
        'authors': ", ".join([f"{a.get('given', '')} {a.get('family', '')}" for a in entry.get('author', [])])
    }

def call_model(request):
    if request.method == 'POST':
        # my_prompt = request.POST.get('input')
        data = json.loads(request.body.decode('utf-8'))  # Decode and load JSON data
        my_prompt = data.get('input')
        
        if not my_prompt:
            return JsonResponse({'error': 'No input provided'}, status=400)

        my_system_prompt = """
            Given the full_text and a specific input_text, perform the following steps:
            1. **Extract Key Topics**:
            - Identify the primary subjects or technologies discussed in the input text. Focus on broad but relevant terms that are likely to be used in academic literature.
            2. **Identify Contextual Keywords**:
            - Determine additional terms that provide context or are closely related to the main topics. These should include specific technologies, problems, or methodologies mentioned in the text.
            3. **Determine the Type of Information Desired**:
            - Analyze the text to understand what kind of information is being sought (e.g., methodologies, applications, theoretical frameworks, case studies).
            Using the information gathered above, output a Google Scholar search query using only the most relevant keywords and logical operators. The query should be formatted as follows:
            "[Key Topics] AND [Contextual Keywords] AND ([Type of Information Desired])"
            Ensure that the query is balanced between specificity and breadth to maximize the chance of retrieving relevant academic papers.
            IMPORTANT: Only output the query formatted as above, do not write any additional details.
        """

        inputs ={
            "top_k": 0,
            "top_p": 0.99,
            "prompt": my_prompt,
            "max_tokens": 32,
            "temperature": 0.4,
            "system_prompt": my_system_prompt,
            "length_penalty": 1,
            "stop_sequences": "<|end_of_text|>,<|eot_id|>",
            "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "presence_penalty": 0,
            "log_performance_metrics": False
        }
        
        outputs = []
        for event in replicate.stream(
            "meta/meta-llama-3-8b-instruct",
            input=inputs,
        ):
            outputs.append(str(event))

        full_text = ''.join(outputs)
        cleaned_text = full_text.replace('"', '').replace("\\", "").strip()

    #     return JsonResponse({'data': cleaned_text})

    # else:
    #     return JsonResponse({'error': 'Invalid method'}, status=400)

        # Fetch and sort CrossRef data
        entries = fetch_sorted_data(cleaned_text)
        sorted_by_citations = sorted(entries, key=lambda x: x.get('is-referenced-by-count', 0), reverse=True)
        sorted_by_date = sorted(entries, key=lambda x: x['issued']['date-parts'][0], reverse=True)

        # Prepare results for JSON response
        results = {
            'by_relevance': [format_entry(e) for e in entries[:10]],
            'by_citations': [format_entry(e) for e in sorted_by_citations[:10]],
            'by_date': [format_entry(e) for e in sorted_by_date[:10]]
        }
        return JsonResponse(results)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)