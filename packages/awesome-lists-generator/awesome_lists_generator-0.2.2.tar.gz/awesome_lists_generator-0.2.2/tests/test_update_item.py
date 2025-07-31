from awesome_list import awesome_items 

def test_update_item_success():

    item = {}
    item["link_id"] = "https://news.sap.com"
    item["name"] = "SAP News"
    item["description"] = ""

    awesome_items.update_item(item)

    assert item["name"] == "SAP News Center"
    assert item["description"].startswith("News & press releases from SAP")
    assert item["update_at"] == ''
    assert item["published_at"] == ''

def test_update_item_non_valid_url():
    item = {}
    item["link_id"] = "https://kemikal.io/notfound"
    item["name"] = "Kemikal IO - Not Found"
    item["description"] = ""

    assert item["name"] == "Kemikal IO"