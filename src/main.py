from copystatic import *

from mdnode import *

from htmlnode import *

from textnode import *

import os

import sys


def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.strip().startswith("# "):
            lines = block.strip().split("\n")
            return lines[0].strip("# ")
    raise Exception("No Title")

def generate_page(source_path, template_path, destination_path, basepath):
    print(f"Generating page from {source_path} to {destination_path} using {template_path}")
    with open(source_path, "r") as f:
        markdown = f.read()
    with open(template_path, "r") as f:
        template_string = f.read()
    html_node = markdown_to_html_node(markdown)
    html = html_node.to_html()
    title = extract_title(markdown)
    page = template_string.replace("{{ Title }}", title)
    page = page.replace("{{ Content }}", html)
    page = page.replace(f'href="/', f'href="{basepath}')
    page = page.replace(f'src="/', f'src="{basepath}')
    dirpath = os.path.dirname(destination_path)
    if dirpath != "":
        os.makedirs(dirpath, exist_ok=True)
    
    with open(destination_path, "w") as f:
        f.write(page)

def generate_pages_recusive(source_path, template_path, destination_path, basepath):
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(".md"):
                source_file = os.path.join(root, file)
                
                destination_file = os.path.join(root.replace(source_path, destination_path), file.replace("md", "html"))
                
                generate_page(source_file, template_path, destination_file, basepath)










def main():
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"

    template_path = "./template.html"

    print(f"Deleting docs directory...")
    clean_destination("./docs")

    print(f"Copying static files to docs directory...")
    repeat_copy("static", "docs")

    generate_pages_recusive("content", template_path, "docs", basepath)

if __name__ == "__main__":
    main()
