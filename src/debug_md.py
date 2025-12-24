from mdnode import markdown_to_html_node

md = "## Blog posts\n\n- [Why Glorfindel is More Impressive than Legolas](/blog/glorfindel)"

print("RAW MD:", md)
html_node = markdown_to_html_node(md)
print("\nHTML:")
print(html_node.to_html())