from spider import Spider


if __name__ == "__main__":
    website = Spider()
    # website.search('变身')
    # website.get_lists("http://www.biquge5200.com/85_85278/")
    print(website.get_page("http://www.biquge5200.com/81_81174/149183228.html"))
