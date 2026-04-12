from Browser import browser_view
def test_browser_is_filling_up_with_all_datas():
    """test the input file are corectly generating one element for each file"""
    files = ["test1", "test2", "test3", "test4"]
    browser = browser_view.BrowserPanelView()
    layout = browser.display_files(files)
    assert layout.count() == len(files)
