import subprocess
import os
import time
from typing import Optional
import sys
from typing import List, Optional
from base.log import log_util

class GitOperator:

    def __init__(self, repo_path: str):
        self.logger = log_util.BccacheLogger(
            name="Gitlog",
            use_console=True
        )      
        if not os.path.isdir(repo_path):
            self.logger.error(f"指定的仓库路径不存在或不是一个目录: {repo_path}")
            raise FileNotFoundError(f"指定的仓库路径不存在或不是一个目录: {repo_path}")
        self.repo_path = repo_path
        if not os.path.isdir(os.path.join(repo_path, '.git')):
             self.logger.warning(f"目录 '{repo_path}' 可能不是一个Git仓库的根目录。")
        

    def _run_command(self, command_args: list) -> Optional[str]:
        """
        在仓库路径下执行一个Git命令并返回其标准输出。

        Args:
            command_args (list): 要执行的命令参数列表 (例如 ['rev-parse', 'HEAD']).

        Returns:
            str | None: 命令成功时的输出 (已去除首尾空白)，失败则返回 None。
        """
        try:
            command = ['git'] + command_args
            self.logger.info(f"正在执行 Git 命令: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.stdout.strip()
        except FileNotFoundError:
            self.logger.error(f"'git' command not found. Is Git installed and in your PATH?")
            return None
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip()
            self.logger.error(f"在 '{self.repo_path}' 执行命令失败: {' '.join(e.cmd)}")
            self.logger.error(f"Git 错误: {e.stderr.strip()}")
            return None

    def initialize_repo(self) -> bool:
        """
        初始化一个 Git 仓库（执行 git init 命令）。
        
        Returns:
            bool: 如果初始化成功，返回 True；否则返回 False。
        """
        result = self._run_command(['init'])
        if result:
         self.logger.info(f"Git 仓库初始化成功，路径: {self.repo_path}")
        else:
         self.logger.error(f"Git 仓库初始化失败，路径: {self.repo_path}")
        return result is not None

    def add_remote(self, remote_url: str) -> bool:#这里返回值判断成功与否可能会有问题
        """
        添加远程仓库地址（执行 git remote add origin <url> 命令）。
        
        Args:
            remote_url (str): 远程仓库的 URL。
        
        Returns:
            bool: 如果成功添加远程仓库，返回 True；否则返回 False。
        """
        cmd = ['remote', 'add', 'origin', remote_url]
        try:
            self.logger.info(f"正在为仓库 '{self.repo_path}' 添加远程仓库: {remote_url}")
            result = self._run_command(cmd)
            if result is not None:
                self.logger.info(f"成功为仓库 '{self.repo_path}' 添加远程仓库：{remote_url}")
                return True
            else:
                self.logger.error(f"无法为仓库 '{self.repo_path}' 添加远程仓库：{remote_url}")
                return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 执行命令时出错: {' '.join(e.cmd)}")
            return False

    def get_current_commit(self) -> str:
        """获取当前 HEAD 的完整 commit hash。"""
        commit = self._run_command(['rev-parse', 'HEAD'])
        if commit:
         self.logger.info(f"仓库 '{self.repo_path}' 当前 HEAD commit hash: {commit}")
        else:
         self.logger.error(f"无法获取仓库 '{self.repo_path}' 的当前 HEAD commit hash")
        return commit or "" 

    def get_current_branch(self) -> str:
        

        """
        获取当前的 git 分支名。
        如果处于 'detached HEAD' 状态，会尝试返回一个有用的标识。
        """
        self.logger.info(f"正在获取仓库 '{self.repo_path}' 的当前分支信息...")
        branch = self._run_command(['symbolic-ref', '--short', 'HEAD'])
        if branch is None:
            tag = self._run_command(['describe', '--tags', '--exact-match'])
            if tag:
                self.logger.info(f"仓库 '{self.repo_path}' 当前处于标签: {tag}")
                return tag
            short_commit = self._run_command(['rev-parse', '--short', 'HEAD'])
            return f"HEAD@{short_commit}" if short_commit else "HEAD (detached)"
        else:
         self.logger.info(f"仓库 '{self.repo_path}' 当前分支: {branch}") 
        return branch or "" 
    
    def fetch(self, remote: str = 'origin') -> bool:
        """
        拉取远程仓库的更新（执行 git fetch 命令）。
        
        Args:
            remote (str): 要拉取的远程仓库，默认为 'origin'。
        
        Returns:
            bool: 如果拉取成功，返回 True；否则返回 False。
        """
        cmd = ['fetch', remote]
        result = self._run_command(cmd)
        return result is not None

    def pull(self, remote: str = 'origin', branch: str = 'master') -> bool:
        """
        拉取远程仓库的更新并合并（执行 git pull 命令）。
        
        Args:
            remote (str): 要拉取的远程仓库，默认为 'origin'。
            branch (str): 要拉取的分支，默认为 'master'。
        
        Returns:
            bool: 如果拉取并合并成功，返回 True；否则返回 False。
        """
        cmd = ['pull', remote, branch]
        result = self._run_command(cmd)
        return result is not None
    
    def check_branch_exists(self, branch: str) -> bool:
        """
        检查指定的分支是否存在。

        Args:
            branch (str): 要检查的分支名称。
        
        Returns:
            bool: 如果分支存在，返回 True；否则返回 False。
        """
        try:
            cmd = ['rev-parse', f'origin/{branch}^{{commit}}']
            result = self._run_command(cmd)
            return result is not None  # 如果成功，说明分支存在
        except Exception as e:
            print(f"[Error] 检查分支 '{branch}' 时发生异常: {e}")
            return False
        
    def checkout_branch(self, branch: str) -> bool:
        """
        切换到指定的分支。

        Args:
            branch (str): 要切换到的分支名称。
        
        Returns:
            bool: 如果切换成功，返回 True；否则返回 False。
        """
        try:
            self.logger.info(f"正在切换仓库 '{self.repo_path}' 到分支 '{branch}'...")
            cmd = ['checkout', branch]
            result = self._run_command(cmd)
            if result:
             self.logger.info(f"成功切换仓库 '{self.repo_path}' 到分支 '{branch}'")
             return True
            else:
             self.logger.error(f"无法切换仓库 '{self.repo_path}' 到分支 '{branch}'")
             return False
        except Exception as e:
            self.logger.exception(f"切换到分支 '{branch}' 时发生异常: {e}")
            return False
        
    def checkout_commit_f(self, commitid: str) -> bool:
        """
        强制切换到指定的提交。

        Args:
         commitid (str): 要切换到的提交 ID。
      
        Returns:
         bool: 如果切换成功，返回 True；否则返回 False。
        """
        try:
            self.logger.info(f"正在切换仓库 '{self.repo_path}' 到提交 '{commitid}'...")
            cmd = ['checkout', '-f', commitid]
            result = self._run_command(cmd)
            if result is not None:
              self.logger.info(f"成功切换仓库 '{self.repo_path}' 到提交 '{commitid}'")
              return True
            else:
              self.logger.error(f"无法切换仓库 '{self.repo_path}' 到提交 '{commitid}'")
              return False
        except Exception as e:
            self.logger.exception(f"切换到提交 '{commitid}' 时发生异常: {e}")
            return False

    def create_and_checkout_branch(self, branch: str, commitid: str) -> bool:
       """
        创建并切换到指定的新分支，并且基于某个特定的提交 ID。

        Args:
         branch (str): 要创建并切换到的新分支名称。
         commitid (str): 用于创建分支的提交 ID。
    
        Returns:
         bool: 如果创建并切换成功，返回 True；否则返回 False。
       """
       try:
          self.logger.info(f"正在为仓库 '{self.repo_path}' 基于提交 {commitid} 创建并切换到分支: {branch}...")
          cmd = ['checkout', '-b', branch, commitid]
          result = self._run_command(cmd)
          if result is not None:
            self.logger.info(f"成功为仓库 '{self.repo_path}' 基于提交 {commitid} 创建并切换到分支: {branch}")
            return True
          else:
            self.logger.error(f"无法为仓库 '{self.repo_path}' 基于提交 {commitid} 创建并切换到分支: {branch}")
            return False
       except Exception as e:
          self.logger.exception(f"创建并切换到分支 '{branch}' 时发生异常，在仓库 '{self.repo_path}' 中: {e}")
          return False

        
    def delete_local_branch(self, branch: str) -> bool:
        """
        删除本地分支。

        Args:
            branch (str): 要删除的本地分支名称。
        
        Returns:
            bool: 如果删除成功，返回 True；否则返回 False。
        """
        try:
            self.logger.info(f"正在尝试删除仓库 '{self.repo_path}' 中的本地分支: {branch}")
            cmd = ['branch', '-D', branch]
            result = self._run_command(cmd)
            if result is not None:
              self.logger.info(f"成功删除仓库 '{self.repo_path}' 中的本地分支: {branch}")
              return True
            else:
              self.logger.error(f"无法删除仓库 '{self.repo_path}' 中的本地分支: {branch}")
              return False
        except Exception as e:
            self.logger.error(f"删除仓库 '{self.repo_path}' 中的本地分支 '{branch}' 时发生异常: {e}")
            return False
        
    def reset_hard(self) -> bool:
        """
        重置 Git 仓库到最新的提交（执行 git reset --hard 命令）。
        
        Returns:
            bool: 如果重置成功，返回 True；否则返回 False。
        """
        self.logger.info(f"正在仓库 '{self.repo_path}' 执行 git reset --hard 操作...")
        try:
            cmd = ['reset', '--hard']
            result = self._run_command(cmd)
            if result is not None: 
              self.logger.info(f"仓库 '{self.repo_path}' 成功执行 git reset --hard 操作")
              return True
            else:
              self.logger.error(f"仓库 '{self.repo_path}' 执行 git reset --hard 操作失败")
              return False
        except Exception as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 执行 git reset --hard 时发生异常: {e}")
            return False

    def clean_untracked_files(self, excludes: list = None) -> bool:
        """
        清理 Git 仓库中未跟踪的文件（执行 git clean -xdf 命令）。
        
        Args:
            excludes (list): 可选的排除文件或文件夹列表。
        
        Returns:
            bool: 如果清理成功，返回 True；否则返回 False。
        """
        try:
            cmd = ['clean', '-df']
            if excludes:
                for exclude in excludes:
                    cmd += ['-e', exclude]
            self.logger.info(f"正在仓库 '{self.repo_path}' 执行 {cmd} 操作...")
            result = self._run_command(cmd)       
            if result is not None:
             self.logger.info(f"仓库 '{self.repo_path}' 成功执行 git clean -df 操作")
             return True
            else:
             self.logger.error(f"仓库 '{self.repo_path}' 执行 git clean -df 操作失败")
             return False            
        except Exception as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 执行 git clean -df 时发生异常: {e}")
            return False
     
    def set_git_config(self, key: str, value: str) -> bool:
        """
        设置 Git 配置（执行 git config 命令）。
        
        Args:
            key (str): 配置项的键。
            value (str): 配置项的值。
        
        Returns:
            bool: 如果配置成功，返回 True；否则返回 False。
        """
        try:
            cmd = ['config', key, value]
            result = self._run_command(cmd)
            if result is not None:  
             self.logger.info(f"仓库 '{self.repo_path}' 成功设置 Git 配置: {key}={value}")
             return True
            else:
             self.logger.error(f"仓库 '{self.repo_path}' 设置 Git 配置失败: {key}={value}")
             return False      
        except Exception as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 执行 git config 时发生异常: {e}")
            return False
        
    def remove_lock_files(self) -> bool:
        """
        删除 Git 仓库中的所有 .lock 文件。
        
        Returns:
            bool: 如果删除成功，返回 True；否则返回 False。
        """
        self.logger.info(f"正在删除仓库 '{self.repo_path}' 中的所有 .lock 文件...")
        try:
            dot_git = os.path.join(self.repo_path, '.git')
            for root, dirs, files in os.walk(dot_git):
                for file in files:
                    if file.endswith('.lock'):
                        lock_file_path = os.path.join(root, file)
                        os.remove(lock_file_path)
                        self.logger.info(f"成功删除文件: {lock_file_path}")
            return True
        except Exception as e:
            self.logger.error(f"删除仓库 '{self.repo_path}' 中 .lock 文件时发生异常: {e}")
            return False
    #此处浅克隆默认拉取所有分支而非当前分支
    def shallow_clone(self, remote_url: str, depth: int = 1) -> bool:
        """
        执行浅克隆（使用 git fetch --depth=1 命令）。
        
        Args:
            remote_url (str): 远程仓库的 URL。
            depth (int): 克隆深度，默认为 1。
        
        Returns:
            bool: 如果成功浅克隆，返回 True；否则返回 False。
        """
        self.logger.info(f"正在仓库 '{self.repo_path}' 执行浅克隆操作，远程仓库: {remote_url}，深度: {depth}...")
        try:
            cmd = ['fetch', remote_url, '+refs/heads/*:refs/remotes/origin/*', '--depth', str(depth)]
            result = self._run_command(cmd)
            if result is not None:
             self.logger.info(f"仓库 '{self.repo_path}' 成功执行浅克隆操作，远程仓库: {remote_url}，深度: {depth}")
             return True
            else:
             self.logger.error(f"仓库 '{self.repo_path}' 执行浅克隆操作失败，远程仓库: {remote_url}，深度: {depth}")
             return False
        except Exception as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 执行浅克隆时发生异常，远程仓库: {remote_url}，深度: {depth}，错误信息: {e}")
            return False
    
    def get_commit_timestamp(self, commit: str = 'HEAD') -> int:
        """
        获取指定提交的时间戳（以秒为单位）。

        Args:
            commit (str): 提交标识（默认为 'HEAD'，即最新的提交）。

        Returns:
            int: 提交的时间戳（如果成功）；否则返回 0。
        """
        self.logger.info(f"正在获取仓库 '{self.repo_path}' 提交 '{commit}' 的时间戳...")
        try:
            # 使用 'git log' 命令获取提交的日期
            cmd = ['log', '--pretty=format:"%cd"', commit, '-1']
            content = self._run_command(cmd)

            if content:
                content = content.strip()
                index = content.rfind('+')
                if index > 0:
                    # 去掉时区信息，并转换为时间戳
                    content = content[:index].strip()
                    timestamp = int(time.mktime(time.strptime(content, "%a %b %d %H:%M:%S %Y")))
                    return timestamp
            self.logger.error(f"无法获取仓库 '{self.repo_path}' 提交 '{commit}' 的有效时间戳")
            return 0  # 如果没有获取到有效的日期，返回 0
        except Exception as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 获取提交 '{commit}' 的时间戳时发生异常: {e}")
            return 0
    
    def run_gc(self) -> bool:
        """
        执行 Git 的垃圾回收命令（git gc --prune=now --force）。

        Returns:
            bool: 如果命令执行成功，返回 True；否则返回 False。
        """
        self.logger.info(f"正在仓库 '{self.repo_path}' 执行 Git 垃圾回收操作...")
        try:
            cmd = ['gc', '--prune=now', '--force']
            result = self._run_command(cmd)
            if result is not None:
             self.logger.info(f"仓库 '{self.repo_path}' 成功执行 git gc --prune=now --force 操作")
             return True
            else:
             self.logger.error(f"仓库 '{self.repo_path}' 执行 git gc --prune=now --force 操作失败")
        except Exception as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 执行 git gc 时发生异常: {e}")
            return False
        
    def prune_remote(self, remote: str = 'origin') -> bool:
        """
        清理本地仓库中已删除的远程分支引用（执行 git remote prune origin 命令）。
        
        Args:
            remote (str): 要清理的远程仓库，默认为 'origin'。
        
        Returns:
            bool: 如果操作成功，返回 True；否则返回 False。
        """
        cmd = ['remote', 'prune', remote]
        result = self._run_command(cmd)
        if result is not None:
            self.logger.info(f"仓库 '{self.repo_path}' 成功清理远程分支引用: {remote}")
            return True
        else:
            self.logger.error(f"仓库 '{self.repo_path}' 清理远程分支引用失败: {remote}")
            return False
        
    #git lfs操作
    def lfs_pull(self) -> bool:
        """
        执行 git lfs pull 操作，拉取大文件。
        
        Returns:
            bool: 如果成功执行 git lfs pull，返回 True；否则返回 False。
        """
        self.logger.info(f"正在仓库 '{self.repo_path}' 执行 git lfs pull 操作...")
        try:
            cmd = ['lfs', 'pull']
            result = self._run_command(cmd)
            if result is not None:
             self.logger.info(f"仓库 '{self.repo_path}' 成功拉取大文件。")
             return True
            else:
             self.logger.error(f"仓库 '{self.repo_path}' 拉取大文件失败。")
             return False
        except Exception as e:
            self.logger.error(f"在仓库 '{self.repo_path}' 执行 git lfs pull 时发生异常: {e}")
            return False
   
    def get_commits_lists(self, target_branch: str, feature_branch: str) -> Optional[List[str]]:
        """
        获取 feature_branch 相对于 target_branch 新增的所有提交(commit)列表。
        
        这个方法首先找到两个分支的共同祖先，然后列出从该祖先到 
        feature_branch 头部的所有提交，并按时间正序排列。

        Args:
            target_branch (str): 目标分支或基础分支 (例如 'main' 或 'develop')。
            feature_branch (str): 功能分支，需要找出其新增提交的分支。

        Returns:
            Optional[List[str]]: 如果成功，返回一个包含新增 commit 哈希值的列表。
                                 如果没有新增提交，则返回一个空列表。
                                 如果执行过程中发生错误，则返回 None。
        """
        self.logger.info(f"正在查找 '{feature_branch}' 相对于 '{target_branch}' 的新增提交...")
        ancestor_commit = self._run_command(['merge-base', target_branch, feature_branch])
        if not ancestor_commit:
            self.logger.error(f"无法找到 '{target_branch}' 和 '{feature_branch}' 的共同祖先。请确认分支名称是否正确并且存在于仓库中。")
            return None
        self.logger.info(f"找到的共同祖先 commit: {ancestor_commit}")
        self.logger.info(f"正在获取从 {ancestor_commit} 到 '{feature_branch}' 的提交列表...")
        commit_range = f"{ancestor_commit}..{feature_branch}"
        commit_list_str = self._run_command(['rev-list', '--reverse', commit_range])
        if commit_list_str is None:
            self.logger.error(f"执行 'git rev-list' 失败。无法获取提交列表。")
            return None
        if not commit_list_str:
            self.logger.info(f"'{feature_branch}' 相对于 '{target_branch}' 没有新的提交。")
            return []
        commits = commit_list_str.splitlines()
        self.logger.info(f"成功获取了 {len(commits)} 个新增提交。")
        return commits
    
    def get_git_version(self) -> str:
        """
        获取当前 Git 版本。
        
        Returns:
            str: 当前 Git 的版本号。
        """
        try:
            # 使用 'git --version' 命令来获取 Git 版本
            version = self._run_command(['--version'])
            if version:
                self.logger.info(f"当前 Git 版本: {version}")
                return version
            else:
                self.logger.error(f"无法获取 Git 版本信息")
                return ""
        except Exception as e:
            self.logger.error(f"获取 Git 版本时发生异常: {e}")
            return ""
    