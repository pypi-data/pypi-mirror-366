
'''
定时模块Schtasks:可以按照当天指定时间运行指定python代码
----
使用方法:\n
在指定时刻执行\n
```
from pywechat.Clock import scntasks
scntasks.create_task(taskname='定时任务',start_time='08:31:14',pyfile_path='python文件地址')
```
注:运行上述代码后,名为定时任务的schtask将会被添加到windows系统下的定时任务中,并在指定时刻运行传入的python文件内的代码\n
'''
import os
import sys
import re
import subprocess
from pywechat.Errors import TaskNotBuildError

class Schtasks():
    '''
    使用windows系统下的schtasks命令实现定时操作
    --
    '''
    @staticmethod
    def create_task(taskname:str,start_time:str,pyfile_path:str):
        '''
        创建一个Windows系统下的schtasks任务,该任务将在当天指定的start_time\n
        执行传入的python代码或python脚本,只运行,无返回值\n
        Args:
            taskname:\tschtasks命令名称
            start_ime:\t执行任务的时间
            pyfile_path:\tpython代码路径

        注意:pyfile_path与code二者有其一即可,若二者都传入,优先使用pyfile_path的py代码
        ----
        '''
        # 创建一个schtasks命令来创建计划任务
        command=f'{sys.executable} {pyfile_path}'
        schtasks_command = (
            f'schtasks /create /tn {taskname} '
            f'/tr "{command}" /sc ONCE /st {start_time} /f'
        )
        subprocess.run(schtasks_command,text=True,shell=True)

    @staticmethod
    def change_task(taskname:str,start_time:str,pyfile_path:str=None):
        '''
        通过taskname修改一个已经设定的windows系统下的schtasks任务\n
        Args:
            taskname:\t已经设定的schtasks任务的名称
            start_ime:\t修改后执行任务的时间
            pyfile_path:\t需要替换的py文件路径,如果需要替换就传入路径\n
                不需要替换那么只需要输入taskname与start_time
        '''
        tasks=Schtasks.get_all_created_tasks()
        if taskname in tasks.keys():
            if pyfile_path:
                command=f'{sys.executable} {pyfile_path}'
                schtasks_command= (
                    f'schtasks /change /tn {taskname} '
                    f'/tr "{command}" /st {start_time} '
                )
                subprocess.run(schtasks_command,text=True,input='\n')
            else:
                schtasks_command=(
                    f'schtasks /change /tn {taskname} /st {start_time} '
                )
                subprocess.run(schtasks_command,text=True,input='\n')
        else:
            raise TaskNotBuildError(f'你还未创建过名为{taskname}的定时任务！')
        
    @staticmethod
    def cancel_task(taskname):
        '''
        通过已经设定的schtasks的taskname取消该任务\n

        Args:
            taskname:\t已经设定的schtasks任务的名称
        
        '''
        schtasks_command=(f'schtasks /delete /tn {taskname} /f')
        pyfile_path=os.path.abspath(os.path.join(os.getcwd(),'exec.py'))
        tasks=Schtasks.get_all_created_tasks()
        if taskname in tasks.keys():
            if os.path.exists(pyfile_path):
                os.remove(pyfile_path)
            subprocess.run(schtasks_command)
        else:
            raise TaskNotBuildError(f'你还未创建过名为{taskname}的定时任务！')
    @staticmethod
    def get_all_created_tasks()->dict:
        '''
        获取所有已建立的schtasks任务名称与时间\n
        返回值为任务名称与执行时间构成的字典\n
        '''
        schtasks_command='schtasks /query /v /fo list'
        process=subprocess.run(schtasks_command,stdout=subprocess.PIPE,encoding='gbk')
        result=process.stdout
        tasknames=re.findall(r'任务名:(.*?)(\n|$)',result)
        tasknames=[name[0].strip() for name in tasknames]
        tasknames=[name.replace('\\','') for name in tasknames]
        start_times=re.findall(r'开始时间:(.*?)(\n|$)',result)
        start_times=[name[0].strip() for name in start_times]
        start_times=[name.replace('\\','') for name in start_times]
        tasks=dict(zip(tasknames,start_times))
        return tasks