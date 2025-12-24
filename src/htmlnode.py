class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def __eq__(self, other):
        if (self.tag == other.tag 
            and self.value == other.value 
            and self.children == other.children
            and self.props == other.props
            ):
                return True
                
        return False

    def __repr__(self):
            return(f"{self.tag}, {self.value}, {self.children}, {self.props}")

    def to_html(self):
            raise NotImplementedError

    def props_to_html(self):
        if self.props == None or len(self.props) == 0:
            return ""
            
        total = ""
        for key, value in self.props.items():
            string = f' {key}="{value}"'
            total += string
        return total


class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value == None:
            raise ValueError("Leaf Node has no value")
        
        elif self.tag == None:
            return self.value

        elif self.props == None or len(self.props) == 0:
                return f"<{self.tag}>{self.value}</{self.tag}>"
        else:
            return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
        
class ParentNode(HTMLNode):

    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)


    def to_html(self):
        if self.tag == None:
            raise ValueError("Node has no tag!")
        
        if self.children == None:
            raise ValueError("Node has no children!")

        children_html = "".join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"



        children_string = ""
        for item in self.children:
            children_string += item.to_html()
        return f"<{self.tag}{self.props_to_html()}>{children_string}</{self.tag}>"                

        

    