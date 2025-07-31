import hashlib
import requests
import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time

LOCALE_DIR = "./data/downloaded_reports"  # 本地保存目录


class OSSDirectoryDownloader:
    def __init__(self, host, sk, ak, data_name, data_type):
        self.host = host  # 服务器地址
        self.sk = sk
        self.ak = ak
        self.data_name = data_name
        self.data_type = data_type

    def make_user_headers(self):
        data_str = self.sk + self.ak
        data = data_str.encode("utf-8")
        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        authorization = hash_obj.hexdigest()
        headers = {
            "Authorization": authorization,
            "Source": self.ak,
        }
        return headers

    def list_oss_files(self):
        """列举OSS目录下的所有文件（处理分页）"""
        response = requests.post(
            f"{self.host}/v1/api/load_file/list_oss_file",
            headers=self.make_user_headers(),
            json={
                "data_name": self.data_name,
                "data_type": self.data_type,
            },
        )
        if response.status_code != 200:
            raise Exception(f"list_oss_files {response.text}")

        res_data = response.json().get("data")
        return res_data

    def oss_file_load(self, oss_path):
        """列举OSS目录下的所有文件（处理分页）"""
        # 用临时密钥初始化OSS客户端
        response = requests.post(
            f"{self.host}/v1/api/load_file/oss_file_load_url",
            headers=self.make_user_headers(),
            json={
                "data_name": self.data_name,
                "data_type": self.data_type,
                "oss_path": oss_path,
            },
        )
        if response.status_code != 200:
            raise Exception(f"获取文件列表失败：{response.text}")

        res_data = response.json().get("data")
        if res_data is None:
            return res_data
        return res_data.get("file_url")

    def download_from_oss(self, oss_path, local_path, chunk_size=1024, retries=3):
        # 检查是否有部分下载的文件
        temp_path = local_path + ".temp"
        completed_size = 0

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        if os.path.exists(temp_path):
            # 获取已下载的部分大小
            completed_size = os.path.getsize(temp_path)
            print(f"发现部分下载文件，大小: {completed_size/1024/1024:.2f} MB")

        if os.path.exists(temp_path):
            completed_size = os.path.getsize(temp_path)
            print(f"发现部分下载文件，大小: {completed_size/1024/1024:.2f} MB")

        headers = {}
        if completed_size > 0:
            headers["Range"] = f"bytes={completed_size}-"

        url = self.oss_file_load(oss_path)
        if url is None:
            print(f"获取下载失败: {oss_path}")
            return
        for attempt in range(retries):
            try:
                with requests.get(
                    url, headers=headers, stream=True, timeout=30
                ) as response:
                    response.raise_for_status()

                    # 获取文件总大小
                    total_size = int(response.headers.get("content-length", 0))
                    if completed_size > 0:
                        total_size += completed_size

                    print(f"开始下载，文件大小: {total_size/1024/1024:.2f} MB")

                    # 下载文件
                    with open(
                        temp_path, "ab" if completed_size > 0 else "wb"
                    ) as f, tqdm(
                        desc=os.path.basename(local_path),
                        total=total_size,
                        initial=completed_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))

                    # 下载完成后重命名文件
                    os.replace(temp_path, local_path)
                    print(f"下载完成: {local_path}")
                    return True

            except Exception as e:
                wait_time = (attempt + 1) * 2
                print(f"下载失败 ({attempt+1}/{retries}): {str(e)}")
                print(f"将在 {wait_time} 秒后重试...")
                time.sleep(wait_time)

        print("下载失败，已达到最大重试次数")
        return False

    def download_directory(self):
        """下载整个OSS目录（并发下载多文件）"""
        # 1. 列举目录所有文件
        res_data = self.list_oss_files()
        if not res_data:
            print("目录为空，无需下载")
            return
        # 2. 并发下载（根据CPU核心数设置线程数）
        with ThreadPoolExecutor(max_workers=8) as executor:
            for single_data in res_data:
                # 本地路径：保持OSS目录结构
                oss_file = single_data.get("file_path")
                oss_dir = single_data.get("file_name")
                relative_path = os.path.relpath(single_data.get("file_path"), oss_dir)
                local_path = os.path.join(LOCALE_DIR, relative_path)
                print(f"准备下载{oss_file}到{local_path},relative_path:{relative_path}")
                # 提交下载任务
                executor.submit(self.download_from_oss, oss_file, local_path)
        print("所有文件下载完成")


if __name__ == "__main__":
    api_ak = "533d3041-1e89-4569-a8f1-ba3463251a4e"
    api_sk = "0a49d25922c0f4eef4fda69afa194d1380da73389e194cc149f4b3d0178cd5a2"
    data_set_name = "zhihu_answer_step_3"
    host = "http://127.0.0.1:8060"
    data_type = "dataset"  # 或 "book", "patent" 等

    downloader = OSSDirectoryDownloader(
        host=host,
        ak=api_ak,
        sk=api_sk,
        data_name=data_set_name,
        data_type=data_type,
    )

    downloader.download_directory()
