import requests
import json

#url = "https://o3sky-sora2api.hf.space/v1/chat/completions"
url = "https://rendersora2api.duckcloud.fun/v1/chat/completions"

payload = json.dumps({
   "model": "sora2-portrait-15s",
   "messages": [
      {
         "role": "user",
         "content": """镜头跟随一辆白色复古SUV，它装有黑色车顶行李架，沿着一条陡峭的土路飞驰而上，两旁是陡峭山坡上的松树，轮胎扬起尘土。阳光洒在SUV上，为场景投射出温暖的光芒。土路缓缓蜿蜒向远处，看不到其他车辆。道路两侧的树木是红木，间或点缀着绿色植被。从后方可以看到汽车从容地跟随道路的弯曲，仿佛正在崎岖地驾车穿越险峻的地形。土路本身被陡峭的山坡和群山环绕，蓝天清澈，飘着几丝薄云。"""
      }
   ],
   "stream": True
})
headers = {
   'Authorization': 'Bearer sk_xxx',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
###
##data: {"id": "chatcmpl-1767105219616", "object": "chat.completion.chunk", "created": 1767105219, "model": "sora", "choices": [{"index": 0, "delta": 
# {"content": "```html\n<video src='https://oscdn2.dyysy.com/MP4/s_6953e2c377bc819185440082d9683a45.mp4' controls></video>\n```",
#  "reasoning_content": null, "tool_calls": null}, "finish_reason": "STOP", "native_finish_reason": "STOP"}], 
# "usage": {"prompt_tokens": 0, "completion_tokens": 1, "total_tokens": 
#1}}
###