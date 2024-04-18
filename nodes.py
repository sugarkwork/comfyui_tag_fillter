import os
import json

tag_category = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category.json")))

class TagFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default": ""}),
                "pose": ("BOOLEAN", {"default": True}),
                "gesture": ("BOOLEAN", {"default": True}),
                "action": ("BOOLEAN", {"default": True}),
                "emotion": ("BOOLEAN", {"default": True}),
                "expression": ("BOOLEAN", {"default": True}),
                "color": ("BOOLEAN", {"default": True}),
                "sensitive": ("BOOLEAN", {"default": True}),
                "liquid": ("BOOLEAN", {"default": True}),
                "include_categories": ("STRING", {"default": ""}),
                "exclude_categories": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags, pose=True, gesture=True, action=True, emotion=True, expression=True, color=True, sensitive=True, liquid=True, include_categories="", exclude_categories=""):
        tags = [tag.strip() for tag in tags.split(",")]
        tags2 = [tag.replace("_", " ").lower() for tag in tags]
        targets = []
        if pose:
            targets.append("pose")
        if gesture:
            targets.append("gesture")
        if action:
            targets.append("action")
        if emotion:
            targets.append("emotion")
        if expression:
            targets.append("expression")
        if color:
            targets.append("color")
        if sensitive:
            targets.append("sensitive")
        if liquid:
            targets.append("liquid")
        if include_categories:
            targets += [category.strip() for category in include_categories.replace("\n",",").split(",")]
        if exclude_categories:
            targets = [target for target in targets if target not in [category.strip() for category in exclude_categories.replace("\n",",").split(",")]]
        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 in tag_category:
                category_list = tag_category[tag2]
                for target in targets:
                    if target in category_list and tags[i] not in result:
                        result.append(tags[i])
        return (", ".join(result),)

NODE_CLASS_MAPPINGS = {
    "TagFilter": TagFilter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TagFilter": "TagFilter"
}