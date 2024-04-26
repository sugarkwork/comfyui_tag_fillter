import os
import json


tag_category = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category.json")))


class TagRemover:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "exclude_tags": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags:str, exclude_tags:str=""):
        tags = [tag.strip() for tag in tags.replace("\n",",").split(",")]
        tags2 = [tag.replace(" ", "_").lower().strip() for tag in tags]

        exclude_tags = [tag.strip() for tag in exclude_tags.replace("\n",",").split(",")]
        exclude_tags2 = [tag.replace(" ", "_").lower().strip() for tag in exclude_tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 not in exclude_tags2:
                result.append(tags[i])
        
        return (", ".join(result),)


class TagFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "pose": ("BOOLEAN", {"default": True}),
                "gesture": ("BOOLEAN", {"default": True}),
                "action": ("BOOLEAN", {"default": True}),
                "emotion": ("BOOLEAN", {"default": True}),
                "expression": ("BOOLEAN", {"default": True}),
                "camera": ("BOOLEAN", {"default": True}),
                "angle": ("BOOLEAN", {"default": True}),
                "sensitive": ("BOOLEAN", {"default": True}),
                "liquid": ("BOOLEAN", {"default": True}),
                "include_categories": ("STRING", {"default": ""}),
                "exclude_categories": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags, pose=True, gesture=True, action=True, emotion=True, expression=True, camera=True, angle=True, sensitive=True, liquid=True, include_categories="", exclude_categories=""):

        targets = []
        exclude_targets = []
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
        if camera:
            targets.append("camera")
        if angle:
            targets.append("angle")
        if sensitive:
            targets.append("sensitive")
        if liquid:
            targets.append("liquid")
        if include_categories:
            targets += [category.strip() for category in include_categories.replace("\n",",").split(",")]
        if exclude_categories:
            exclude_targets = [category.strip() for category in exclude_categories.replace("\n",",").split(",")]
            targets = [target for target in targets if target not in exclude_targets]
        
        print("targets", targets)

        tags = [tag.strip() for tag in tags.split(",")]
        tags2 = [tag.replace(" ", "_").lower() for tag in tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 in tag_category:
                category_list = tag_category.get(tag2, [])

                for category in category_list:
                    if category in exclude_targets:
                        break
                else:
                    for category in category_list:
                        if category in targets and tags[i] not in result:
                            result.append(tags[i])
                            break

        return (", ".join(result),)

NODE_CLASS_MAPPINGS = {
    "TagFilter": TagFilter,
    "TagRemover": TagRemover,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TagFilter": "TagFilter",
    "TagRemover": "TagRemover"
}
