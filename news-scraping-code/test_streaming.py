#!/usr/bin/env python3
import requests
import json

def test_streaming():
    url = "http://localhost:8003/ask"
    headers = {"Content-Type": "application/json"}
    data = {"query": "what is AI"}

    print("Testing streaming response...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data)}")
    print("-" * 50)

    try:
        with requests.post(url, json=data, stream=True) as response:
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            print("-" * 50)

            if response.status_code == 200:
                chunk_count = 0
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            chunk_count += 1
                            data_content = line_str[6:]  # Remove 'data: '
                            try:
                                parsed = json.loads(data_content)
                                if 'chunk' in parsed:
                                    print(f"Chunk {chunk_count}: {parsed['chunk']}", end='', flush=True)
                                elif 'error' in parsed:
                                    print(f"Error: {parsed['error']}")
                                    break
                                elif data_content == '[DONE]':
                                    print(f"\n[DONE] - Total chunks: {chunk_count}")
                                    break
                            except json.JSONDecodeError:
                                print(f"Raw: {line_str}")

                        if chunk_count >= 5:  # Limit output
                            print("\n... (stopping after 5 chunks)")
                            break
            else:
                print(f"Error: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_streaming()