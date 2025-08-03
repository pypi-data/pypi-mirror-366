import os
import shutil
import json
import csv
import zipfile
import chardet
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from difflib import unified_diff, SequenceMatcher
from collections import Counter
import jieba
from mcp.server.fastmcp import FastMCP

# 创建 MCP Server
mcp = FastMCP("桌面 TXT 文件管理器")


def get_desktop_path() -> Path:
    """获取桌面路径"""
    username = os.getenv("USER") or os.getenv("USERNAME")
    return Path(f"/Users/{username}/Desktop")


def ensure_backup_dir() -> Path:
    """确保备份目录存在"""
    backup_dir = get_desktop_path() / "txt_backups"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def detect_encoding(file_path: Path) -> str:
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding'] or 'utf-8'


@mcp.tool()
def count_desktop_txt_files() -> int:
    """统计桌面上的 .txt 文件数量"""
    desktop_path = get_desktop_path()
    txt_files = list(desktop_path.glob("*.txt"))
    return len(txt_files)


@mcp.tool()
def list_desktop_txt_files() -> str:
    """获取桌面上所有 .txt 文件的列表"""
    desktop_path = get_desktop_path()
    txt_files = list(desktop_path.glob("*.txt"))

    if not txt_files:
        return "桌面上没有找到 .txt 文件。"

    file_list = "\n".join([f"- {file.name}" for file in txt_files])
    return f"在桌面上找到 {len(txt_files)} 个 .txt 文件：\n{file_list}"


@mcp.tool()
def analyze_txt_file(filename: str) -> Dict:
    """分析指定 TXT 文件的详细信息"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return {"error": f"文件 {filename} 不存在"}

    stats = file_path.stat()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return {
        "文件名": filename,
        "文件大小": f"{stats.st_size / 1024:.2f} KB",
        "创建时间": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "修改时间": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "字符数": len(content),
        "行数": len(content.splitlines()),
        "单词数": len(content.split())
    }


@mcp.tool()
def get_txt_files_by_size() -> List[Tuple[str, float]]:
    """按大小排序获取所有 TXT 文件"""
    desktop_path = get_desktop_path()
    txt_files = list(desktop_path.glob("*.txt"))

    file_sizes = [(f.name, f.stat().st_size / 1024) for f in txt_files]
    return sorted(file_sizes, key=lambda x: x[1], reverse=True)


@mcp.tool()
def search_txt_content(keyword: str) -> str:
    """在桌面的 TXT 文件中搜索关键词"""
    desktop_path = get_desktop_path()
    txt_files = list(desktop_path.glob("*.txt"))

    results = []
    for file in txt_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                if keyword.lower() in content.lower():
                    results.append(file.name)
        except Exception as e:
            continue

    if not results:
        return f"没有找到包含关键词 '{keyword}' 的文件"

    return f"以下文件包含关键词 '{keyword}'：\n" + "\n".join([f"- {name}" for name in results])


@mcp.tool()
def backup_txt_file(filename: str) -> str:
    """备份指定的 TXT 文件"""
    desktop_path = get_desktop_path()
    backup_dir = ensure_backup_dir()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name

    shutil.copy2(file_path, backup_path)
    return f"文件已备份到：{backup_path}"


@mcp.tool()
def compare_txt_files(file1: str, file2: str) -> str:
    """比较两个 TXT 文件的内容差异"""
    desktop_path = get_desktop_path()
    path1 = desktop_path / file1
    path2 = desktop_path / file2

    if not path1.exists() or not path2.exists():
        return "一个或两个文件不存在"

    with open(path1, 'r', encoding='utf-8') as f1, open(path2, 'r', encoding='utf-8') as f2:
        content1 = f1.readlines()
        content2 = f2.readlines()

    diff = list(unified_diff(content1, content2, fromfile=file1, tofile=file2))
    if not diff:
        return "两个文件内容完全相同"

    return "文件差异：\n" + "".join(diff)


@mcp.tool()
def merge_txt_files(files: List[str], output_name: str) -> str:
    """合并多个 TXT 文件的内容"""
    desktop_path = get_desktop_path()
    output_path = desktop_path / output_name

    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for filename in files:
                file_path = desktop_path / filename
                if not file_path.exists():
                    continue
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(f"\n=== {filename} ===\n")
                    outfile.write(infile.read())
                    outfile.write("\n")
        return f"文件已合并到：{output_name}"
    except Exception as e:
        return f"合并文件时出错：{str(e)}"


@mcp.tool()
def create_txt_file(filename: str, content: str = "") -> str:
    """创建新的 TXT 文件"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not filename.endswith('.txt'):
        filename += '.txt'
        file_path = desktop_path / filename

    if file_path.exists():
        return f"文件 {filename} 已存在"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"文件 {filename} 已创建"
    except Exception as e:
        return f"创建文件时出错：{str(e)}"


@mcp.tool()
def append_to_txt_file(filename: str, content: str) -> str:
    """向 TXT 文件追加内容"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}")
        return f"内容已追加到文件 {filename}"
    except Exception as e:
        return f"追加内容时出错：{str(e)}"


@mcp.tool()
def get_file_statistics() -> Dict:
    """获取桌面 TXT 文件的统计信息"""
    desktop_path = get_desktop_path()
    txt_files = list(desktop_path.glob("*.txt"))

    if not txt_files:
        return {"error": "没有找到 TXT 文件"}

    total_size = sum(f.stat().st_size for f in txt_files)
    total_lines = 0
    total_words = 0

    for file in txt_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                total_lines += len(content.splitlines())
                total_words += len(content.split())
        except:
            continue

    return {
        "文件总数": len(txt_files),
        "总大小": f"{total_size / 1024:.2f} KB",
        "总行数": total_lines,
        "总单词数": total_words,
        "平均文件大小": f"{total_size / len(txt_files) / 1024:.2f} KB",
        "平均行数": total_lines / len(txt_files),
        "平均单词数": total_words / len(txt_files)
    }


@mcp.tool()
def convert_file_format(filename: str, target_format: str) -> str:
    """将 TXT 文件转换为其他格式（CSV、JSON）"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
            content = f.readlines()

        output_name = f"{file_path.stem}.{target_format}"
        output_path = desktop_path / output_name

        if target_format.lower() == 'csv':
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for line in content:
                    writer.writerow([line.strip()])

        elif target_format.lower() == 'json':
            data = [line.strip() for line in content]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        else:
            return f"不支持的格式：{target_format}"

        return f"文件已转换为 {output_name}"

    except Exception as e:
        return f"转换文件时出错：{str(e)}"


@mcp.tool()
def convert_file_encoding(filename: str, target_encoding: str) -> str:
    """转换文件编码"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        # 检测当前编码
        current_encoding = detect_encoding(file_path)

        # 读取文件内容
        with open(file_path, 'r', encoding=current_encoding) as f:
            content = f.read()

        # 写入新编码
        output_name = f"{file_path.stem}_{target_encoding}{file_path.suffix}"
        output_path = desktop_path / output_name

        with open(output_path, 'w', encoding=target_encoding) as f:
            f.write(content)

        return f"文件已转换为 {target_encoding} 编码，保存为 {output_name}"

    except Exception as e:
        return f"转换编码时出错：{str(e)}"


@mcp.tool()
def compress_txt_files(files: List[str], zip_name: str) -> str:
    """压缩多个 TXT 文件"""
    desktop_path = get_desktop_path()

    if not zip_name.endswith('.zip'):
        zip_name += '.zip'

    zip_path = desktop_path / zip_name

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in files:
                file_path = desktop_path / filename
                if file_path.exists():
                    zipf.write(file_path, filename)

        return f"文件已压缩到 {zip_name}"

    except Exception as e:
        return f"压缩文件时出错：{str(e)}"


@mcp.tool()
def extract_zip_file(zip_name: str) -> str:
    """解压缩 ZIP 文件"""
    desktop_path = get_desktop_path()
    zip_path = desktop_path / zip_name

    if not zip_path.exists():
        return f"文件 {zip_name} 不存在"

    try:
        extract_dir = desktop_path / f"{zip_path.stem}_extracted"
        extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)

        return f"文件已解压到 {extract_dir}"

    except Exception as e:
        return f"解压文件时出错：{str(e)}"


@mcp.tool()
def batch_rename_files(pattern: str, new_pattern: str) -> str:
    """批量重命名文件"""
    desktop_path = get_desktop_path()
    txt_files = list(desktop_path.glob("*.txt"))

    renamed = []
    for file in txt_files:
        if pattern in file.name:
            new_name = file.name.replace(pattern, new_pattern)
            new_path = file.parent / new_name
            try:
                file.rename(new_path)
                renamed.append(f"{file.name} -> {new_name}")
            except Exception:
                continue

    if not renamed:
        return "没有找到匹配的文件"

    return "重命名结果：\n" + "\n".join(renamed)


@mcp.tool()
def batch_convert_encoding(target_encoding: str) -> str:
    """批量转换文件编码"""
    desktop_path = get_desktop_path()
    txt_files = list(desktop_path.glob("*.txt"))

    converted = []
    for file in txt_files:
        try:
            current_encoding = detect_encoding(file)
            if current_encoding != target_encoding:
                with open(file, 'r', encoding=current_encoding) as f:
                    content = f.read()

                with open(file, 'w', encoding=target_encoding) as f:
                    f.write(content)

                converted.append(f"{file.name}: {current_encoding} -> {target_encoding}")
        except Exception:
            continue

    if not converted:
        return "没有需要转换的文件"

    return "转换结果：\n" + "\n".join(converted)


@mcp.tool()
def encrypt_file(filename: str, password: str) -> str:
    """加密文件（使用简单的异或加密）"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # 简单的异或加密
        encrypted = bytearray()
        for i, byte in enumerate(content):
            encrypted.append(byte ^ ord(password[i % len(password)]))

        output_name = f"{file_path.stem}_encrypted{file_path.suffix}"
        output_path = desktop_path / output_name

        with open(output_path, 'wb') as f:
            f.write(encrypted)

        return f"文件已加密并保存为 {output_name}"

    except Exception as e:
        return f"加密文件时出错：{str(e)}"


@mcp.tool()
def decrypt_file(filename: str, password: str) -> str:
    """解密文件"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # 异或解密（与加密相同）
        decrypted = bytearray()
        for i, byte in enumerate(content):
            decrypted.append(byte ^ ord(password[i % len(password)]))

        output_name = f"{file_path.stem}_decrypted{file_path.suffix}"
        output_path = desktop_path / output_name

        with open(output_path, 'wb') as f:
            f.write(decrypted)

        return f"文件已解密并保存为 {output_name}"

    except Exception as e:
        return f"解密文件时出错：{str(e)}"


@mcp.tool()
def format_text_content(filename: str, line_length: int = 80) -> str:
    """格式化文本内容（自动换行）"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
            content = f.read()

        # 简单的文本格式化
        words = content.split()
        formatted_lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= line_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                formatted_lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            formatted_lines.append(' '.join(current_line))

        output_name = f"{file_path.stem}_formatted{file_path.suffix}"
        output_path = desktop_path / output_name

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(formatted_lines))

        return f"文件已格式化并保存为 {output_name}"

    except Exception as e:
        return f"格式化文件时出错：{str(e)}"


@mcp.tool()
def extract_keywords(filename: str, top_n: int = 10) -> str:
    """提取文本文件中的关键词"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
            content = f.read()

        # 使用结巴分词
        words = jieba.cut(content)
        # 过滤停用词和标点符号
        words = [word for word in words if len(word.strip()) > 1 and not re.match(r'[^\w\s]', word)]
        # 统计词频
        word_freq = Counter(words)

        # 获取前N个关键词
        top_keywords = word_freq.most_common(top_n)

        result = f"文件 {filename} 的前 {top_n} 个关键词：\n"
        for word, freq in top_keywords:
            result += f"- {word}: {freq}次\n"

        return result

    except Exception as e:
        return f"提取关键词时出错：{str(e)}"


@mcp.tool()
def analyze_text_statistics(filename: str) -> Dict:
    """分析文本文件的详细统计信息"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return {"error": f"文件 {filename} 不存在"}

    try:
        with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
            content = f.read()

        # 基本统计
        lines = content.splitlines()
        words = content.split()
        chars = list(content)

        # 句子统计（简单按句号、问号、感叹号分割）
        sentences = re.split(r'[。！？.!?]', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 计算平均句子长度
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0

        return {
            "文件名": filename,
            "字符数": len(chars),
            "行数": len(lines),
            "单词数": len(words),
            "句子数": len(sentences),
            "平均句子长度": f"{avg_sentence_length:.2f}",
            "非空行数": len([line for line in lines if line.strip()]),
            "最长行长度": max(len(line) for line in lines),
            "最短行长度": min(len(line) for line in lines) if lines else 0
        }

    except Exception as e:
        return {"error": f"分析文本时出错：{str(e)}"}


@mcp.tool()
def regex_search(filename: str, pattern: str) -> str:
    """使用正则表达式搜索文本内容"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
            content = f.read()

        # 编译正则表达式
        regex = re.compile(pattern)
        matches = regex.finditer(content)

        # 收集匹配结果
        results = []
        for match in matches:
            line_number = content[:match.start()].count('\n') + 1
            line_content = content.split('\n')[line_number - 1]
            results.append(f"第 {line_number} 行: {line_content}")

        if not results:
            return f"没有找到匹配模式 '{pattern}' 的内容"

        return f"找到 {len(results)} 个匹配：\n" + "\n".join(results)

    except re.error:
        return "正则表达式格式错误"
    except Exception as e:
        return f"搜索时出错：{str(e)}"


@mcp.tool()
def regex_replace(filename: str, pattern: str, replacement: str) -> str:
    """使用正则表达式替换文本内容"""
    desktop_path = get_desktop_path()
    file_path = desktop_path / filename

    if not file_path.exists():
        return f"文件 {filename} 不存在"

    try:
        with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
            content = f.read()

        # 执行替换
        new_content = re.sub(pattern, replacement, content)

        # 保存结果
        output_name = f"{file_path.stem}_replaced{file_path.suffix}"
        output_path = desktop_path / output_name

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"替换完成，结果已保存到 {output_name}"

    except re.error:
        return "正则表达式格式错误"
    except Exception as e:
        return f"替换时出错：{str(e)}"


@mcp.tool()
def compare_files_visual(file1: str, file2: str) -> str:
    """可视化比较两个文件的内容差异"""
    desktop_path = get_desktop_path()
    path1 = desktop_path / file1
    path2 = desktop_path / file2

    if not path1.exists() or not path2.exists():
        return "一个或两个文件不存在"

    try:
        with open(path1, 'r', encoding=detect_encoding(path1)) as f1, \
                open(path2, 'r', encoding=detect_encoding(path2)) as f2:
            content1 = f1.readlines()
            content2 = f2.readlines()

        # 使用 SequenceMatcher 进行更详细的比较
        matcher = SequenceMatcher(None, content1, content2)
        differences = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                differences.append(f"{tag}:")
                if tag in ('replace', 'delete'):
                    differences.extend(f"- {line}" for line in content1[i1:i2])
                if tag in ('replace', 'insert'):
                    differences.extend(f"+ {line}" for line in content2[j1:j2])

        if not differences:
            return "两个文件内容完全相同"

        return "文件差异：\n" + "\n".join(differences)

    except Exception as e:
        return f"比较文件时出错：{str(e)}"


@mcp.tool()
def merge_files_with_conflict_resolution(file1: str, file2: str, output_name: str) -> str:
    """合并两个文件，并处理冲突"""
    desktop_path = get_desktop_path()
    path1 = desktop_path / file1
    path2 = desktop_path / file2

    if not path1.exists() or not path2.exists():
        return "一个或两个文件不存在"

    try:
        with open(path1, 'r', encoding=detect_encoding(path1)) as f1, \
                open(path2, 'r', encoding=detect_encoding(path2)) as f2:
            content1 = f1.readlines()
            content2 = f2.readlines()

        # 使用 SequenceMatcher 找出差异
        matcher = SequenceMatcher(None, content1, content2)
        merged_content = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                merged_content.extend(content1[i1:i2])
            elif tag == 'replace':
                # 在冲突处添加标记
                merged_content.append("<<<<<<< HEAD\n")
                merged_content.extend(content1[i1:i2])
                merged_content.append("=======\n")
                merged_content.extend(content2[j1:j2])
                merged_content.append(">>>>>>> MERGE\n")
            elif tag == 'delete':
                merged_content.extend(content1[i1:i2])
            elif tag == 'insert':
                merged_content.extend(content2[j1:j2])

        # 保存合并结果
        output_path = desktop_path / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(merged_content)

        return f"文件已合并到 {output_name}，请检查并解决冲突"

    except Exception as e:
        return f"合并文件时出错：{str(e)}"


@mcp.tool()
def auto_backup_files(interval_minutes: int = 60) -> str:
    """自动备份文件（需要手动启动）"""
    desktop_path = get_desktop_path()
    backup_dir = ensure_backup_dir()

    try:
        txt_files = list(desktop_path.glob("*.txt"))
        if not txt_files:
            return "没有找到需要备份的文件"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = backup_dir / f"backup_{timestamp}"
        backup_subdir.mkdir(exist_ok=True)

        for file in txt_files:
            shutil.copy2(file, backup_subdir / file.name)

        return f"文件已备份到 {backup_subdir}"

    except Exception as e:
        return f"备份文件时出错：{str(e)}"


@mcp.tool()
def calculate_text_similarity(file1: str, file2: str) -> str:
    """计算两个文本文件的相似度"""
    desktop_path = get_desktop_path()
    path1 = desktop_path / file1
    path2 = desktop_path / file2

    if not path1.exists() or not path2.exists():
        return "一个或两个文件不存在"

    try:
        with open(path1, 'r', encoding=detect_encoding(path1)) as f1, \
                open(path2, 'r', encoding=detect_encoding(path2)) as f2:
            content1 = f1.read()
            content2 = f2.read()

        # 使用 SequenceMatcher 计算相似度
        similarity = SequenceMatcher(None, content1, content2).ratio()

        return f"文件相似度：{similarity:.2%}"

    except Exception as e:
        return f"计算相似度时出错：{str(e)}"


if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport='stdio')


def main() -> None:
    # 初始化并运行服务器
    mcp.run()
