import requests
import os
from datetime import datetime, timezone, timedelta
import re

# 黑名单源
BLACKLIST_SOURCES = {
    "AdGuard DNS filter": "https://adguardteam.github.io/HostlistsRegistry/assets/filter_1.txt",
    "秋风的规则": "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt",
    "GitHub加速": "https://raw.hellogithub.com/hosts",
    "酷安广告规则": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/OtherRules/CoolapkRules.txt",
    "广告规则": "https://raw.githubusercontent.com/huantian233/HT-AD/main/AD.txt",
    "不是DD啊": "https://raw.githubusercontent.com/afwfv/DD-AD/main/rule/DD-AD.txt",
    "大萌主": "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt",
    "逆向涉猎": "https://raw.githubusercontent.com/790953214/qy-Ads-Rule/main/black.txt",
    "下个ID见": "https://raw.githubusercontent.com/2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts",
    "那个谁520": "https://raw.githubusercontent.com/qq5460168/666/master/rules.txt",
    "1hosts": "https://o0.pages.dev/Lite/adblock.txt",
    "茯苓的广告规则": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingBlockList.txt",
    "极客爱好者": "https://www.kbsml.com/wp-content/uploads/adblock/adguard/adg-kall-dns.txt",
    "立场不定的": "https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/Uncertain%20position.txt"
}

# 白名单源
WHITELIST_SOURCES = {
    "茯苓允许列表": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingAllowList.txt",
    "666": "https://raw.githubusercontent.com/qq5460168/666/master/allow.txt",
    "个人自用白名单": "https://hub.gitmirror.com/https://raw.githubusercontent.com/qq5460168/dangchu/main/white.txt",
    "冷漠白名单": "https://file-git.trli.club/file-hosts/allow/Domains"
}

def download_file(url, timeout=30):
    """下载文件内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return None

def extract_blacklist_domains(content):
    """从黑名单内容中提取域名"""
    domains = set()
    # 匹配域名的正则表达式
    domain_pattern = re.compile(r'^[0-9a-zA-Z]([0-9a-zA-Z\-]{0,61}[0-9a-zA-Z])?(\.[0-9a-zA-Z]([0-9a-zA-Z\-]{0,61}[0-9a-zA-Z])?)*$')
    # 匹配特殊广告规则的正则表达式 (如 *-ad.example.com*)
    special_rule_pattern = re.compile(r'^\*.*\*$')
    # 匹配hosts文件格式的正则表达式
    hosts_pattern = re.compile(r'^\d+\.\d+\.\d+\.\d+\s+.*$')
    
    # 按行处理内容
    for line in content.splitlines():
        line = line.strip()
        
        # 跳过注释和空行 (只跳过每行第一个字符是 # 或 ! 的行)
        if not line or (line.startswith('#') or line.startswith('!')):
            continue
            
        # 处理hosts文件格式 (保留原始格式)
        if hosts_pattern.match(line):
            domains.add(line)
            continue
            
        # 处理adblock格式
        if '||' in line and '^' in line and not line.startswith('@@'):
            domains.add(line)
            continue
            
        # 处理特殊广告规则 (如 *-ad.example.com*)
        if special_rule_pattern.match(line):
            domains.add(line)
            continue
            
        # 处理纯域名格式
        if domain_pattern.match(line):
            domains.add(line)
            
    return domains

def extract_whitelist_domains(content):
    """从白名单内容中提取域名"""
    domains = set()
    
    # 匹配域名的正则表达式
    domain_pattern = re.compile(r'^[0-9a-zA-Z]([0-9a-zA-Z\-]{0,61}[0-9a-zA-Z])?(\.[0-9a-zA-Z]([0-9a-zA-Z\-]{0,61}[0-9a-zA-Z])?)*$')
    
    # 按行处理内容
    for line in content.splitlines():
        line = line.strip()
        
        # 跳过注释和空行 (只跳过每行第一个字符是 # 或 ! 的行)
        if not line or (line.startswith('#') or line.startswith('!')):
            continue
            
        # 处理白名单adblock格式 (@@||example.org^)
        if line.startswith('@@||') and '^' in line:
            domains.add(line)
            continue
            
        # 处理hosts文件格式 (127.0.0.1 example.org)
        if line.startswith('127.0.0.1') or line.startswith('0.0.0.0'):
            parts = line.split()
            if len(parts) >= 2:
                domain = parts[1]
                if domain_pattern.match(domain):
                    domains.add(domain)
            continue
            
        # 处理纯域名格式
        if domain_pattern.match(line):
            domains.add(line)
            
    return domains

def update_impurities_file(filename, sources, file_type, is_whitelist=False):
    """更新包含杂质的文件"""
    print(f"开始更新 {filename}...")
    
    # 获取北京时间
    beijing_time = get_beijing_time()
    formatted_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 添加文件头注释
    all_content = f"# 更新时间: {formatted_time}\n\n"
    all_domains = set()
    
    for name, url in sources.items():
        print(f"正在下载 {name} ({url})...")
        content = download_file(url)
        if content:
            # 过滤掉以!和#开头的注释行 (只过滤每行第一个字符是 # 或 ! 的行)
            filtered_lines = []
            for line in content.splitlines():
                stripped_line = line.lstrip()  # 使用 lstrip() 只去除行首的空白字符
                # 检查去除空白字符后，第一个字符是否是 # 或 !
                if not (stripped_line.startswith('#') or stripped_line.startswith('!')):
                    # 只添加非空行
                    if stripped_line:
                        filtered_lines.append(line)
            
            # 如果all_content不为空，则添加换行符分隔不同来源的内容
            if all_content:
                all_content += '\n'
            all_content += '\n'.join(filtered_lines)
            
            # 提取域名用于去重
            if is_whitelist:
                domains = extract_whitelist_domains(content)
            else:
                domains = extract_blacklist_domains(content)
            all_domains.update(domains)
            print(f"  - 提取到 {len(domains)} 个域名")
        else:
            # 如果all_content不为空，则添加换行符
            if all_content:
                all_content += '\n'
            all_content += f"# 来源: {name} (下载失败)"
    
    # 保存包含杂质的文件
    impurities_path = os.path.join("Ipurities", filename)
    with open(impurities_path, "w", encoding="utf-8") as f:
        f.write(all_content)
    
    print(f"{filename} 更新完成，共 {len(all_domains)} 个唯一域名")
    return all_domains

def get_beijing_time():
    """获取北京时间"""
    # 首先尝试从多个时间API获取时间
    time_apis = [
        "http://worldtimeapi.org/api/timezone/Asia/Shanghai",
        "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp",
        "http://quan.suning.com/getSysTime.do"
    ]
    
    for api_url in time_apis:
        try:
            if "worldtimeapi.org" in api_url:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # 解析时间字符串
                    dt = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
                    # 转换为北京时间（UTC+8）
                    beijing_time = dt.astimezone(timezone(timedelta(hours=8)))
                    print(f"使用网络时间API获取时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    return beijing_time
            elif "taobao.com" in api_url:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    timestamp = int(data['data']['t']) / 1000  # 转换为秒
                    beijing_time = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8)))
                    print(f"使用淘宝时间API获取时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    return beijing_time
            elif "suning.com" in api_url:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    time_str = data['sysTime1']
                    # 解析时间字符串（苏宁的时间格式是YYYYMMDDHHMMSS）
                    if len(time_str) == 14:
                        beijing_time = datetime.strptime(time_str, '%Y%m%d%H%M%S')
                    else:
                        beijing_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    beijing_time = beijing_time.replace(tzinfo=timezone(timedelta(hours=8)))
                    print(f"使用苏宁时间API获取时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    return beijing_time
        except Exception as e:
            print(f"尝试使用时间API {api_url} 失败: {e}")
            continue
    
    # 如果所有网络时间API都失败，使用本地时间
    print("所有网络时间API均不可用，使用本地时间")
    local_tz = timezone(timedelta(hours=8))
    local_time = datetime.now(local_tz)
    print(f"使用本地时间: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
    return local_time

def update_main_file(filename, domains, is_whitelist=False):
    """更新主文件（去重后的文件）"""
    print(f"正在更新主文件 {filename}...")
    
    # 按字母顺序排序域名
    sorted_domains = sorted(domains)
    
    # 获取北京时间
    beijing_time = get_beijing_time()
    formatted_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 添加文件头注释
    content = "# 更新时间: " + formatted_time + "\n"
    rule_type = "白名单" if is_whitelist else "黑名单"
    content += f"# {rule_type}规则数：{len(domains)}\n"
    content += "# 作者名称: Menghuibanxian\n"
    content += "# 作者主页: https://github.com/Menghuibanxian/AdguardHome\n\n"
    
    # 根据是黑名单还是白名单使用不同的格式
    for domain in sorted_domains:
        # 如果是白名单且规则以 @@ 开头，保持原始格式
        if is_whitelist and domain.startswith('@@'):
            content += f"{domain}\n"
        # 如果是黑名单且规则已经包含 || 或以 * 开头或包含IP地址，保持原始格式
        elif not is_whitelist and (domain.startswith('||') or domain.startswith('*') or re.match(r'^\d+\.\d+\.\d+\.\d+\s+.*$', domain)):
            content += f"{domain}\n"
        # 如果是白名单且规则不以 @@ 开头，添加 @@|| 前缀
        elif is_whitelist:
            content += f"@@||{domain}^\n"
        # 如果是黑名单且规则不包含 || 或 * 或 IP 地址，添加 || 前缀
        else:
            content += f"||{domain}^\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"{filename} 更新完成")

def main():
    """主函数"""
    print("开始更新广告拦截规则...")
    print("=" * 50)
    
    # 确保Ipurities目录存在
    if not os.path.exists("Ipurities"):
        os.makedirs("Ipurities")
    
    # 更新黑名单
    black_domains = update_impurities_file("Black with impurities.txt", BLACKLIST_SOURCES, "黑名单", is_whitelist=False)
    
    # 更新白名单
    white_domains = update_impurities_file("White with impurities.txt", WHITELIST_SOURCES, "白名单", is_whitelist=True)
    
    # 更新主文件
    update_main_file("Black.txt", black_domains, is_whitelist=False)
    update_main_file("White.txt", white_domains, is_whitelist=True)
    
    print("=" * 50)
    print("所有规则更新完成!")
    print(f"黑名单域名数: {len(black_domains)}")
    print(f"白名单域名数: {len(white_domains)}")

if __name__ == "__main__":
    main()
