#!/usr/bin/env python3
"""听篁苑整体鸟瞰V3 - 1344x768 16:9 - 参照水榭露台V2调整"""
import requests, json, time, sys

API_KEY = "1f8f60420f204fa5b0e9ca5018791dbd"
BASE_URL = "https://www.runninghub.cn"
WORKFLOW_ID = "2049358468934541313"

prompt = """听篁苑整体俯瞰鸟瞰图，大远景俯视，
庞大的墨竹海中只有这一座孤零零的院落，四面竹海密不透风如天然城墙，无其他任何建筑，
中景院落主体布局清晰——正前方深色檀木院门（正南），院门正对一条青石板小径蜿蜒穿过竹海伸向远方，
院门内是开阔的冷灰色苍苔石板庭院，庭院中央一棵枯木逢春的老梅树（正中偏后位置），
老梅树后方是灰瓦屋脊的主建筑群，
院落左侧（西侧）深色原木水榭露台从庭院边缘延伸至外侧池塘水面上，露台由深色原木铺就纹理自然没有任何雕花，边缘离水面极近，露台上有一盏极简矮几，
池塘位于院落左外侧紧邻露台，池塘对岸墨竹低垂水面竹影倒映，池水清澈如镜可见池底莹润白石，几株冷霜白莲从水中自然生长而出莲叶舒展平铺水面白莲花苞与盛开的花朵高低错落散布池面，
近景院落最前方竹海边缘和青石板小径蜿蜒起点，
清晨，薄雾缭绕，初秋，
自然晨光天光均匀洒落，柔光漫射晨雾朦胧，冷色调清冷统一有微妙层次，
以竹青苍灰墨黑深檀月白冷霜白为主调，
四面浩瀚竹海中仅此一座院落，老梅树在庭院中央偏后，左外侧池塘对岸墨竹低垂水面水池清澈可见白石白莲从水中自然生长而出莲叶平铺花苞与盛开花朵错落散布，深色原木露台无雕花延伸水面极简矮几，
深色檀木院门灰瓦屋脊建筑群，
薄雾如纱院落孤悬竹海之中如云中孤岛，
俯视约45度角，广角无人机航拍视角，深景深整体清晰，
居中构图院落居中竹海浩瀚无边，
电影质感，超高清，8K，东方美学风格，横版16:9"""

payload = {
    "apiKey": API_KEY,
    "workflowId": WORKFLOW_ID,
    "nodeInfoList": [
        {"nodeId": "137", "fieldName": "text", "fieldValue": prompt},
        {"nodeId": "216", "fieldName": "width", "fieldValue": "1344"},
        {"nodeId": "216", "fieldName": "height", "fieldValue": "768"},
        {"nodeId": "216", "fieldName": "aspect_ratio", "fieldValue": "custom"},
        {"nodeId": "216", "fieldName": "swap_dimensions", "fieldValue": "Off"},
        {"nodeId": "216", "fieldName": "upscale_factor", "fieldValue": "1"},
        {"nodeId": "216", "fieldName": "batch_size", "fieldValue": "1"}
    ],
    "retainSeconds": 600
}

print("📤 创建任务 1344×768 V3(参照水榭露台)...")
r = requests.post(f"{BASE_URL}/task/openapi/create", json=payload, timeout=30)
result = r.json()
print(json.dumps(result, ensure_ascii=False, indent=2))

if result.get("code") != 0:
    sys.exit(1)

task_id = result["data"]["taskId"]
print(f"✅ 任务ID: {task_id}")

start = time.time()
while True:
    time.sleep(15)
    r2 = requests.post(f"{BASE_URL}/task/openapi/status",
        json={"apiKey": API_KEY, "taskId": task_id}, timeout=10)
    data = r2.json()
    status = data.get("data", "")
    if isinstance(status, dict):
        status = status.get("taskStatus", "")
    elapsed = int(time.time() - start)
    print(f"  ⏰ {elapsed}秒... 状态: {status}")
    if status == "SUCCESS":
        print("✅ 完成!")
        r3 = requests.post(f"{BASE_URL}/task/openapi/outputs",
            json={"apiKey": API_KEY, "taskId": task_id}, timeout=30)
        outputs = r3.json().get("data", [])
        for out in outputs:
            url = out.get("fileUrl", "")
            if url:
                vr = requests.get(url, timeout=120)
                fname = "/home/jason/aigc-douyin-project/output/t2i/tinghuang_aerial_v3.png"
                with open(fname, "wb") as f:
                    f.write(vr.content)
                print(f"  ✅ {fname} ({len(vr.content)/1024:.0f}KB)")
                print(f"\nMEDIA:{fname}")
        break
    elif status in ("FAILED", "ERROR"):
        print(f"❌ 失败: {json.dumps(data, ensure_ascii=False)[:300]}")
        break
