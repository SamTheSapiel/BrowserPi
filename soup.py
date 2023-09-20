import requests
from bs4 import BeautifulSoup
import sys
import re

def get_bullet_points_from_url(url, tag):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Use regular expression to match the tag, regardless of surrounding whitespace
    h2_tag = soup.find('h2', string=re.compile(r'^\s*{}\s*$'.format(re.escape(tag)), re.IGNORECASE))
    if not h2_tag:
        return []

    # Find the parent div of the current parent of the h2 tag
    parent_div = h2_tag.find_parent().find_parent()

    ul = parent_div.find('ul')
    if not ul:
        return []

    # Get the text content of each list item
    bullet_points = [li.text.strip() for li in ul.find_all('li')]

    return bullet_points

def write_bullet_points_to_file(bullet_points, filename):
    with open(filename, 'w') as file:
        for point in bullet_points:
            file.write(point + '\n')  # Write each bullet point followed by a newline

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("[!] Error, two arguments are needed! \n[*] Usage: python3 soup.py '#link' 'Raspi#number' ")
        sys.exit(1)

    bullet_points = get_bullet_points_from_url(sys.argv[1], sys.argv[2])

    if bullet_points:
        write_bullet_points_to_file(bullet_points, 'links.txt')
        print(f"[*] Bullet Points were saved in 'links.txt'!")
        sys.exit(0)
    else:
        print("[!] No Bullet Points found.")
        sys.exit(1)

