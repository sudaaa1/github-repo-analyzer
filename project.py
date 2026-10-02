import requests
def main():
    owner, repo = prompt_repository()
    print(f"Owner: {owner}")
    print(f"Repo: {repo}")
    try:
        repo_response = fetch_repo(owner, repo)
    except requests.exceptions.RequestException:
        print("网络请求失败，请检查网络后重试。")
        return
    if repo_response.status_code == 200:
        print("请求成功")
        data = repo_response.json()
        repo_text = format_repo(data)
        print(repo_text)
        try:
            save_report(repo_text, "report.txt")
        except OSError:
            print("报告保存失败，请检查保存位置和写入权限")
            return
        print("报告已保存")
        show_contents(owner, repo)
        show_languages(owner, repo)
        try:
            readme_response = fetch_readme(owner,repo)
        except requests.exceptions.RequestException:
            print("README请求失败")
            return
        if readme_response.status_code == 200:
            print(readme_response.text)
            try:
                save_report(readme_response.text, "repo_readme.txt")
            except OSError:
                print("报告保存失败，请检查保存位置和写入权限")
                return
            print("README已保存")
            keyword = input("输入关键词: ").strip()
            if keyword == "":
                print("已跳过搜索")
                return
            results = search_readme(readme_response.text, keyword)
            if not results == []:
                for result in results:
                    print(result)
            else:
                print("未找到匹配内容")
        else:
            print(f"暂时无法获取 README: {readme_response.status_code}")
    else:
        print(f"暂时无法获取仓库信息: {repo_response.status_code}")

def prompt_repository():
    while True:
        try:
            name = input("owner/repo: ").strip()
            owner, repo = parse_repo_name(name)
        except ValueError:
            print("格式错误")
        else:
            break
    return owner, repo

def parse_repo_name(repo_name):
    owner, repo = repo_name.split("/")
    if owner == "" or repo == "":
        raise ValueError("不能为空")
    return owner, repo

def show_contents(owner, repo):
    try:
        contents_response = fetch_contents(owner, repo)
    except requests.exceptions.RequestException:
        print("目录请求失败")
        return
    if contents_response.status_code != 200:
        print(f"暂时无法获取目录: {contents_response.status_code}")
        return
    contents_data = contents_response.json()
    contents_text = format_contents(contents_data)
    print(f"仓库根目录: {contents_text}")
    analysis_results = analyze_contents(contents_data)
    if analysis_results:
        for analysis_result in analysis_results:
            print(analysis_result)
    else:
        print("未在根目录发现这三种配置文件")

def show_languages(owner, repo):
    try:
        languages_response = fetch_languages(owner, repo)
    except requests.exceptions.RequestException:
        print("语言请求失败")
        return
    if languages_response.status_code != 200:
        print(f"暂时无法获取语言分布: {languages_response.status_code}")
        return
    languages_data = languages_response.json()
    languages_text = format_languages(languages_data)
    print(f"语言分布（按代码字节数）: {languages_text}")

def fetch_repo(OWNER, REPO):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    response = requests.get(url, timeout=10)
    return response

def fetch_readme(OWNER, REPO):
    header = {"Accept":"application/vnd.github.raw+json"}
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/readme"
    response = requests.get(url, headers = header, timeout=10)
    return response

def fetch_contents(OWNER, REPO):
    header = {"Accept":"application/vnd.github+json"}
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
    response = requests.get(url, headers = header, timeout=10)
    return response

def fetch_languages(owner, repo):
    header = {"Accept":"application/vnd.github+json"}
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    response = requests.get(url, headers = header, timeout=10)
    return response

def format_languages(languages):
    lines = []
    sums = sum(languages.values())
    if sums == 0:
        return("暂无语言数据")
    for language, count in languages.items():
        percentage = (count / sums)* 100
        lines.append(f"{language}: {percentage:.1f}%")
    return "\n".join(lines)

def format_repo(data):
    full_name = data["full_name"]
    description = data["description"]
    language = data["language"]
    if description is None:
        description = "未提供简介"
    if language is None:
        language = "暂无主要语言信息"
    return (f"仓库: {full_name}\n简介: {description}\n语言: {language}")

def format_contents(contents):
    lines = []
    for item in contents:
        name = item["name"]
        item_type = item["type"]
        if item_type == "dir":
            label = "[目录]"
        elif item_type == "file":
            label = "[文件]"
        else:
            label = "[其他]"
        lines.append(f"{label} {name}")
    return "\n".join(lines)

def search_readme(readme_text, keyword):
    if keyword == "":
        return []
    lines = readme_text.splitlines()
    matches = []
    for line in lines:
        if keyword.lower() in line.lower():
            matches.append(line)
    return matches

def analyze_contents(contents):
    rules = {
        "requirements.txt": "Python 依赖清单",
        "pyproject.toml": "Python 项目配置",
        "package.json": "JavaScript/Node.js 项目配置"
    }
    results = []
    for item in contents:
        name = item["name"]
        item_type = item["type"]
        if item_type == "file" and name in rules:
            results.append(f"{name}: {rules[name]}")
    return results

def save_report(output_text, file_name):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(output_text + "\n")

if __name__ == "__main__":
    main()