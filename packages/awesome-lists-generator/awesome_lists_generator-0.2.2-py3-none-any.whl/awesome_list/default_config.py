from collections import OrderedDict

UP_ARROW_IMAGE = "https://git.io/JtehR"

def initialize_configuration(cfg: dict) -> dict: 
    config = cfg

    if "output_file" not in config:
        config["output_file"] = "README.md"

    if "latest_changes_file" not in config: 
        config["latest_changes_file"] = "latest-changes.md"

    if "awesome_history_folder" not in config:
        config["awesome_history_folder"] = "history"

    if "default_category" not in config:
        config["default_category"] = "other"
    
    if "disable_logging" not in config:
        config["disable_logging"] = False

    if "log_folder" not in config:
        config["log_folder"] = "logs"
    
    if "debug" not in config:
        config["debug"] = False
        
    if "up_arrow_image" not in config:
        config["up_arrow_image"] = "https://raw.githubusercontent.com/derekvincent/awesome-list-generator/main/assets/UpperCaret-32.png"
    '''
    Defines category_sort method used. 
        set = uses the order set in the config. 
        asc = Alphabetical ascending 
        dsc = Alphabetical dscending
    '''
    if "category_sort" not in config:
        config["category_sort"] = "set"

    if "list_title" not in config:
        config["list_title"] = "Awesome List"

    if "list_subtitle" not in config:
        config["list_subtitle"] = ""

    if "list_description" not in config:
        config["list_description"] = ""

    if "markdown_header_file" not in config:
        config["markdown_header_file"] = "config/header.md"

    if "markdown_footer_file" not in config:
        config["markdown_footer_file"] = "config/footer.md"
        
    return config

def initialize_categories(config: dict, categories: dict) -> OrderedDict:

    return_categories = OrderedDict()

    
    if categories:
        for category in categories:
            # print(f'Category: {category}')
            return_categories[category["name"]] = dict(category)

    if config["default_category"] not in return_categories:
        # Add others category at the last position
        return_categories[config["default_category"]] = dict(
            {"name": config["default_category"], "label": "Others"}
        )

    return return_categories
             