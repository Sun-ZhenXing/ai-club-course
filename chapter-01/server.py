import asyncio
import subprocess
import sys
import uuid

import aiofiles
from sanic import Request, Sanic, file, json
from sanic.request import File
from sanic.response import raw

app = Sanic(__name__)

app.static("/", "./static")


@app.route("/")
async def index(request: Request):
    return await file("./static/index.html")


@app.route("/api/super-resolution", methods=["POST"])
async def super_resolution(request: Request):
    asyncio.set_event_loop(asyncio.ProactorEventLoop())
    if not request.files:
        return json(
            {
                "error": "Image file is required",
            },
            status=400,
        )
    image: File = request.files["file"][0]
    extname = image.name.split(".")[-1].lower()
    if extname not in ["png", "jpg", "jpeg", "webp"]:
        return json(
            {
                "error": "Image file type is not supported",
            },
            status=400,
        )
    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        filename = f"{uuid.uuid4()}.{extname}"
        filepath = f"{tmpdir}/{filename}"
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(image.body)
        output_path = f"{tmpdir}/{uuid.uuid4()}.webp"

        # Windows SelectorEventLoop 不支持 create_subprocess_shell
        # 此处阻塞事件循环，部署在 Linux 无影响
        cmd = [
            f"realesrgan-ncnn-vulkan",
            "-i",
            filepath,
            "-o",
            output_path,
            "-n",
            "realesrgan-x4plus-anime",
        ]
        if sys.platform == "win32":
            sh = subprocess.Popen(
                cmd,
                cwd="./libs/",
                shell=True,
            )
            sh.communicate()
        else:
            sh = await asyncio.create_subprocess_shell(
                " ".join(cmd),
                cwd="./libs/",
            )
            await sh.wait()
        async with aiofiles.open(output_path, "rb") as f:
            body = await f.read()
        return raw(
            body,
            headers={
                "Content-Type": "image/webp",
            },
        )
