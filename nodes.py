
class TagFilter:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {            
            "required": {                
                "tags": ("STRING",),                
                },            
                }

    RETURN_TYPES = ("STRING")
    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tags):
        tags = [tag.strip() for tag in tags.split(",")]
        tags2 = [tag.replace("_", " ") for tag in tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2.endswith("by self"):
                result.append(tags[i])

        return {"result": (result,)}

NODE_CLASS_MAPPINGS = {
    "TagFilter": TagFilter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TagFilter": "TagFilter Node"
}
