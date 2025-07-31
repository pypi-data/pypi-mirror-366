import os
import time
from typing import List
from tqdm import tqdm
from threading import Thread
from dataset_up.client import Client
from dataset_up.uploader.uploaded_file import UploadingFile
from dataset_up.utils.system_utils import caculate_upload_worker_num 
from dataset_up.utils.file import list_files_in_folder
from dataset_up.uploader.upload_context import parse_filelist_to_tasklist,upload_files
from dataset_up.utils.concurrent_utils import error_event,interrupt_event
from dataset_up.uploader.upload_context import update_lock



class  Uploader(object):
    def __init__(self, client: Client,dataset_id: str, version: str,worker_num: int = None):
        self.client = client
        self.task_id = None
        self.dataset_id = dataset_id
        self.version = version
        self.worker_num = caculate_upload_worker_num() if worker_num is None else worker_num    
        
    def upload_file(self, source_path: str, destination_path: str):
        
        source_path = os.path.realpath(os.path.expanduser(source_path))
        
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"源路径不存在: {source_path}")
        if not os.path.isfile(source_path):
            raise NotADirectoryError(f"源路径不是一个文件: {source_path}")
        
        if not destination_path:
            destination_path = "/"

        if not destination_path.endswith("/"):
            destination_path = destination_path + "/"
            
        self.create_task(is_dir=False)
        
        rel_path = os.path.basename(source_path)
        target_path = os.path.join(destination_path, rel_path)
        
        file = UploadingFile(client=self.client,
                                 abs_path=source_path,
                                 rel_path=rel_path,
                                 target_path=target_path,
                                 dataset_id=self.dataset_id,
                                 version=self.version)
        
        file_list = [file]
        task_list = []
        
        total_list_size = len(file_list)
            
        with tqdm(total=total_list_size, ncols=100, desc="Preparing", unit_scale=True) as progress:
            task_list = parse_filelist_to_tasklist(file_list,task_list ,self.dataset_id, self.version, progress, self.worker_num)
        
        begin_time = time.time()
        total_size = sum([file.size for file in file_list])
        uploaded_size = total_size - sum([task[2] for task in task_list])
        with tqdm(total=total_size,initial=uploaded_size, ncols=100, desc="Uploading", unit_scale=True) as progress:
            self.asyc_report(self.task_id,self.dataset_id,self.version,destination_path=target_path ,operate_type="UPLOAD",
                             exec_state="UPLOADING",is_dir=False,begin_time=begin_time,progress=progress)
            upload_files(task_list, progress, self.worker_num)
        
        self.report(self.task_id,self.dataset_id,self.version,operate_type="UPLOAD", exec_state="UPLOAD_COMPLETE", progress=1.0,file_size=progress.total,begin_time=begin_time,
                                    remaining_time=0,destination_path=target_path,is_dir=False,end_time=time.time())
        
        print(f"\nUpload file {source_path} completed\n")

        
    def upload_folder(self, source_path: str, destination_path: str):
        """
        上传指定的本地文件夹到目标路径。

        参数:
            source_path (str): 本地文件夹路径，支持 ~ 和相对路径。
            destination_path (str): 目标路径，若为空则使用根路径 '/'。
        """
        
        source_path = os.path.realpath(os.path.expanduser(source_path))
        
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"源路径不存在: {source_path}")
        if not os.path.isdir(source_path):
            raise NotADirectoryError(f"源路径不是一个目录: {source_path}")
        
    
        if not destination_path:
            destination_path = "/"

        if not destination_path.endswith("/"):
            destination_path = destination_path + "/"
            
        self.create_task(is_dir=True)
            
        file_list = []
        task_list = []
        
        file_list.extend(self.get_files_to_upload(source_path,destination_path))
        # 倒序遍历删除（避免索引问题）
        for i in range(len(file_list) - 1, -1, -1):
            if file_list[i].size == 0:
                print("file size is 0, skip: " + file_list[i].abs_path)
                del file_list[i]
        
        total_size = sum([file.size for file in file_list])
        
        total_list_size = len(file_list)
            
        with tqdm(total=total_list_size, ncols=100, desc="Preparing", unit_scale=True) as progress:
            task_list = parse_filelist_to_tasklist(file_list,task_list ,self.dataset_id, self.version, progress, self.worker_num)
        
        begin_time = time.time()
        uploaded_size = total_size - sum([task[2] for task in task_list])
        with tqdm(total=total_size,initial=uploaded_size, ncols=100, desc="Uploading", unit_scale=True) as progress:
            self.asyc_report(self.task_id,self.dataset_id,self.version,destination_path=destination_path ,operate_type="UPLOAD",
                             exec_state="UPLOADING",is_dir=True,begin_time=begin_time,progress=progress)
            upload_files(task_list, progress, self.worker_num)
        
        self.report(self.task_id,self.dataset_id,self.version,operate_type="UPLOAD", exec_state="UPLOAD_COMPLETE", progress=1.0,file_size=progress.total,begin_time=begin_time,
                                    remaining_time=0,destination_path=destination_path,is_dir=True,end_time=time.time())
        
        print(f"\nUpload folder {source_path} completed\n")
    
    
    def get_files_to_upload(self,source_path,destination_path) -> List[UploadingFile]:
        file_list = []
        for file_path in list_files_in_folder(source_path):
            rel_path = os.path.relpath(file_path, source_path).replace("\\", "/")
            target_path = os.path.join(destination_path, rel_path)
            file = UploadingFile(client=self.client,
                                 abs_path=file_path,
                                 rel_path=rel_path,
                                 target_path=target_path,
                                 dataset_id=self.dataset_id,
                                 version=self.version)
            file_list.append(file)
        return file_list
    

    def report(self,task_id,dataset_id,version,operate_type,exec_state,progress,file_size,begin_time,remaining_time,destination_path,is_dir,end_time = None):
        req = {
            "taskId": task_id,
            "datasetId": dataset_id,
            "version": version,
            "filePath": destination_path,
            "operateType": operate_type,
            "execState": exec_state,
            "progress": progress,
            "fileSize": file_size,
            "beginTime": begin_time,
            "endTime" : end_time,
            "remainingTime": remaining_time,
            "isDir": is_dir
        }
        self.client.report(req)
        
    def asyc_report(self,task_id,dataset_id,version,destination_path,operate_type,exec_state,is_dir,begin_time,progress: tqdm):
        def report_progress():
                while not error_event.is_set() and not interrupt_event.is_set():
                    if progress.n < progress.total:
                        progress_ratio = 0
                        remaining_time = 0
                        with update_lock:
                                processed_bytes = progress.n
                                elapsed_time = time.time() - begin_time
                                if elapsed_time <= 0:
                                    continue
                                speed = processed_bytes / elapsed_time
                                if speed <= 0:
                                    continue
                                remaining_time = (progress.total - processed_bytes) / speed
                                progress_ratio = processed_bytes / progress.total
                        
                        try:
                                self.report(task_id,dataset_id,version,operate_type=operate_type, exec_state=exec_state, progress=progress_ratio,file_size=progress.total,begin_time=begin_time,
                                remaining_time=remaining_time,destination_path=destination_path,is_dir=is_dir,end_time=None)
                        except Exception as e:
                                print(f"Error occurred while reporting progress: {e}")
                        
                    else:
                        return
                    time.sleep(5)  # 每隔 5 秒汇报一次
        reporter_thread = Thread(target=report_progress, daemon=True)
        reporter_thread.setDaemon(True)
        reporter_thread.start()
    
    
    def list(self,dir ="/"):
        if dir == "":
            dir = "/"
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "filePath": dir
        }
        ret = self.client.list(req)
        objects = ret["objects"]
        return objects
        
    
    def mkdir(self,dir):
        if dir is None or str(dir).strip() == "":
            raise Exception("dir cannot be empty")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "dir": dir
        }
        ret = self.client.mkdir(req)
        dir_key = ret["dirKey"]
        result = ret["result"]
        message = ret["message"]
        if result:
            print(f"Create directory {dir} successfully")
        else:
            print(f"Failed to create directory {dir}, message: {message}")
            
    def deleteDir(self,dir):
        if dir is None or str(dir).strip() == "":
            raise Exception("dir cannot be empty")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "dir": dir
        }
        ret = self.client.deleteDir(req)
        dir = ret["dir"]
        result = ret["result"]
        message = ret["message"]
        if result:
            print(f"Delete directory {dir} successfully")
        else:
            print(f"Failed to delete directory {dir}, message: {message}")
        
    
    def deleteFile(self,file):
        if file is None or str(file).strip() == "":
            raise Exception("file cannot be empty")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "filePath": file
        }
        ret = self.client.deleteFile(req)
        key = ret["key"]
        result = ret["result"]
        dataset_id = ret["datasetId"]
        version = ret["version"]
        if result:
            print(f"Delete file {file} successfully")
        else:
            print(f"Failed to delete file {file}")
            
    def create_task(self,is_dir: bool):
        if is_dir is None:
            raise Exception("is_dir is required")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "isDir": is_dir
        }
        ret = self.client.create_task(req)
        success = ret["success"]
        if not success:
            message = ret["message"]
            raise Exception(f"create upload task failed , message:{message}")                
        self.task_id = ret["taskId"]
        if self.task_id != None and self.task_id != "":
            print("create task success,taskId: %s" % self.task_id)
        else:
            raise Exception("create task failed")
        
        
        
    
