import os
import json


tag_category1 = [] 
tag_category2 = []


def get_tag_category(version=1):
    global tag_category1, tag_category2
    if version == 1:
        if not tag_category1:
            tag_category1 = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category.json")))
        return tag_category1
    else:
        if not tag_category2:
            tag_category2 = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category_v2.json")))
        return tag_category2
    

class TagData:
    def __init__(self, tag, weight):
        self.tag = tag
        self.weight = weight
        self.format = tag.lower().strip().replace(' ', '_')
    
    def __str__(self):
        return self.format
    
    def __repr__(self):
        return self.format

    def __eq__(self, other):
        if isinstance(other, TagData):
            return self.format == other.format
        return False

    def __hash__(self):
        return hash(self.format)
    
    def text(self, format=False, underscore=False):
        tag_text = self.tag
        if format:
            tag_text = self.format
        if underscore:
            tag_text = tag_text.replace(' ', '_')
        
        if self.weight != 1.0:
            return f"({tag_text}:{self.weight})"
        return tag_text


def parse_tags(tag_string) -> list:
    def clean_tag(tag):
        # Remove any leading/trailing whitespace and parentheses
        tag = tag.strip()
        while tag.startswith(('(', ')')) or tag.endswith(('(', ')')):
            tag = tag.strip('()')
        return tag.strip()

    def get_weight_and_tags(group):
        group = clean_tag(group)
        if ':' in group:
            tags_part, weight_part = group.split(':', 1)
            try:
                weight = float(weight_part)
            except ValueError:
                weight = 1.0
            tags = [t.strip() for t in tags_part.split(',')]
        else:
            tags = [t.strip() for t in group.split(',')]
            weight = 1.0
        return tags, weight

    result = []
    paren_count = 0
    
    # First pass: split into proper groups
    groups = []
    current = ''
    for char in tag_string:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        
        current += char
        
        if paren_count == 0 and char == ',':
            if current.strip(',').strip():
                groups.append(current.strip(',').strip())
            current = ''
    if current.strip(',').strip():
        groups.append(current.strip(',').strip())

    # Second pass: process each group
    for group in groups:
        group = group.strip()
        if not group:
            continue

        # Count the number of opening parentheses at the start
        opening_count = 0
        for char in group:
            if char == '(':
                opening_count += 1
            else:
                break

        # Count the number of closing parentheses at the end
        closing_count = 0
        for char in reversed(group):
            if char == ')':
                closing_count += 1
            else:
                break

        # Get the actual parentheses pairs count (use the minimum to ensure matching pairs)
        paren_pairs = min(opening_count, closing_count)

        tags, custom_weight = get_weight_and_tags(group)
        
        # Set weight based on parentheses pairs
        if custom_weight != 1.0:
            weight = custom_weight
        else:
            if paren_pairs == 0:
                weight = 1.0
            else:
                weight = 1.0 + (paren_pairs * 0.1)

        # Add each tag with its weight
        for tag in tags:
            tag = clean_tag(tag)
            if tag:
                result.append(TagData(tag, weight))
    
    return result


def remove_duplicates(lst):
    return list(dict.fromkeys(lst))


def tagdata_to_string(tags:list[TagData], underscore=False) -> str:
    return ", ".join([tag.text(underscore=underscore) for tag in tags])


class TagIf:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "find": ("STRING", {"default": ""}),
                "output1": ("STRING", {"default": ""}),
            },
            "optional": {
                "output2": ("STRING", {"default": ""}),
                "output3": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING","STRING","STRING",)
    RETURN_NAMES = ("output1","output2","output3",)

    FUNCTION = "tag"

    CATEGORY = "string"

    OUTPUT_NODE = True

    def tag(self, tags:str, find:str, output1:str, output2:str=None, output3:str=None):
        tags = parse_tags(tags)
        find = parse_tags(find)
        if all(tag in tags for tag in find):
            return (output1, output2, output3)
        else:
            return ("", "", "")



class TagSwitcher:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_tags": ("STRING",),
                "default_image": ("IMAGE",),
                "tags1": ("STRING", {"default": ""}),
                "image1": ("IMAGE", {"default": ""}),
                "any1": ("BOOLEAN", {"default": True}),
            },
            "optional": {   
                "tags2": ("STRING", {"default": ""}),
                "image2": ("IMAGE", {"default": ""}),
                "any2": ("BOOLEAN", {"default": True}),
                "tags3": ("STRING", {"default": ""}),
                "image3": ("IMAGE", {"default": ""}),
                "any3": ("BOOLEAN", {"default": True}),
                "tags4": ("STRING", {"default": ""}),
                "image4": ("IMAGE", {"default": ""}),
                "any4": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "tag"

    CATEGORY = "image"

    OUTPUT_NODE = True

    def tag(self, input_tags="", default_image=None, tags1="", image1=None, any1=True, tags2="", image2=None, any2=True, tags3="", image3=None, any3=True, tags4="", image4=None, any4=True):
        input_tags = parse_tags(input_tags)

        target_tags = []
        tags1 = set(parse_tags(tags1))
        target_tags.append((tags1, image1, any1))

        tags2 = set(parse_tags(tags2))
        target_tags.append((tags2, image2, any2))

        tags3 = set(parse_tags(tags3))
        target_tags.append((tags3, image3, any3))

        tags4 = set(parse_tags(tags4))
        target_tags.append((tags4, image4, any4))

        for tags, image, any_flag in target_tags:
            if any_flag:
                if any(tag in tags for tag in input_tags):
                    return (image,)
            else:
                if all(tag in input_tags for tag in tags):
                    return (image,)

        return (default_image,)


class TagMerger:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags1": ("STRING",),
                "tags2": ("STRING",),
                "under_score": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags1:str, tags2:str, under_score=True):
        taglist1 = parse_tags(tags1)
        taglist2 = parse_tags(tags2)

        tags = remove_duplicates(taglist1 + taglist2)

        return (tagdata_to_string(tags, underscore=under_score),)


class TagRemover:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING",),
                "exclude_tags": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags:str, exclude_tags:str=""):
        tag_data = parse_tags(tags)
        exclude_tag_data = parse_tags(exclude_tags)

        uniq_tags = [tag for tag in tag_data if tag not in exclude_tag_data]
        
        return (tagdata_to_string(uniq_tags) ,)


class TagReplace:
    # TODO: use TagData class

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "replace_tags": ("STRING", {"default": ""}),
                "match": ("FLOAT", {"default": 0.3}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def _get_categories(self, tag: str) -> set:
        """タグのカテゴリーを取得する"""
        tag_category = get_tag_category(2)
        return set(tag_category.get(tag, []))

    def _category_match_percentage(self, categories1: set, categories2: set) -> float:
        """2つのカテゴリセット間の一致度(%)を計算する"""
        if not categories1 or not categories2:
            return 0
        intersection = categories1.intersection(categories2)
        union = categories1.union(categories2)
        return len(intersection) / len(union)

    def tag(self, tags:str, replace_tags:str="", match:float=0.3):
        tags = [tag.strip() for tag in tags.replace("\n",",").split(",")]
        tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in tags]

        replace_tags = [tag.strip() for tag in replace_tags.replace("\n",",").split(",")]
        replace_tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in replace_tags]
        replace_tags_used = {tag:False for tag in replace_tags_normalized}

        result = []
        for i, tag in enumerate(tags_normalized):
            tag_categories = self._get_categories(tag)
            best_match_tag = None
            best_match_tag_id = None
            best_match_percentage = 0

            for k, replace_tag in enumerate(replace_tags_normalized):
                replace_categories = self._get_categories(replace_tag)
                match_percentage = self._category_match_percentage(tag_categories, replace_categories)

                if match_percentage and match_percentage > best_match_percentage:
                    best_match_percentage = match_percentage
                    best_match_tag = replace_tag
                    replace_tags_used[replace_tag] = True
                    best_match_tag_id = k

            
            if best_match_tag and best_match_percentage >= match:
                result.append(replace_tags[best_match_tag_id])
            else:
                result.append(tags[i])

        # replace_tags の中から、tags に存在しないタグを追加
        extra_tags = [replace_tag for replace_tag, used in replace_tags_used.items() if not used]
        result.extend(extra_tags)
        
        return (", ".join(result),)


class TagSelector:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "categorys": ("STRING", {"default": "*"}),
                "exclude" : ("BOOLEAN", {"default": False}),
                "whitelist_only": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags:str, categorys:str, exclude:bool=False, whitelist_only:bool=False):
        tag_list = parse_tags(tags)
        tag_category = get_tag_category(2)
        target_category = [category.strip() for category in categorys.replace("\n",",").replace(".",",").split(",")]

        result = []
        for i, tag in enumerate(tag_list):
            tag_text = tag.format
            if tag_text in tag_category:
                if '*' == categorys:
                    result.append(tag)
                    continue

                category_list = tag_category.get(tag_text, [])

                for category in category_list:
                    if exclude:
                        if category not in target_category:
                            result.append(tag)
                            break
                    else:
                        if category in target_category:
                            result.append(tag)
                            break
            else:
                if whitelist_only:
                    continue
                result.append(tag)

        return (tagdata_to_string(result),)


class TagComparator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags1": ("STRING", ),
                "tags2": ("STRING", ),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("tags1_unique", "tags2_unique", "common_tags",)

    FUNCTION = "tag"
    
    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags1:str, tags2:str):
        tag_list1 = parse_tags(tags1)
        tag_list2 = parse_tags(tags2)

        tags1_unique = [tag for tag in tag_list1 if tag not in tag_list2]
        tags2_unique = [tag for tag in tag_list2 if tag not in tag_list1]
        common_tags = [tag for tag in tag_list1 if tag in tag_list2]

        return (tagdata_to_string(tags1_unique), tagdata_to_string(tags2_unique), tagdata_to_string(common_tags))


class TagFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
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
        
        include_categories = include_categories.strip()
        if include_categories:
            targets += [category.strip() for category in include_categories.replace("\n",",").split(",")]

        if exclude_categories:
            exclude_targets = [category.strip() for category in exclude_categories.replace("\n",",").split(",")]
            targets = [target for target in targets if target not in exclude_targets]
        
        tag_list = parse_tags(tags)

        result = []
        tag_category = get_tag_category(2)

        for i, tag in enumerate(tag_list):
            tag_text = tag.format
            if tag_text in tag_category:
                category_list = tag_category.get(tag_text, [])

                if not category_list:
                    continue

                for category in category_list:
                    if category in exclude_targets:
                        # not include this tag
                        break
                else:
                    if '*' == include_categories:
                        # include all tags
                        result.append(tag)
                    else:
                        for category in category_list:
                            if category in targets:
                                # include this tag
                                result.append(tag)
                                break

        return (tagdata_to_string(result),)


NODE_CLASS_MAPPINGS = {
    "TagSwitcher": TagSwitcher,
    "TagMerger": TagMerger,
    "TagFilter": TagFilter,
    "TagReplace": TagReplace,
    "TagRemover": TagRemover,
    "TagIf": TagIf,
    "TagSelector": TagSelector,
    "TagComparator": TagComparator
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "TagSwitcher": "TagSwitcher",
    "TagMerger": "TagMerger",
    "TagFilter": "TagFilter",
    "TagReplace": "TagReplace",
    "TagRemover": "TagRemover",
    "TagIf": "TagIf",
    "TagSelector": "TagSelector",
    "TagComparator": "TagComparator"
}


def simple_test():
    sample_tags = "school_uniform, (long hair, v:1.2), (sitting:1.5), (standing:0.5), attack, ((1girl)), original_tag"

    tf = TagFilter()

    result = tf.tag(sample_tags, pose=False, gesture=False, action=False, emotion=False, expression=False, camera=False, angle=False, sensitive=False, liquid=False,
                    include_categories="*", exclude_categories="pose")
    
    print("@@@ all in, pose out", result)
    if 'school_uniform, (long hair:1.2), (1girl:1.2)' != result[0]:
        raise Exception("Test failed")

    result = tf.tag(sample_tags, pose=False, gesture=False, action=False, emotion=False, expression=False, camera=False, angle=False, sensitive=False, liquid=False,
                    include_categories="clothing")
    print("@@@ clothing", result)
    if 'school_uniform' != result[0]:
        raise Exception("Test failed")

    result = tf.tag(sample_tags, pose=False, gesture=False, action=True, emotion=False, expression=False, camera=False, angle=False, sensitive=False, liquid=False)
    print("@@@ action", result)
    if 'attack' != result[0]:
        raise Exception("Test failed")

    result = tf.tag(sample_tags, pose=True, gesture=True, action=True, emotion=True, expression=False, camera=True, angle=False, sensitive=False, liquid=False)
    print("@@@ pose", result)
    if '(v:1.2), (sitting:1.5), (standing:0.5), attack' != result[0]:
        raise Exception("Test failed")

    ti = TagIf()
    result = ti.tag(tags=sample_tags, 
                 find="sitting", 
                 output1="sitting found")
    print("@@@ tagif sitting", result)
    if 'sitting found' != result[0]:
        raise Exception("Test failed")
    
    result = ti.tag(tags=sample_tags, 
                 find="school_uniform1", 
                 output1="found")
    print("@@@ tagif uniform not found", result)
    if '' != result[0]:
        raise Exception("Test failed")
    
    ts = TagSwitcher()
    
    result = ts.tag(input_tags=sample_tags, 
                 default_image="default", 
                 tags1="1girl,2girls", 
                 image1="image1", 
                 any1=True)
    print("@@@ tagswitcher found1", result)
    if 'image1' != result[0]:
        raise Exception("Test failed")
    
    result = ts.tag(input_tags=sample_tags, 
                 default_image="default", 
                 tags1="1girl,2girls", 
                 image1="image1", 
                 any1=False)
    print("@@@ tagswitcher found2", result)
    if 'default' != result[0]:
        raise Exception("Test failed")
    
    result = ts.tag(input_tags=sample_tags, 
                 default_image="default", 
                 tags1="2girls", 
                 image1="image1", 
                 any1=True)
    print("@@@ tagswitcher not found", result)
    if 'default' != result[0]:
        raise Exception("Test failed")
    
    tm = TagMerger()
    result = tm.tag(tags1=sample_tags, 
                 tags2="(1boy:1.5), (1girl:1.5), ((sitting)), (lying:0.5), long hair", 
                 under_score=True)
    print("@@@ tagmerger1", result)
    if 'school_uniform, (long_hair:1.2), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:1.2), original_tag, (1boy:1.5), (lying:0.5)' != result[0]:
        raise Exception("Test failed")
    
    result = tm.tag(tags1=sample_tags, 
                 tags2="(1boy:1.5), (1girl:1.5), ((sitting)), (lying:0.5), long_hair", 
                 under_score=False)
    print("@@@ tagmerger2 underscore", result)
    if 'school_uniform, (long hair:1.2), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:1.2), original_tag, (1boy:1.5), (lying:0.5)' != result[0]:
        raise Exception("Test failed")
    
    ts = TagSelector()
    result = ts.tag(tags=sample_tags, 
                 categorys="pose", 
                 whitelist_only=True)
    print("@@@ tagselector1 whitelist", result)
    if '(v:1.2), (sitting:1.5), (standing:0.5), attack' != result[0]:
        raise Exception("Test failed")
    
    result = ts.tag(tags=sample_tags, 
                 categorys="pose", 
                 whitelist_only=False)
    print("@@@ tagselector2 no whitelist", result)
    if '(v:1.2), (sitting:1.5), (standing:0.5), attack, original_tag' != result[0]:
        raise Exception("Test failed")
    
    result = ts.tag(tags=sample_tags, 
                 categorys="pose", 
                 exclude=True,
                 whitelist_only=True)
    print("@@@ tagselector3 whitelist exclude", result)
    if 'school_uniform, (long hair:1.2), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:1.2)' != result[0]:
        raise Exception("Test failed")
    
    result = ts.tag(tags=sample_tags, 
                 categorys="pose", 
                 exclude=True,
                 whitelist_only=False)
    print("@@@ tagselector3 no whitelist exclude", result)
    if 'school_uniform, (long hair:1.2), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:1.2), original_tag' != result[0]:
        raise Exception("Test failed")
    
    tc = TagComparator()
    result = tc.tag(tags1=sample_tags, 
                 tags2="(1boy:1.5), (1girl:1.5), ((sitting)), (lying:0.5), long hair, twintails")
    print("@@@ tagcomparator1", result)
    if 'school_uniform, (v:1.2), (standing:0.5), attack, original_tag' != result[0]:
        raise Exception("Test failed")
    if '(1boy:1.5), (lying:0.5), twintails' != result[1]:
        raise Exception("Test failed")
    if '(long hair:1.2), (sitting:1.5), (1girl:1.2)' != result[2]:
        raise Exception("Test failed")
    
    tr = TagRemover()
    result = tr.tag(tags=sample_tags, 
                 exclude_tags="school_uniform, long hair, 1girl")
    print("@@@ tagremover1", result)
    if '(v:1.2), (sitting:1.5), (standing:0.5), attack, original_tag' != result[0]:
        raise Exception("Test failed")


#if __name__ == "__main__":
#    simple_test()

