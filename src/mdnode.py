import re

from enum import Enum

from textnode import *

from htmlnode import *

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(md_block):
    lines = md_block.split("\n")
    
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    count = 0
    for ch in md_block:
        if ch == "#":
            count += 1
        else:
            break
    if 0 < count <= 6 and len(md_block) > count and md_block[count] == " ":
        return BlockType.HEADING

    
    if md_block.startswith("```") and md_block.endswith("```"):
        return BlockType.CODE
    
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    is_ordered = True
    for i, line in enumerate(lines, start=1):
        if ". " not in line:
            is_ordered = False
            break
        num_str, _ = line.split(". ", 1)
        if not num_str.isdigit() or int(num_str) != i:
            is_ordered = False
            break

    if is_ordered and len(lines) > 1:
        return BlockType.ORDERED_LIST

    
    return BlockType.PARAGRAPH


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        count = old_node.text.count(delimiter)
        if count == 0:
            new_nodes.append(old_node)
            continue

        text_list = old_node.text.split(delimiter)

        if len(text_list) % 2 == 0:
            raise Exception("That's invalid markdown text!")

        for i, part in enumerate(text_list):
            if part == "":
                continue

            if i % 2 == 0:
                new_node = TextNode(part, TextType.TEXT)
            else:
                new_node = TextNode(part, text_type)

            new_nodes.append(new_node)

    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        links = extract_markdown_links(original_text)

        if not links:
            new_nodes.append(old_node)
            continue

        for label, href in links:
            sections = original_text.split(f"[{label}]({href})", 1)
            if len(sections) != 2:
                raise Exception("invalid markdown, link section not closed")

            before, after = sections

            if before != "":
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(label, TextType.LINK, href))

            original_text = after

        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        
        if len(images) == 0:
            new_nodes.append(old_node)
            continue

        for alt, src in images:
            sections = original_text.split(f"![{alt}]({src})", 1)
            if len(sections) != 2:
                raise Exception("invalid markdown, image section not closed")

            before, after = sections

            if before != "":
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(alt, TextType.IMAGE, src))

            original_text = after

        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    
    return new_nodes
            
def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    nodes = [node]
    delimiter_tuples = [
        ("**",TextType.BOLD),
        ("_",TextType.ITALIC),
        ("`",TextType.CODE),
        ]
    
    for item in delimiter_tuples:
        nodes = split_nodes_delimiter(nodes, item[0], item[1])

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    new_blocks = []
    for item in blocks:
        item = item.strip()
        if item != "":
            new_blocks.append(item)
    return new_blocks

def text_to_children(text):
    textnodes = text_to_textnodes(text)
    htmlnodes = []
    for textnode in textnodes:
        htmlnodes.append(text_node_to_html_node(textnode))
    return htmlnodes

def paragraph_to_html_node(block):
    block = block.replace("\n", " ")
    return ParentNode("p",text_to_children(block))
    
def heading_to_hmtl_node(block):
    count = 0
    for ch in block:
        if ch == "#":
            count += 1
        else:
            break
    block = block[count:].strip()
    return ParentNode(f"h{count}", text_to_children(block))

def code_to_html_node(block):
    block = block[3:-3].lstrip('\n')
    code_node = text_node_to_html_node(TextNode(block, TextType.CODE))
    return ParentNode("pre", [code_node])

def quote_to_html_node(block):
    lines = block.split("\n")
    clean_lines = []
    for line in lines:
        clean_lines.append(line[1:].strip())
    block = " ".join(clean_lines)
    return ParentNode("blockquote", text_to_children(block))

def unorderedlist_to_html_node(block):
    lines = block.split("\n")
    list_item_html_nodes = []
    for line in lines:
        if not line.strip():
            continue
        # assume "- " at the start
        if not line.startswith("- "):
            continue
        content = line[2:].strip()
        children = text_to_children(content)
        list_item_html_nodes.append(ParentNode("li", children))
    return ParentNode("ul", list_item_html_nodes)

def ordered_list_to_html_node(block):
    lines = block.split("\n")
    list_item_html_nodes = []
    for line in lines:
        line = line[line.index(".")+1:].strip()
        line_element_children = text_to_children(line)
        line_node = ParentNode("li", line_element_children)
        list_item_html_nodes.append(line_node)
    return ParentNode("ol", list_item_html_nodes)


def markdown_to_html_node(markdown):
    block_list = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.PARAGRAPH:
                block_list.append(paragraph_to_html_node(block))
            case BlockType.HEADING:
                block_list.append(heading_to_hmtl_node(block))
            case BlockType.CODE:
                block_list.append(code_to_html_node(block))
            case BlockType.QUOTE:
                block_list.append(quote_to_html_node(block))
            case BlockType.UNORDERED_LIST:
                
                block_list.append(unorderedlist_to_html_node(block))
            case BlockType.ORDERED_LIST:
                block_list.append(ordered_list_to_html_node(block))
    final_node = ParentNode("div", block_list)
    return final_node

    return final_node



