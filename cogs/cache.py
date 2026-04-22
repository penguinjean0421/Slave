import os
import json
import time
from discord.ext import commands, tasks

class CacheManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        base_path = os.path.dirname(os.path.abspath(__file__))
        # 모든 파일이 공유하는 캐시 파일 경로
        self.cache_file = os.path.join(base_path, "..", "tracking.json")
        
        if not self.clean_cache_task.is_running():
            self.clean_cache_task.start()

    def cog_unload(self):
        self.clean_cache_task.stop()

    @tasks.loop(minutes=10)
    async def clean_cache_task(self):
        """30분이 지난 캐시 데이터를 정리합니다."""
        if not os.path.exists(self.cache_file):
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            current_time = time.time()
            # 1800초(30분) 이내의 데이터만 남김
            new_data = {k: v for k, v in data.items() if current_time - v.get('timestamp', 0) < 1800}
            
            # 데이터에 변화가 있을 때만 저장 (불필요한 쓰기 방지)
            if len(data) != len(new_data):
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=4)
                print(f"🧹 캐시 정리 완료: {len(data) - len(new_data)}개의 항목 삭제됨.")
        except Exception as e:
            print(f"❌ 캐시 정리 중 오류 발생: {e}")

async def setup(bot):
    await bot.add_cog(CacheManager(bot))