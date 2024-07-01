import requests

def get_current_ip_and_location():
    try:
        ip_response = requests.get('https://httpbin.org/ip')
        ip_address = ip_response.json()['origin']
        
        location_response = requests.get(f'http://ipinfo.io/{ip_address}/json')
        location_data = location_response.json()
        
        country = location_data.get('country', 'Unknown')
        city = location_data.get('city', 'Unknown')
        
        return ip_address, country, city
    except requests.RequestException as e:
        print(f'Could not determine IP address or its location: {e}')
        return None, None, None

def read_blocked_phrases(blocked_phrases_file):
    blocked_phrases = {'english': [], 'russian': [], 'ukrainian': [], 'spanish': []}
    current_language = None
    with open(blocked_phrases_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                if 'English' in line:
                    current_language = 'english'
                elif 'Russian' in line:
                    current_language = 'russian'
                elif 'Ukrainian' in line:
                    current_language = 'ukrainian'
                elif 'Spanish' in line:
                    current_language = 'spanish'
            elif current_language and line:
                blocked_phrases[current_language].append(line)
    return blocked_phrases

def check_sites(domains_file, results_file, blocked_phrases_file):
    blocked_phrases = read_blocked_phrases(blocked_phrases_file)

    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f.readlines()]

    with open(results_file, 'w') as f:
        f.write(f'IP: {ip_address}, Country: {country}, City: {city}\n')
        for domain in domains:
            try:
                response = requests.get(f'http://{domain}', timeout=5)
                
                if any(phrase in response.text for phrases in blocked_phrases.values() for phrase in phrases):
                    status = 'blocked'
                else:
                    status = 'good'
            except requests.RequestException as e:
                status = f'error {e.response.status_code if e.response else "no answer"}'
            
            f.write(f'{status}\n')
            print(f'{domain}: {status}')

domains_file = 'domains.txt'
results_file = 'results.txt'
blocked_phrases_file = 'blocked_phrases.txt'

ip_address, country, city = get_current_ip_and_location()
if ip_address and country and city:
    print(f'IP address in use: {ip_address}')
    print(f'Country: {country}, City: {city}')
else:
    print('Could not retrieve information about the current IP address and its location.')

check_sites(domains_file, results_file, blocked_phrases_file)
