import http.client
import json
import time

# 配置信息
API_HOST = "api.jxincm.cn"
AUTH_TOKEN = "sk-xxx"
HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json'
}

def create_video():
    """创建视频生成任务"""
    conn = http.client.HTTPSConnection(API_HOST)
    payload = json.dumps({
        "images": [],
        "model": "sora-2",
        "orientation": "portrait",
        "prompt": """### Style
* **Visual Texture:** AI-generated photorealistic aesthetic. The surfaces appear unnaturally smooth and highly detailed, with a digital crispness typical of high-end neural video generation. The "smoke" or steam is a prominent digital overlay that flows with fluid-like density.
* **Lighting Quality:** Dramatic and high-contrast. The first scene uses warm, diffused cafe lighting; the second uses cool, overhead gym lighting; the third uses focused studio rim lighting to highlight the metallic textures of the mug.
* **Color Palette:** A bold "Engine Red" dominates the coffee mug, contrasted against deep espresso browns, metallic silver accents, and warm wood tones.
* **Atmosphere:** Energetic and commercial. It blends a "manly" blue-collar aesthetic with quirky, high-octane enthusiasm.

### Cinematography
* **Camera:** A mix of medium shots and macro close-ups. The final shot uses a handheld-style movement as the mug is picked up and rotated to showcase the 360-degree detail.
* **Lens:** Shallow depth of field throughout. The backgrounds (cafe, gym, table) are softly blurred (bokeh) to keep the viewer’s focus entirely on the V8 engine mug.
* **Lighting:** Professional-grade "product photography" lighting. Highlights are placed strategically on the metallic "exhaust pipes" and the "V8" logo to create a sense of premium material quality.
* **Mood:** Enthusiastic, viral, and hyper-masculine.

---

### Scene Breakdown

**Scene 1 (00:00s - 00:04s):**
A middle-aged man with a thick beard, wearing a charcoal Carhartt t-shirt, stands in a rustic cafe. He is pouring dark coffee from a glass pot into a red V8 engine-shaped mug. As the liquid hits the bottom, thick, stylized plumes of white steam billow out of the "exhaust manifold" pipes on the side of the mug. The man looks at the camera with an expression of exaggerated surprise and delight.

**Actions:**
* The man tilts the glass carafe steadily.
* Digital steam effects rise rapidly and dissipate.
* The man’s eyebrows raise and his mouth opens in a "wow" expression.

**Dialogue:**
* None. (Text overlay: "Thank you for purchasing the V8 engine coffee cup...")

**Background Sound:**
High-energy, soulful rock/gospel vocals with a heavy beat and soaring high notes. 

---

**Scene 2 (00:04s - 00:09s):**
The V8 engine mug sits on a black leather weight bench inside a gym. Professional gym equipment and weights are visible in the blurred background. A silver pitcher pours dark coffee into the mug. Again, thick digital steam "exhausts" from the side pipes of the mug, creating a high-performance visual metaphor.

**Actions:**
* Liquid streams into the center of the mug.
* Thick white smoke pours out of the chrome-colored exhaust pipes on the mug's sides.
* The camera remains static in a low-angle close-up.

**Dialogue:**
* None.

**Background Sound:**
Continuation of the high-energy vocal track.

---

**Scene 3 (00:09s - 00:17s):**
A product showcase shot. The mug sits on a dark, rustic wooden surface. A hand reaches into the frame, grabs the handle, and lifts the mug, rotating it toward the camera. This shot highlights the intricate details: the chrome belt pulleys, the silver "bolt" accents, and the "V8" branding.

**Actions:**
* Hand enters from the right to grip the handle.
* The mug is tilted and spun slowly to reveal all sides.
* Subtle reflections of light dance across the metallic surfaces.

**Dialogue:**
* None.

**Background Sound:**
The music reaches a crescendo with powerful, sustained vocal notes.""",
        "size": "large",
        "duration": 15,
        "watermark": False,
        "private": True
    })
    
    print("正在创建视频任务...")
    conn.request("POST", "/v1/video/create", payload, HEADERS)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    result = json.loads(data)
    
    if "id" in result:
        print(f"任务创建成功，ID: {result['id']}")
        return result["id"]
    else:
        print(f"任务创建失败: {data}")
        return None

def query_video_status(video_id):
    """查询视频生成状态"""
    conn = http.client.HTTPSConnection(API_HOST)
    conn.request("GET", f"/v1/video/query?id={video_id}", '', {'Authorization': f'Bearer {AUTH_TOKEN}'})
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return json.loads(data)

def main():
    # 1. 创建视频
    video_id = create_video()
    if not video_id:
        return

    # 2. 轮询查询状态
    print("开始轮询视频状态...")
    while True:
        try:
            result = query_video_status(video_id)
            status = result.get("status")
            progress = result.get("progress", 0)
            
            print(f"当前状态: {status}, 进度: {progress}%")
            
            if status == "completed":
                video_url = result.get("video_url")
                print("\n🎉 视频生成完成！")
                print(f"视频链接: {video_url}")
                break
            elif status in ["failed", "error"]:
                print(f"\n❌ 视频生成失败: {result.get('detail', '未知错误')}")
                break
            
            # 等待 10 秒后再次查询
            time.sleep(10)
            
        except Exception as e:
            print(f"查询出错: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
