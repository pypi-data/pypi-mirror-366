from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from shiyunzi.utils.models import Work, Task, RunwayAccount
from shiyunzi.utils.log_util import get_logger
from shiyunzi.utils.account_util import available_runway_endpoint
from shiyunzi.llm.text2text_util import chat_with_llm, ImagePrompt, doubao_chat_with_llm
import time
from runwayapi import login, generate_image, get_user_team_id, create_session, get_image_task_detail, get_video_task_detail, get_sessions, upload_image, generate_video_for_gen4, generate_video_for_gen3a, delete_other_task
from shiyunzi.llm.image2text import image2text_prompt, VideoPrompt, doubao_image2text_prompt
from shiyunzi.utils.download_util import download_image, download_video
from shiyunzi.utils.path_util import get_task_image_dir, get_task_video_dir, get_task_no_music_dir
from shiyunzi.utils.music_util import add_audio_to_video
from shiyunzi.llm.stable_diffusion_text2image import stable_deffusion_txt2img
from shiyunzi.utils.config_util import get_config, set_config
from shiyunzi.doubao.doubao_service import chat_completion, upload_file, delete_conversation
from shiyunzi.llm.doubao_util import doubao_image_generate
from PIL import Image
import os
import random

logger = get_logger(__name__)

class TaskService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.t2t_futures = []
        self.t2i_futures = []
        self.i2v_futures = []
        self.download_futures = []
        self.runway_task_id_list = []

    def t2t_task(self, work: Work):
        try:
            logger.info(f"开始处理T2T任务,work_id:{work.id}")
            
            work.task.status = "running"
            work.task.save()

            work.status = "running" 
            work.save()

            if get_config("llm_model") == "doubao":
                text = doubao_chat_with_llm(work.task.text2image, work.super_prompt, return_json=True)
            else:
                text = chat_with_llm(work.task.text2image, work.super_prompt, return_json=True)

            if text == "FAILED":
                work.status = "completed"
                work.save()
                return

            image_prompt = ImagePrompt(**text)
            work.text2image_prompt = image_prompt.image_prompt_Y
            work.text2image_negative_prompt = image_prompt.image_prompt_N
            work.save()
            logger.info(f"保存生成的提示词,work_id:{work.id}")

        except Exception as e:
            logger.error(f"T2T任务执行失败: {e}")
        finally:
            work.status = "pending"
            work.save()

    def t2i_task(self, work: Work):
        try:
            logger.info(f"开始处理T2I任务,work_id:{work.id}")
            
            work.task.status = "running"
            work.task.save()

            work.status = "running" 
            work.save()

            if work.task.text2image == "sd":
                logger.info(f"使用stable_diffusion模型生成图片,work_id:{work.id}")
                image_url = stable_deffusion_txt2img(work)
                if image_url is None:
                    logger.error(f"stable_diffusion模型生成图片失败,work_id:{work.id}")
                    return
                work.image_path = image_url
                work.save()
            elif work.task.text2image == "runway":
                logger.info(f"使用runway模型生成图片,work_id:{work.id}")
                with available_runway_endpoint() as runway:
                    if runway is None:
                        return
                    session_id = get_sessions(runway.token, runway.team_id)[0]["id"]
                    task_id = generate_image(
                        token=runway.token,
                        team_id=runway.team_id,
                        session_id=session_id,
                        prompt=work.text2image_prompt,
                        resolution=work.task.resolution,
                        num_images=1
                    )
                    if task_id == "FAILED":
                        work.status = "completed"
                        work.save()
                        raise Exception(f"图片生成失败,work_id:{work.id},任务终止")
                    self.runway_task_id_list.append(task_id)
                    images = get_image_task_detail(runway.token, runway.team_id, task_id)
                    
                    if images is None:
                         work.status = "completed"
                         work.save()
                         raise Exception(f"图片生成失败,work_id:{work.id},任务终止, 可能出现违禁词")
                    if images == "FAILED":
                        work.status = "completed"
                        work.save()
                        raise Exception(f"图片生成失败,work_id:{work.id},任务失败,Runway禁止生成,该任务终止")
                    if images == "CANCELLED":
                        raise Exception(f"任务被取消,work_id:{work.id},可以在设置模式开启变态模式")
                    image_dir = get_task_image_dir(work.task.id)
                    # 下载图片到本地
                    save_path = f"{image_dir}/{work.id}.png"
                    download_image(images[0], save_path)
                    work.image_path = images[0]
                    work.save()
            elif work.task.text2image == "doubao":
                image_url = doubao_image_generate(work.super_prompt, work.task.resolution)
                if image_url is None:
                    logger.error(f"豆包模型生成图片失败,work_id:{work.id}")
                    return
                image_dir = get_task_image_dir(work.task.id)
                # 下载图片到本地
                save_path = f"{image_dir}/{work.id}.png"
                download_image(image_url, save_path)
                work.image_path = save_path
                work.save()
            if work.task.type == "text2image":
                work.status = "completed"
                work.save()
                work.task.status = "completed"
                work.task.save()
                return

        except Exception as e:
            logger.error(f"T2I任务执行失败: {e}")
        finally:
            if work.status == "running":
                work.status = "pending"
                work.save()

    def i2v_task(self, work: Work):
        try:
            logger.info(f"开始处理I2V任务,work_id:{work.id}")
            
            work.task.status = "running"
            work.task.save()

            work.status = "running" 
            work.save()

            image_path = work.image_path
            width = 0
            height = 0

            # 下载图片到本地
            if work.image_path.startswith("http"):
                image_dir = get_task_image_dir(work.task.id)
                # 下载图片到本地
                save_path = f"{image_dir}/{work.id}.png"
                if not download_image(image_path, save_path):
                    raise Exception("图片下载失败")
                if not os.path.exists(save_path):
                    raise Exception("图片下载失败")
                image_path = save_path
            
            # 兜底
            if not os.path.exists(image_path):
                work.image_path = None
                work.status = "completed"
                work.save()
                return

            # 使用大模型通过图片解析提示词
            if work.image2video_prompt is None:
                if get_config("llm_model") == "doubao":
                    result = doubao_image2text_prompt(work.task.image2video, work.super_prompt, image_path, return_json=True)
                else:
                    result = image2text_prompt(work.task.image2video, work.super_prompt, image_path, return_json=True)
                if result == "FAILED":
                    work.status = "completed"
                    work.save()
                    return
                video_prompt = VideoPrompt(**result)
                work.image2video_prompt = video_prompt.video_prompt
                work.save()

            # 根据图片获取宽高
            image = Image.open(image_path)
            width = image.width
            height = image.height

            if work.task.image2video == "runway":
                with available_runway_endpoint() as runway:
                    if runway is None:
                        return
                    if not work.image_path.startswith("http"):
                        # 走上传
                        logger.info(f"上传图片到runway,work_id:{work.id}, image_path:{work.image_path}")
                        image_url = upload_image(runway.token, work.image_path)
                        if image_url is None:
                            raise Exception("图片上传失败")
                        work.image_path = image_url
                        work.save()

                    session_id = get_sessions(runway.token, runway.team_id)[0]["id"]

                    if get_config("runway_model") == "gen3":
                        task_id = generate_video_for_gen3a(
                            token=runway.token,
                            team_id=runway.team_id,
                            session_id=session_id,
                            image_url=work.image_path,
                            prompt=work.image2video_prompt,
                            second=work.second
                        )
                    else:
                        task_id = generate_video_for_gen4(
                            token=runway.token,
                            team_id=runway.team_id,
                            session_id=session_id,
                            image_url=work.image_path,
                            prompt=work.image2video_prompt,
                            second=work.second,
                            width=width,
                            height=height
                        )
                    if task_id == "FAILED":
                        work.status = "completed"
                        work.save()
                        raise Exception(f"视频生成失败,work_id:{work.id},任务终止")
                    self.runway_task_id_list.append(task_id)
                    video = get_video_task_detail(runway.token, runway.team_id, task_id)
                    logger.info(f"视频生成成功,work_id:{work.id}, video_path:{video}")
                    if video is None:
                        work.status = "completed"
                        work.save()
                        raise Exception(f"视频生成失败,work_id:{work.id},任务终止, 可能出现违禁词")
                    if video == "FAILED":
                        work.status = "completed"
                        work.save()
                    if video == "CANCELLED":
                        raise Exception(f"任务被取消,work_id:{work.id},可以在设置模式开启变态模式")
                    work.video_path = video
                    work.save()
        except Exception as e:
            logger.error(f"I2V任务执行失败: {e}")
        finally:
            if work.status == "running":
                work.status = "pending"
                work.save()
    
    def download_task(self, work: Work):  
        try:
            logger.info(f"开始处理下载任务,work_id:{work.id}")

            work.task.status = "running"
            work.task.save()

            work.status = "running" 
            work.save()

            no_music_dir = get_task_no_music_dir(work.task.id)
            no_music_path = f"{no_music_dir}/{work.id}.mp4"
            if not download_video(work.video_path, no_music_path):
                return
            logger.info(f"下载视频成功,work_id:{work.id}, video_path:{no_music_path}")
            if work.task.music_dir != "" and work.task.music_dir is not None:
                music_dir = get_task_video_dir(work.task.id)
                # 从音乐文件夹随机获取一个mp3文件路径
                music_path = random.choice(os.listdir(work.task.music_dir))
                music_path = os.path.join(work.task.music_dir, music_path)
                add_audio_to_video(no_music_path, music_path, music_dir)
                
            work.status = "completed"
            work.save()

            pending_count = Work.select().where(Work.task == work.task, Work.status == "running" | Work.status == "pending").count()
            if pending_count == 0:
                work.task.status = "completed"
                work.task.save()
            
        except Exception as e:
            logger.error(f"下载任务执行失败: {e}")
        finally:
            if work.status == "running":
                work.status = "pending"
                work.save()

    def setup(self):
        while True:
            logger.info("处理中任务:")
            logger.info(f"t2t_futures: {len(self.t2t_futures)}")
            logger.info(f"t2i_futures: {len(self.t2i_futures)}")
            logger.info(f"i2v_futures: {len(self.i2v_futures)}")
            logger.info(f"download_futures: {len(self.download_futures)}")

            # 计算Runway账号最大使用数量
            shared_runway_account_count = RunwayAccount.select().where(RunwayAccount.type == "shared").count()
            exclusive_runway_account_count = RunwayAccount.select().where(RunwayAccount.type == "exclusive").count()
            max_count = shared_runway_account_count * 2 + exclusive_runway_account_count

            # 清除已经完成T2T任务
            done, not_done = wait(
                self.t2t_futures, timeout=1, return_when=FIRST_COMPLETED
            )
            self.t2t_futures = list(not_done)

            # 查询T2T任务
            while len(self.t2t_futures) < 1:
                try:
                    # 计算提示词任务超前数量
                    t2t_ahead = Work.select().join(Task).where(
                        (Task.type == "text2video") | (Task.type == "text2image"), 
                        Work.status == "pending",
                        Work.text2image_prompt != None
                    ).count()
                    
                    logger.info(f"当前提示词任务超前数量: {t2t_ahead}")

                    if t2t_ahead >= 5:
                        break

                    # 启动一个T2T任务
                    work = Work.select().join(Task).where(
                        (Task.type == "text2video") | (Task.type == "text2image"), 
                        Work.status == "pending",
                        Work.text2image_prompt.is_null()
                    ).first()
                    
                    if work is not None:
                        logger.info(f"启动新的T2T任务, work_id: {work.id}")
                        future = self.executor.submit(self.t2t_task, work)
                        self.t2t_futures.append(future)
                        time.sleep(1)
                    else:
                        break
                except Exception as e:
                    logger.error(f"T2T任务启动失败: {e}")
                    time.sleep(1)

            done, not_done = wait(
                self.i2v_futures, timeout=1, return_when=FIRST_COMPLETED
            )
            self.i2v_futures = list(not_done)

            # 查询I2V任务
            while len(self.i2v_futures) < max_count:
                try:
                    work = Work.select().join(Task).where(
                        (Task.type == "image2video") | (Task.type == "text2video"), 
                        Work.status == "pending",
                        Work.image_path != None,
                        Work.video_path.is_null()
                    ).first()

                    if work is not None:
                        future = self.executor.submit(self.i2v_task, work)
                        self.i2v_futures.append(future)
                        time.sleep(1)
                    else:
                        break

                except Exception as e:
                    logger.error(f"I2V任务启动失败: {e}")
                    time.sleep(1)

            done, not_done = wait(
                self.t2i_futures, timeout=1, return_when=FIRST_COMPLETED
            )
            self.t2i_futures = list(not_done)

            # 查询T2I任务
            while len(self.t2i_futures) < max_count:
                try:
                    # 查询文生图使用什么模型
                    work = Work.select().join(Task).where(
                        (Task.type == "text2video") | (Task.type == "text2image"), 
                        Work.status == "pending",
                        Work.text2image_prompt != None,
                        Work.image_path == None
                    ).first()

                    if work is not None:
                        future = self.executor.submit(self.t2i_task, work)
                        self.t2i_futures.append(future)
                        time.sleep(1)
                    else:
                        break
                except Exception as e:
                    logger.error(f"T2I任务启动失败: {e}")
                    time.sleep(1)

            
            done, not_done = wait(
                self.download_futures, timeout=1, return_when=FIRST_COMPLETED
            )
            self.download_futures = list(not_done)

            while len(self.download_futures) < 1:
                try:
                    work = Work.select().join(Task).where(
                        (Task.type == "image2video") | (Task.type == "text2video"), 
                        Work.status == "pending",
                        Work.video_path != None
                    ).first()

                    if work is not None:
                        future = self.executor.submit(self.download_task, work)
                        self.download_futures.append(future)
                        time.sleep(1)
                    else:
                        break
                except Exception as e:
                    logger.error(f"下载任务启动失败: {e}")
                    time.sleep(1)
            # 判断账号是否失效
            runway_accounts = RunwayAccount.select().where(RunwayAccount.status == 0)
            for runway_account in runway_accounts:
                retry_count = 0
                max_retries = 3
                while retry_count < max_retries:
                    user_id = get_user_team_id(runway_account.token)
                    if user_id is None or user_id != 401:
                        break
                    if retry_count == max_retries:
                        runway_account.status = 1
                        runway_account.save()
                        break
                    retry_count += 1
                    time.sleep(5)

            if get_config("pervert_mode") == "1":
                # 查找状态为正常并且是共享的账号
                runway_accounts = RunwayAccount.select().where(RunwayAccount.status == 0, RunwayAccount.type == "shared")
                for runway_account in runway_accounts:
                    delete_other_task(runway_account.token, runway_account.team_id, self.runway_task_id_list)
            time.sleep(5)

def reset_task_status():
    RunwayAccount.update(used=0).where(RunwayAccount.status == 0).execute()
    Work.update(status="pending").where(Work.status == "running").execute()
    
def kickoff():
    reset_task_status()
    service = TaskService()
    import threading
    threading.Thread(target=service.setup).start()