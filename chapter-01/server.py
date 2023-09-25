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


def process_command(cmd: list[str]):
    sh = subprocess.Popen(
        cmd,
        cwd="./libs/",
        shell=True,
    )
    return sh.communicate()


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
            await asyncio.to_thread(process_command, cmd)
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
