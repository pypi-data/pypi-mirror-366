import DrissionPage._pages

replace_name_dict = {
    'scrollIntoViewIfNeeded' : 'flcat_scrollIntoViewIfNeeded',
    'getComputedStyle' : 'flcat_getComputedStyle'
}

def auto_replace(tab : "DrissionPage._pages.mix_tab.MixTab"):
    js = f'Element.prototype.{replace_name_dict["scrollIntoViewIfNeeded"]} = Element.prototype.scrollIntoViewIfNeeded;'
    js +=  f'window.{replace_name_dict["getComputedStyle"]} = window.getComputedStyle;'
    tab.add_init_js(js)