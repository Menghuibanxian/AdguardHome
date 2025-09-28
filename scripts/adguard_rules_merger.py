import os
import re
import requests
import time
import json
import datetime
import os

# 获取北京时间
def get_beijing_time():
    """获取北京时间"""
    # 使用多个API源获取北京时间，增加可靠性
    urls = [
        "https://quan.suning.com/getSysTime.do",  # 优先使用HTTPS版本的苏宁API
        "https://www.baidu.com",                 # 从响应头获取时间
        "https://a.jd.com/js/union_ajax.js",     # 从响应头获取时间
        "https://pages.github.com",              # 从响应头获取时间
        "https://consumer.huawei.com",           # 从响应头获取时间
        "https://www.mi.com",                    # 从响应头获取时间
        "http://quan.suning.com/getSysTime.do"    # 备用：HTTP版本的苏宁API
    ]
    
    for url in urls:
        try:
            # 设置较短的超时时间，避免长时间等待
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, timeout=3, headers=headers)
            
            # 从响应头中获取时间
            if 'Date' in response.headers:
                date_str = response.headers['Date']
                # 解析HTTP日期格式
                gmt_time = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
                # 转换为北京时间（GMT+8）
                beijing_time = gmt_time + datetime.timedelta(hours=8)
                return beijing_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            # 出错时继续尝试下一个源
            continue
    
    # 如果所有API都失败，回退到本地时间
    print("获取北京时间失败，使用本地时间")
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 文件路径配置
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLACKLIST_FILE = os.path.join(ROOT_DIR, "Black.txt")
COLORFUL_FILE = os.path.join(ROOT_DIR, "scripts", "colorful.txt")
WHITELIST_FILE = os.path.join(ROOT_DIR, "White.txt")

# 黑名单源
BLACKLIST_SOURCES = {
    "AdGuard DNS filter": "https://adguardteam.github.io/HostlistsRegistry/assets/filter_1.txt",
    "秋风的规则          ": "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt",
    "GitHub加速         ": "https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts",
    "广告规则            ": "https://raw.githubusercontent.com/huantian233/HT-AD/main/AD.txt",
    "DD自用             ": "https://raw.githubusercontent.com/afwfv/DD-AD/main/rule/DD-AD.txt",
    "消失DD             ": "https://raw.githubusercontent.com/afwfv/DD-AD/main/rule/dns.txt",
    "大萌主             ": "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt",
    "逆向涉猎            ": "https://raw.githubusercontent.com/790953214/qy-Ads-Rule/main/black.txt",
    "下个ID见           ": "https://raw.githubusercontent.com/2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts",
    "那个谁520          ": "https://raw.githubusercontent.com/qq5460168/666/master/rules.txt",
    "1hosts            ": "https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/adblock.txt",
    "茯苓的广告规则       ": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingBlockList.txt",
    "立场不定的          ": "https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/Uncertain%20position.txt"
}

# 白名单源
WHITELIST_SOURCES = {
    "茯苓允许列表  ": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingAllowList.txt",
    "666         ": "https://raw.githubusercontent.com/qq5460168/666/master/allow.txt",
    "个人自用白名单": "https://raw.githubusercontent.com/qq5460168/dangchu/main/white.txt",
    "冷漠白名单   ": "https://file-git.trli.club/file-hosts/allow/Domains",
    "BlueSkyXN   ": "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/ok.txt"
}

def remove_comments_and_blank_lines(rules):
    """移除规则中的注释和空行"""
    result = []
    for line in rules:
        # 去掉行首和行尾的空白字符
        line = line.strip()
        # 跳过空行和注释行
        if not line or line.startswith("!") or line.startswith("#"):
            continue
        # 去掉行内的注释
        line = re.sub(r"[!#].*$", "", line).strip()
        if line:
            result.append(line)
    return result

def extract_whitelist_from_blacklist(blacklist_rules):
    """从黑名单规则中提取白名单规则"""
    # 假设白名单规则在黑名单中以特定格式存在，例如以@@开头（AdGuard格式）
    whitelist_rules = [rule for rule in blacklist_rules if rule.startswith("@@")]
    # 过滤后的黑名单规则（移除白名单规则）
    filtered_blacklist = [rule for rule in blacklist_rules if not rule.startswith("@@")]
    return filtered_blacklist, whitelist_rules

def deduplicate_rules(rules):
    """移除重复的规则"""
    # 使用集合去重并保持顺序
    seen = set()
    result = []
    for rule in rules:
        if rule not in seen:
            seen.add(rule)
            result.append(rule)
    return result

def download_blacklist_sources():
    """下载所有黑名单源的规则"""
    all_blacklist_rules = []
    
    print(f"开始下载 {len(BLACKLIST_SOURCES)} 个黑名单源...")
    
    for name, url in BLACKLIST_SOURCES.items():
        try:
            print(f"正在下载 {name} ({url})...")
            response = requests.get(url, timeout=30)  # 增加超时时间
            response.raise_for_status()
            
            # 处理不同格式的规则文件
            rules = response.text.split("\n")
            # 移除注释和空行
            cleaned_rules = remove_comments_and_blank_lines(rules)
            
            all_blacklist_rules.extend(cleaned_rules)
            print(f"成功下载 {name}，获取到 {len(cleaned_rules)} 条规则")
            
            # 添加延迟以避免请求过于频繁
            time.sleep(1)
        except Exception as e:
            print(f"下载 {name} 失败 ({url}): {e}")
    
    print(f"所有黑名单源下载完成，共获取到 {len(all_blacklist_rules)} 条规则")
    return all_blacklist_rules

def download_whitelist_sources():
    """下载所有白名单源的规则"""
    all_whitelist_rules = []
    
    print(f"开始下载 {len(WHITELIST_SOURCES)} 个白名单源...")
    
    for name, url in WHITELIST_SOURCES.items():
        try:
            print(f"正在下载 {name} ({url})...")
            response = requests.get(url, timeout=30)  # 增加超时时间
            response.raise_for_status()
            
            # 处理不同格式的规则文件
            rules = response.text.split("\n")
            # 移除注释和空行
            cleaned_rules = remove_comments_and_blank_lines(rules)
            
            all_whitelist_rules.extend(cleaned_rules)
            print(f"成功下载 {name}，获取到 {len(cleaned_rules)} 条规则")
            
            # 添加延迟以避免请求过于频繁
            time.sleep(1)
        except Exception as e:
            print(f"下载 {name} 失败 ({url}): {e}")
    
    print(f"所有白名单源下载完成，共获取到 {len(all_whitelist_rules)} 条规则")
    return all_whitelist_rules

def main():
    print("开始处理AdGuardHome规则...")
    
    # 获取当前北京时间，只获取一次，所有文件使用相同的时间戳
    current_time = get_beijing_time()
    
    # 下载所有黑名单源
    blacklist_rules = download_blacklist_sources()
    
    # 从黑名单中提取白名单规则
    filtered_blacklist, extracted_whitelist = extract_whitelist_from_blacklist(blacklist_rules)
    print(f"从黑名单中提取的白名单规则数量: {len(extracted_whitelist)}")
    print(f"过滤后的黑名单规则数量: {len(filtered_blacklist)}")
    
    # 黑名单去重
    deduplicated_blacklist = deduplicate_rules(filtered_blacklist)
    print(f"去重后的黑名单规则数量: {len(deduplicated_blacklist)}")
    
    # 使用之前获取的时间戳
    
    # 保存处理后的黑名单
    with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
        # 按照用户要求的格式添加文件头部
        f.write(f"# 更新时间: {current_time}\n")
        f.write(f"# 黑名单规则数：{len(deduplicated_blacklist)}\n")
        f.write(f"# 作者名称: Menghuibanxian\n")
        f.write(f"# 作者主页:https://github.com/Menghuibanxian/AdguardHome\n")
        f.write("\n")
        
        # 添加规则内容并过滤掉以[开头且以]结尾的行
        for rule in deduplicated_blacklist:
            if not (rule.startswith('[') and rule.endswith(']')):
                f.write(f"{rule}\n")
    print(f"已保存处理后的黑名单到 {BLACKLIST_FILE}")
    
    # 使用之前获取的时间戳
    
    # 保存提取的白名单到colorful.txt
    with open(COLORFUL_FILE, "w", encoding="utf-8") as f:
        # 按照用户要求的格式添加文件头部
        f.write(f"# 更新时间: {current_time}\n")
        f.write(f"# 提取的规则数：{len(extracted_whitelist)}\n")
        f.write("\n")
        
        # 添加规则内容
        for rule in extracted_whitelist:
            f.write(f"{rule}\n")
    print(f"已保存提取的白名单到 {COLORFUL_FILE}")
    
    # 下载白名单源
    downloaded_whitelist = download_whitelist_sources()
    print(f"下载的白名单规则数量: {len(downloaded_whitelist)}")
    
    # 合并提取的白名单和下载的白名单
    merged_whitelist = extracted_whitelist + downloaded_whitelist
    
    # 去重
    deduplicated_whitelist = deduplicate_rules(merged_whitelist)
    print(f"合并去重后的白名单规则数量: {len(deduplicated_whitelist)}")
    
    # 保存最终的白名单
    # 使用之前获取的时间戳
    
    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
        # 按照用户要求的格式添加文件头部
        f.write(f"# 更新时间: {current_time}\n")
        f.write(f"# 白名单规则数：{len(deduplicated_whitelist)}\n")
        f.write(f"# 作者名称: Menghuibanxian\n")
        f.write(f"# 作者主页:\n")
        f.write("\n")
        
        # 添加规则内容并过滤掉以[开头且以]结尾的行
        for rule in deduplicated_whitelist:
            if not (rule.startswith('[') and rule.endswith(']')):
                f.write(f"{rule}\n")
    print(f"已保存最终的白名单到 {WHITELIST_FILE}")
    
    print("AdGuardHome规则处理完成！")

if __name__ == "__main__":
    main()
