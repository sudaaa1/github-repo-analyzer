import pytest
import requests
from project import parse_repo_name
from project import format_repo
from project import save_report
from project import search_readme
from project import format_contents
from project import analyze_contents
from project import prompt_repository
from project import show_contents
from project import format_languages

def test_parse_repo_name():
    assert parse_repo_name("owner/repo") == ("owner", "repo")

def test_get_missing_owner():
    with pytest.raises(ValueError):
        parse_repo_name("/repo")

def test_get_missing_repo():
    with pytest.raises(ValueError):
        parse_repo_name("owner/")

def test_get_missing_separator():
    with pytest.raises(ValueError):
        parse_repo_name("owner repo")

def test_get_too_many_separators():
    with pytest.raises(ValueError):
        parse_repo_name("owner//repo")


def test_normal():
    # 测试常规完整数据
    data = {
        "full_name": "cs50/python",
        "description": "This is CS50",
        "language": "Python",
    }
    assert (
        format_repo(data)
        == "仓库: cs50/python\n简介: This is CS50\n语言: Python"
    )


def test_none_description():
    # 测试 description 为 None 的情况
    data = {
        "full_name": "cs50/python",
        "description": None,
        "language": "Python",
    }
    assert (
        format_repo(data) == "仓库: cs50/python\n简介: 未提供简介\n语言: Python"
    )


def test_none_language():
    # 测试 language 为 None 的情况
    data = {
        "full_name": "cs50/python",
        "description": "This is CS50",
        "language": None,
    }
    assert (
        format_repo(data)
        == "仓库: cs50/python\n简介: This is CS50\n语言: 暂无主要语言信息"
    )


def test_both_none():
    # 测试两者都为 None 的情况
    data = {
        "full_name": "cs50/python",
        "description": None,
        "language": None,
    }
    assert (
        format_repo(data)
        == "仓库: cs50/python\n简介: 未提供简介\n语言: 暂无主要语言信息"
    )


def test_missing_key():
    # 测试缺少 key 抛出 KeyError（CS50P 中学过的 pytest.raises）
    with pytest.raises(KeyError):
        format_repo({"full_name": "cs50/python"})

def test_save_report(tmp_path):
    text = "你好, readme"
    file_path = tmp_path / "sample.txt"
    save_report(text,file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        actual = file.read()
    assert actual == text + "\n"

def test_search_readme_insensitive():
    readme = "Flask简介\n安装方法\nFlask示例\n"
    assert search_readme(readme,"flaSK") == ["Flask简介","Flask示例"]

def test_search_readme_nomatch():
    readme = "Flask简介\n安装方法\nFlask示例\n"
    assert search_readme(readme,"django") == []

def test_search_readme_empty_text():
    readme = ""
    assert search_readme(readme,"flask") == []

def test_search_readme_empty_keyword():
    readme = "Flask简介\n安装方法\nFlask示例\n"
    assert search_readme(readme,"") == []

def test_format_contents():
    contents = [
        {"name": "docs", "type": "dir"},
        {"name": "README.md", "type": "file"},
    ]
    assert format_contents(contents) == "[目录] docs\n[文件] README.md"

def test_format_contents_other_type():
    items = [{"name": "link", "type": "unknow"}]
    assert format_contents(items) == "[其他] link"


def test_format_contents_empty():
    assert format_contents([]) == ""

def test_analyze_contents_normal():
    contents = [
        {"name": "requirements.txt", "type": "file"},
        {"name": "pyproject.toml", "type": "file"},
    ]
    assert analyze_contents(contents) == ["requirements.txt: Python 依赖清单", "pyproject.toml: Python 项目配置"]

def test_analyze_contents_ignores_unmatched():
    contents = [
            {"name": "README.md", "type": "file"},
            {"name": "requirements.txt", "type": "dir"},
        ]
    assert analyze_contents(contents) == []

def test_analyze_contents_empty():
    contents = []
    assert analyze_contents(contents) == []

def test_prompt_repository_valid(monkeypatch):
    def fake_input(prompt):
        return "expressjs/express"
    monkeypatch.setattr("builtins.input", fake_input)
    actual = prompt_repository()
    assert actual == ("expressjs", "express")

def test_prompt_repository_retries(monkeypatch):
    answers = ["wrong", "expressjs/express"]
    def fake_input(prompt):
        return answers.pop(0)
    monkeypatch.setattr("builtins.input", fake_input)
    actual = prompt_repository()
    assert actual == ("expressjs", "express")

def test_show_contents(monkeypatch, capsys):
    def fake_fetch_contents(owner, repo):
        raise requests.exceptions.Timeout("模拟超时")
    monkeypatch.setattr("project.fetch_contents", fake_fetch_contents)
    show_contents("expressjs", "express")
    captured = capsys.readouterr()
    assert captured.out == "目录请求失败\n"

def test_format_languages_normal():
    assert format_languages(
        {"Python": 800, "JavaScript": 200}
    ) == "Python: 80.0%\nJavaScript: 20.0%"

def test_format_languages_empty():
    assert format_languages({}) == "暂无语言数据"

def test_format_languages_zero_total():
    assert format_languages({"Python": 0, "JavaScript": 0}) == "暂无语言数据"